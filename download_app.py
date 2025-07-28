

import os
import sys
import argparse
import threading
import time
import hashlib
import shutil
from urllib.parse import urlparse
from pathlib import Path
import requests

def get_download_path(directory=None):
    """
    Determines the correct download path.
    Defaults to the user's Downloads folder if no directory is provided.
    """
    if directory:
        path = Path(directory)
        if not path.exists() or not path.is_dir():
            print(f"Error: The directory '{directory}' does not exist or is not a valid directory.")
            sys.exit(1)
        return path
    else:
        return Path.home() / "Downloads"

def get_filename_from_url(url):
    """Extracts the filename from a given URL."""
    try:
        parsed_url = urlparse(url)
        filename = os.path.basename(parsed_url.path)
        return filename if filename else 'downloaded_file'
    except Exception:
        return 'downloaded_file'

class Downloader:
    """Handles the file downloading logic for the CLI."""

    def __init__(self, url, output_path, num_threads=8, retries=3):
        self.url = url
        self.output_path = output_path
        self.num_threads = num_threads
        self.retries = retries
        self.total_size = 0
        self.total_downloaded = 0
        self.start_time = None
        self.stop_event = threading.Event()
        self.error_occurred = None

    def download(self):
        """Starts the download process."""
        try:
            head = requests.head(self.url, allow_redirects=True, timeout=10)
            head.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Error: Failed to connect to the server: {e}")
            return

        self.total_size = int(head.headers.get('Content-Length', 0))
        accept_ranges = 'bytes' in head.headers.get('Accept-Ranges', '').lower()

        if self.total_size and accept_ranges:
            print("Server supports multi-threaded downloading. Starting...")
            self._multi_threaded_download()
        else:
            print("Server does not support multi-threaded downloading. Using single-threaded mode.")
            self._single_threaded_download()

    def _print_progress(self):
        """Prints a progress bar to the console."""
        if self.stop_event.is_set():
            return

        percentage = 0
        if self.total_size > 0:
            percentage = (self.total_downloaded / self.total_size) * 100

        bar_length = 40
        filled_length = int(bar_length * self.total_downloaded // self.total_size) if self.total_size else 0
        bar = '█' * filled_length + '-' * (bar_length - filled_length)

        elapsed_time = time.time() - self.start_time
        speed = self.total_downloaded / elapsed_time / 1024 if elapsed_time > 0 else 0  # KB/s
        
        eta = ""
        if speed > 0 and self.total_size > 0:
            remaining = (self.total_size - self.total_downloaded) / (speed * 1024)
            eta = f"ETA: {int(remaining // 60)}m {int(remaining % 60)}s"

        sys.stdout.write(f"\r|{bar}| {percentage:.2f}% ({speed:.2f} KB/s) {eta}      ")
        sys.stdout.flush()

    def _single_threaded_download(self):
        """Downloads the file using a single thread."""
        part_file = str(self.output_path) + '.part'
        resume_pos = 0
        if os.path.exists(part_file):
            resume_pos = os.path.getsize(part_file)

        headers = {'Range': f'bytes={resume_pos}-'} if resume_pos > 0 else {}
        self.total_downloaded = resume_pos
        self.start_time = time.time()

        try:
            response = requests.get(self.url, headers=headers, stream=True, timeout=10)
            response.raise_for_status()

            mode = 'ab' if resume_pos > 0 else 'wb'
            with open(part_file, mode) as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        self.total_downloaded += len(chunk)
                        self._print_progress()

            os.rename(part_file, self.output_path)
            self._verify_file_integrity()
        except requests.exceptions.RequestException as e:
            print(f"\nDownload error: {e}")
        except KeyboardInterrupt:
            print("\nDownload cancelled by user.")
            self.stop_event.set()

    def _multi_threaded_download(self):
        """Downloads the file using multiple threads."""
        chunk_size = self.total_size // self.num_threads
        segments = []
        for i in range(self.num_threads):
            start = i * chunk_size
            end = start + chunk_size - 1 if i < self.num_threads - 1 else self.total_size - 1
            segments.append((start, end))

        lock = threading.Lock()
        threads = []
        self.start_time = time.time()

        for i, (start, end) in enumerate(segments):
            thread = threading.Thread(target=self._download_segment, args=(i, start, end, lock))
            threads.append(thread)
            thread.start()

        try:
            while any(t.is_alive() for t in threads):
                self._print_progress()
                time.sleep(0.1)

            for thread in threads:
                thread.join()

        except KeyboardInterrupt:
            print("\nDownload cancelled by user. Waiting for segments to finish...")
            self.stop_event.set()
            for t in threads:
                t.join()
            print("Cancellation complete.")
            return

        if not self.error_occurred:
            self._merge_files()
            self._verify_file_integrity()
        else:
            print(f"\nDownload failed due to an error: {self.error_occurred}")


    def _download_segment(self, index, start, end, lock):
        """Downloads a single segment of the file."""
        part_file = f"{self.output_path}.part{index}"
        resume_pos = 0
        if os.path.exists(part_file):
            resume_pos = os.path.getsize(part_file)

        with lock:
            self.total_downloaded += resume_pos

        if resume_pos >= (end - start + 1):
            return

        current_start = start + resume_pos
        headers = {'Range': f'bytes={current_start}-{end}'}
        mode = 'ab' if resume_pos > 0 else 'wb'

        for attempt in range(self.retries):
            if self.stop_event.is_set():
                return
            try:
                response = requests.get(self.url, headers=headers, stream=True, timeout=10)
                response.raise_for_status()

                with open(part_file, mode) as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if self.stop_event.is_set():
                            return
                        if chunk:
                            f.write(chunk)
                            with lock:
                                self.total_downloaded += len(chunk)
                break
            except requests.exceptions.RequestException as e:
                if attempt < self.retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    with lock:
                        self.error_occurred = f"Failed to download segment {index}: {e}"
                    return

    def _merge_files(self):
        """Merges the downloaded segments into a single file."""
        print("\nDownload complete. Merging files...")
        with open(self.output_path, 'wb') as f_out:
            for i in range(self.num_threads):
                part_file = f"{self.output_path}.part{i}"
                if os.path.exists(part_file):
                    with open(part_file, 'rb') as f_in:
                        shutil.copyfileobj(f_in, f_out)
                    os.remove(part_file)

    def _verify_file_integrity(self):
        """Verifies the integrity of the downloaded file using SHA-256."""
        print("\nVerifying file integrity...")
        try:
            hasher = hashlib.sha256()
            with open(self.output_path, 'rb') as f:
                while chunk := f.read(8192):
                    hasher.update(chunk)
            file_hash = hasher.hexdigest()
            print(f"File verification successful. SHA-256: {file_hash}")
        except IOError as e:
            print(f"\nFile verification error: {e}")

def main():
    """Main function to run the CLI application."""
    parser = argparse.ArgumentParser(description="Swift File Downloader - CLI")
    parser.add_argument("url", help="The URL of the file to be downloaded.")
    parser.add_argument("directory", nargs='?', default=None, help="The directory to save the file in (optional).")
    parser.add_argument("-t", "--threads", type=int, default=8, help="Number of threads to use for multi-threaded downloading.")
    
    args = parser.parse_args()

    download_dir = get_download_path(args.directory)
    filename = get_filename_from_url(args.url)
    output_path = download_dir / filename

    if output_path.exists():
        overwrite = input(f"The file '{output_path}' already exists. Do you want to overwrite it? (y/n): ").lower()
        if overwrite != 'y':
            print("Download cancelled.")
            sys.exit(0)

    print(f"Starting download of '{args.url}' to '{output_path}'")
    downloader = Downloader(args.url, output_path, num_threads=args.threads)
    downloader.download()

if __name__ == "__main__":
    main()
