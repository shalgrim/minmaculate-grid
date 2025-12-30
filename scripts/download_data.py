#!/usr/bin/env python3
"""
Download and extract the Sean Lahman Baseball Database.

Usage:
    python scripts/download_data.py
"""

import sys
import zipfile
from pathlib import Path
from urllib.request import urlretrieve

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Database download URL
# Note: The exact URL may change; check https://sabr.org/lahman-database/ for the latest
LAHMAN_URL = (
    "https://github.com/chadwickbureau/baseballdatabank/archive/refs/heads/master.zip"
)

# Alternate direct download (if above doesn't work):
# LAHMAN_URL = "http://seanlahman.com/files/database/baseballdatabank-master.zip"

DATA_DIR = Path(__file__).parent.parent / "data"
REQUIRED_FILES = ["Appearances.csv", "Teams.csv", "People.csv"]


def download_progress(block_count, block_size, total_size):
    """Progress callback for urlretrieve."""
    downloaded = block_count * block_size
    percent = (downloaded / total_size) * 100 if total_size > 0 else 0
    print(
        f"\rDownloading: {percent:.1f}% ({downloaded:,}/{total_size:,} bytes)", end=""
    )


def download_lahman_database():
    """Download and extract the Lahman Baseball Database."""
    print("Minmaculate Grid - Lahman Database Downloader")
    print("=" * 50)
    print()

    # Create data directory if it doesn't exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Check if files already exist
    existing_files = [f for f in REQUIRED_FILES if (DATA_DIR / f).exists()]
    if len(existing_files) == len(REQUIRED_FILES):
        print(f"✅ All required files already exist in {DATA_DIR}")
        for f in REQUIRED_FILES:
            file_path = DATA_DIR / f
            size = file_path.stat().st_size / (1024 * 1024)  # MB
            print(f"   - {f} ({size:.1f} MB)")
        print()
        response = input("Re-download? (y/N): ").strip().lower()
        if response != "y":
            print("Skipping download.")
            return True

    # Download ZIP file
    zip_path = DATA_DIR / "lahman.zip"
    print(f"Downloading from: {LAHMAN_URL}")
    print(f"Saving to: {zip_path}")
    print()

    try:
        urlretrieve(LAHMAN_URL, zip_path, reporthook=download_progress)
        print("\n✅ Download complete!")
    except Exception as e:
        print(f"\n❌ Error downloading database: {e}")
        print()
        print("Alternative: Download manually from https://sabr.org/lahman-database/")
        print(f"and extract the following files to {DATA_DIR}:")
        for f in REQUIRED_FILES:
            print(f"  - {f}")
        return False

    # Extract ZIP file
    print()
    print("Extracting ZIP file...")

    try:
        with zipfile.ZipFile(zip_path, "r") as zip_ref:
            # The GitHub archive has files in baseballdatabank-master/core/
            # We need to extract just the CSV files we need
            all_files = zip_ref.namelist()

            for required_file in REQUIRED_FILES:
                # Find the file in the archive (it might be in a subdirectory)
                matching_files = [f for f in all_files if f.endswith(required_file)]

                if not matching_files:
                    print(f"⚠️  Warning: {required_file} not found in archive")
                    continue

                # Extract the first match
                archive_path = matching_files[0]
                print(f"Extracting: {required_file}")

                # Read from archive and write to data directory
                with zip_ref.open(archive_path) as source:
                    with open(DATA_DIR / required_file, "wb") as target:
                        target.write(source.read())

        print("✅ Extraction complete!")

        # Clean up ZIP file
        zip_path.unlink()
        print(f"🗑️  Removed {zip_path.name}")

    except Exception as e:
        print(f"❌ Error extracting database: {e}")
        return False

    # Verify all files exist
    print()
    print("Verifying files...")
    missing_files = [f for f in REQUIRED_FILES if not (DATA_DIR / f).exists()]

    if missing_files:
        print("❌ Missing required files:")
        for f in missing_files:
            print(f"   - {f}")
        return False

    print("✅ All required files present:")
    for f in REQUIRED_FILES:
        file_path = DATA_DIR / f
        size = file_path.stat().st_size / (1024 * 1024)  # MB
        print(f"   - {f} ({size:.1f} MB)")

    print()
    print("=" * 50)
    print("✅ Database download complete!")
    print()
    print("Credits: Sean Lahman Baseball Database")
    print("License: CC BY-SA 3.0")
    print("Source: https://sabr.org/lahman-database/")
    return True


if __name__ == "__main__":
    success = download_lahman_database()
    sys.exit(0 if success else 1)
