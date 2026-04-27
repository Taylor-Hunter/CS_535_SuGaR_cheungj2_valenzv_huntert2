#!/usr/bin/env python3
"""
CS 535 Project - Download script for Mip-NeRF 360 datasets

We made this to automatically download the datasets we need for our SuGaR experiments.

Dataset 1: Garden scene from original paper (big file - 11GB!)
Dataset 2: Tree scene we're using for our new experiments (4.2GB)

Run with: python download_mipnerf360_datasets.py --part2-only
Or just: python download_mipnerf360_datasets.py

Authors: Jaden Cheung, Taylor Hunter, Vito Valenzano
"""

import os
import sys
import urllib.request
import zipfile
import argparse
from pathlib import Path

# Simple progress display for downloads
class DownloadProgress:
    def __init__(self, filename):
        self.filename = filename
        self.last_percent = -1
    
    def show_progress(self, block_num, block_size, total_size):
        if total_size <= 0:
            return
            
        downloaded = block_num * block_size
        percent = min(100, (downloaded * 100) // total_size)
        
        # Only print every 10% to not spam the console too much
        if percent != self.last_percent and percent % 10 == 0:
            mb_done = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            print(f"{self.filename}: {percent}% done ({mb_done:.1f}/{mb_total:.1f} MB)")
            self.last_percent = percent


def download_file(url, save_path, description):
    """Download a file with progress tracking"""
    try:
        print(f"Downloading {description}...")
        print(f"From: {url}")
        print(f"To: {save_path}")
        
        # Make sure the folder exists first
        save_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Actually download it
        progress = DownloadProgress(save_path.name)
        urllib.request.urlretrieve(url, save_path, reporthook=progress.show_progress)
        
        print(f"Success! Downloaded: {save_path.name}")
        return True
        
    except Exception as e:
        print(f"Failed to download: {e}")
        print("Maybe try again? Sometimes the connection is flaky...")
        return False


def extract_zip_file(zip_path, extract_to, description):
    """Extract a ZIP file"""
    try:
        print(f"Extracting {description}...")
        extract_to.mkdir(parents=True, exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            zip_file.extractall(extract_to)
        
        print(f"Extracted: {description}")
        return True
        
    except Exception as e:
        print(f"Extraction failed: {e}")
        return False


def main_download(base_dir, download_part1=True, download_part2=True, keep_zips=False):
    """Main function to download the datasets"""
    
    # URLs we found for the Mip-NeRF 360 datasets - took forever to find these!
    dataset1_url = 'http://storage.googleapis.com/gresearch/refraw360/360_v2.zip'
    dataset2_url = 'https://storage.googleapis.com/gresearch/refraw360/360_extra_scenes.zip'
    
    # TODO: Maybe add checksum validation later if we have time
    # TODO: Could add resume functionality for failed downloads
    
    # Setup directories  
    datasets_dir = base_dir / "datasets" / "mipnerf360"
    datasets_dir.mkdir(parents=True, exist_ok=True)
    
    print("=" * 50)
    print("CS 535 - Downloading Mip-NeRF 360 Datasets")
    print("=" * 50)
    print(f"Save location: {datasets_dir}")
    
    all_good = True
    
    # Download Dataset 1 (Garden scene)
    if download_part1:
        zip_file = datasets_dir / "dataset1_garden.zip"
        extract_folder = datasets_dir / "part1_garden"
        
        if not extract_folder.exists():
            # Download if we don't have it yet
            if not zip_file.exists():
                print("Starting Dataset 1 download...")
                if not download_file(dataset1_url, zip_file, "Dataset 1 - Garden (11GB)"):
                    all_good = False
            
            # Extract if we got the file
            if zip_file.exists():
                if not extract_zip_file(zip_file, extract_folder, "Dataset 1 - Garden"):
                    all_good = False
                elif not keep_zips:
                    zip_file.unlink()  # Clean up the zip
                    print(f"Cleaned up {zip_file.name}")
        else:
            print(f"Dataset 1 already there: {extract_folder}")
    
    # Download Dataset 2 (Tree scene) - this is our main one  
    if download_part2:
        zip_file = datasets_dir / "dataset2_tree.zip"
        extract_folder = datasets_dir / "part2_tree"
        
        if not extract_folder.exists():
            # Download if we don't have it yet
            if not zip_file.exists():
                print("Starting Dataset 2 download...")
                if not download_file(dataset2_url, zip_file, "Dataset 2 - Tree (4.2GB)"):
                    all_good = False
            
            # Extract if we got the file
            if zip_file.exists():
                if not extract_zip_file(zip_file, extract_folder, "Dataset 2 - Tree"):
                    all_good = False
                elif not keep_zips:
                    zip_file.unlink()  # Clean up the zip
                    print(f"Cleaned up {zip_file.name}")
        else:
            print(f"Dataset 2 already there: {extract_folder}")
    
    return all_good


if __name__ == "__main__":
    # Simple command line parsing
    parser = argparse.ArgumentParser(description="Download datasets for our CS 535 project")
    
    parser.add_argument('--part1-only', action='store_true', help='Only download garden dataset')
    parser.add_argument('--part2-only', action='store_true', help='Only download tree dataset') 
    parser.add_argument('--keep-zips', action='store_true', help='Keep zip files after extracting')
    
    args = parser.parse_args()
    
    # Figure out what to download
    if args.part1_only and args.part2_only:
        print("Error: Can't use both --part1-only and --part2-only!")
        sys.exit(1)
    
    download_part1 = not args.part2_only
    download_part2 = not args.part1_only
    
    current_dir = Path('.').resolve()
    
    # Warn about file sizes
    if download_part1 and download_part2:
        print("Warning: About to download ~15GB total. Make sure you have space!")
    elif download_part1:
        print("Warning: About to download ~11GB (garden dataset)")
    elif download_part2:
        print("Warning: About to download ~4.2GB (tree dataset)")
    
    # Ask user to confirm
    answer = input("Continue with download? (y/n): ")
    if answer.lower() != 'y':
        print("Cancelled.")
        sys.exit(0)
    
    # Do the actual downloading
    success = main_download(
        base_dir=current_dir,
        download_part1=download_part1, 
        download_part2=download_part2,
        keep_zips=args.keep_zips
    )
    
    # Report results
    if success:
        print("\n" + "=" * 50)
        print("All done! Datasets downloaded successfully")
        print(f"Location: {current_dir / 'datasets' / 'mipnerf360'}")
        print("=" * 50)
        print("\nNext: Run SuGaR training with:")
        print("python train_full_pipeline.py -s ./datasets/mipnerf360/part2_tree")
    else:
        print("\n" + "=" * 50) 
        print("Something went wrong. Check the errors above.")
        print("=" * 50)
        sys.exit(1)