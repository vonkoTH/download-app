# File Downloader (CLI)

A swift and efficient file downloader for the command line, built in Python.

## Features

- **Multi-threaded Downloading:** Downloads files in multiple segments simultaneously for increased speed.
- **Download Resumption:** Automatically resumes interrupted downloads.
- **SHA-256 Hash Calculation:** Calculates the SHA-256 hash of the downloaded file for manual verification.
- **Command-Line Interface:** Lightweight and easy to use directly from your terminal.
- **Default Download Directory:** Saves files to your operating system's Downloads folder (Windows, macOS, Linux) by default.

## Installation

**Prerequisites:** Ensure you have Python 3.6+ installed.

There are two recommended ways to install this application.

### Option 1: Virtual Environment (Recommended for Development)

This method is best if you are working on the code. It keeps all dependencies isolated from your main system.

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/lordvonko/download-app.git
    cd download-app
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install in editable mode:**
    The `-e` flag allows you to make changes to the code without reinstalling.
    ```bash
    pip install -e .
    ```
    The `download-app` command will be available as long as the virtual environment is active.

### Option 2: Using `pipx` (Recommended for Global Use)

This is the best method if you want to use `download-app` like any other command-line tool, from anywhere on your system, without activating a virtual environment.

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

2.  **Install the application with `pipx`:**
    Navigate to the project directory (`/path/to/download-app`) and run:
    ```bash
    pipx install .
    ```
    The `download-app` command will now be available globally.

---

**A Note on Global Installation:** While you can technically run `pip install .` outside of a virtual environment, it is **strongly discouraged**. This can lead to dependency conflicts and may interfere with system-level Python scripts.

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

