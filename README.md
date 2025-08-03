<h1 align="center">File Downloader (CLI)</h1>

A swift and efficient file downloader for the command line, built in Python.

## Features

- **Multi-threaded Downloading:** Downloads files in multiple segments simultaneously for increased speed.
- **Download Resumption:** Automatically resumes interrupted downloads.
- **SHA-256 Hash Calculation:** Calculates the SHA-256 hash of the downloaded file for manual verification.
- **Command-Line Interface:** Lightweight and easy to use directly from your terminal.
- **Default Download Directory:** Saves files to your operating system's Downloads folder (Windows, macOS, Linux) by default.

## Installation

**Prerequisites:** Ensure you have Python 3.6+ installed.

`pipx` installs the application and its dependencies into an isolated environment but makes the command globally available.

1.  **Install `pipx` (if you haven't already):**
    ```bash
    # For macOS
    brew install pipx
    pipx ensurepath

    # For other systems
    python3 -m pip install --user pipx
    python3 -m pipx ensurepath
    ```
    *(You may need to restart your terminal after this step.)*
    ```bash
    pipx install git+https://github.com/lordvonko/download-app.git
    ```
    The `download-app` command will now be available globally.

---
## Usage

Once installed, you can use the application from your terminal.

**Syntax:**
```bash
download-app [OPTIONS] <URL> [OUTPUT_DIRECTORY]
```

-   `<URL>`: The URL of the file you want to download.
-   `[OUTPUT_DIRECTORY]`: (Optional) The directory where the file will be saved. If not provided, it defaults to your system's "Downloads" folder.

### Options
- `-t, --threads <NUMBER>`: Sets the number of threads for multi-threaded downloads (default: 8).

### Examples

-   **Download to the default Downloads folder:**
    ```bash
    download-app "https://geo.mirror.pkgbuild.com/iso/latest/archlinux-x86_64.iso"
    ```

-   **Download to a specific directory with 16 threads:**
    ```bash
    download-app --threads 16 "https://example.com/somefile.zip" "/home/your_user/Documents"
    ```

