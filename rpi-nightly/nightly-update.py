import requests
import os
import time
import subprocess

# --- CONFIGURATION (UPDATE THESE) ---
# 1. GitHub Repository Information
GITHUB_OWNER = "phamngocvinh"
GITHUB_REPO_NAME = "rpi-trader"
ASSET_FILE_NAME = "released_package.7z" # The name of your .7z file attached to the GitHub Release

# GitHub API URL to fetch the latest release information
GITHUB_LATEST_RELEASE_API = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO_NAME}/releases/latest"

# 2. Full path to the target directory for the EXTRACTED files.
LOCAL_TARGET_DIR = "/test/"

# 3. Local name for the archive file (.7z).
ARCHIVE_FILE_NAME = "released_package.7z"

# 4. Filename used to store the current running version tag (e.g., v1.0.0)
VERSION_FILE_NAME = ".current_version" 
VERSION_FILE_PATH = os.path.join(LOCAL_TARGET_DIR, VERSION_FILE_NAME)

# --- VERSION FUNCTIONALITY (RELEASE CHECK) ---

def get_local_version():
    """Reads the locally stored version tag."""
    if os.path.exists(VERSION_FILE_PATH):
        with open(VERSION_FILE_PATH, 'r') as f:
            return f.read().strip()
    return "v0.0.0" # Default version if none exists

def save_local_version(version_tag):
    """Saves the new version tag upon successful update."""
    if not os.path.exists(LOCAL_TARGET_DIR):
        os.makedirs(LOCAL_TARGET_DIR)
    with open(VERSION_FILE_PATH, 'w') as f:
        f.write(version_tag)

def check_for_new_release():
    """
    Fetches the latest release from GitHub API and checks if it's newer than the local version.
    Returns (remote_version, download_url) or (None, None) if no update is needed.
    """
    local_version = get_local_version()
    print(f"Local stored version: {local_version}")

    try:
        # Request the latest release JSON from GitHub API
        response = requests.get(GITHUB_LATEST_RELEASE_API, timeout=10)
        response.raise_for_status() 
        release_data = response.json()
        
        remote_version = release_data.get('tag_name')
        
        # 1. Check if remote version is the same as local version
        if remote_version == local_version:
            print(f"Latest remote version ({remote_version}) is the same as local version. Skipping download.")
            return None, None
        
        # 2. Check for the specific asset file (archive_file.7z)
        download_url = None
        for asset in release_data.get('assets', []):
            if asset.get('name') == ASSET_FILE_NAME:
                # The browser_download_url is the direct link to the file
                download_url = asset.get('browser_download_url')
                break
        
        if download_url:
            print(f"New version ({remote_version}) found. Download URL retrieved.")
            return remote_version, download_url
        else:
            print(f"New version ({remote_version}) found, but asset '{ASSET_FILE_NAME}' not attached to the release.")
            return None, None

    except requests.exceptions.RequestException as e:
        print(f"API CHECK ERROR: Could not connect to GitHub Release API. Skipping update. Details: {e}")
        return None, None

# --- MAIN UPDATE LOGIC ---

def update_and_extract_archive():
    """Downloads the .7z file from GitHub, extracts it, and cleans up (WITH VERSION CHECK)."""
    
    local_archive_path = os.path.join(LOCAL_TARGET_DIR, ARCHIVE_FILE_NAME)
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    
    print(f"[{timestamp}] Starting version check and update process.")

    # 1. Ensure the target directory exists
    if not os.path.exists(LOCAL_TARGET_DIR):
        print(f"Creating target directory: {LOCAL_TARGET_DIR}")
        try:
            os.makedirs(LOCAL_TARGET_DIR)
        except Exception as e:
            print(f"ERROR: Could not create target directory. Details: {e}")
            return
    
    # --- VERSION CHECK ---
    
    remote_version, download_url = check_for_new_release()
    
    if not download_url:
        print(">>> FILE HAS NOT CHANGED or Download URL not found. Skipping download and extraction.")
        return # Exit script if no new version or asset missing

    # --- PROCEED WITH DOWNLOAD AND EXTRACTION ---

    # 4. Download the .7z file
    try:
        print(f">>> NEW VERSION DETECTED ({remote_version}). Downloading file from Release...")
        # Use the specific download_url retrieved from the API
        response = requests.get(download_url, stream=True, timeout=30) 
        response.raise_for_status() 
        
        with open(local_archive_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Download successful! Saved at: {local_archive_path}")

    except requests.exceptions.RequestException as e:
        print(f"DOWNLOAD ERROR: Could not download file. Details: {e}")
        return
        
    # 5. Extract the .7z file (replacing old scripts with new ones)
    print(f"Starting extraction...")
    try:
        # Extract over the target directory
        subprocess.run(
            ['7z', 'x', local_archive_path, f'-o{LOCAL_TARGET_DIR}', '-y'],
            check=True, 
            capture_output=True,
            text=True
        )
        print("Extraction and file replacement successful!")

    except subprocess.CalledProcessError as e:
        print(f"EXTRACTION ERROR: 7z failed.")
        return
    
    # 6. Cleanup: Delete the downloaded .7z file and SAVE the new VERSION
    try:
        os.remove(local_archive_path)
        if remote_version:
            save_local_version(remote_version)
            print(f"New version {remote_version} saved and temporary archive file cleaned up.")
        else:
            print("Temporary archive file cleaned up (Could not save version tag).")
            
    except Exception as e:
        print(f"CLEANUP WARNING: An error occurred. Details: {e}")


if __name__ == "__main__":
    update_and_extract_archive()