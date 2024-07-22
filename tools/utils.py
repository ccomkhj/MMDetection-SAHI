import argparse
import os
import re
import subprocess
from mmengine.config import Config


def create_local_data_path(s3_url, crop_size):
    # Extract the relevant parts from the s3_url
    parts = s3_url.split("/")
    relevant_parts = parts[3:]
    # Join the extracted parts to form the local path without the crop size
    base_local_data_path = os.path.join("./data", *relevant_parts).rstrip("/")
    # Add the crop_size to the local path
    local_data_path = f"{base_local_data_path}/{crop_size}"
    return local_data_path


def parse_args():
    parser = argparse.ArgumentParser(description="Process a model with S3 data")
    # Arguments for downloading S3 files
    parser.add_argument(
        "--s3-url", required=True, type=str, nargs="+", help="S3 URL of the folder to download"
    )
    # Arguments for configuration
    parser.add_argument("--config", required=True, help="Path to configuration file")
    parser.add_argument("--work-dir", help="Path to save logs and models")
    return parser.parse_args()


def extract_cv_mode(s3_url):
    """Extracts cv_mode from the S3 URL."""
    # Assuming the format is always as shown, adjust regex as needed
    match = re.search(r"s3://[^/]+/([^/]+)/([^/]+)/", s3_url)
    if match:
        return match.group(1) + "-" + match.group(2)
    return "default-mode"


def read_crop_size(config_path):
    """Returns the crop size from the config file."""
    return Config.fromfile(config_path).get("crop_size")


def update_config_file(config_path, cv_mode):
    """Updates the config file with the new cv_mode."""
    with open(config_path, "r") as file:
        config_str = file.read()
    # Look for the pattern to add/update cv_mode
    pattern = re.compile(r"cv_mode = ['\"][^'\"]*['\"]")
    if pattern.search(config_str):
        # cv_mode already exists, update it
        config_str = pattern.sub(f"cv_mode = '{cv_mode}'", config_str)
    else:
        # Insert cv_mode at the beginning of the file
        config_str = f"cv_mode = '{cv_mode}'\n" + config_str
    # Write the updated configuration back to the file
    with open(config_path, "w") as file:
        file.write(config_str)


def download_and_slice_data(s3_url, local_data_path, crop_size_w, crop_size_h):
    if os.path.exists(local_data_path):
        print("Download dataset already exists in local", local_data_path)
    else:
        print("Download dataset from S3 under", s3_url)
        # Run the download script
        subprocess.call(["python3", "tools/download_s3.py", s3_url, local_data_path])

    if os.path.exists(os.path.join(local_data_path, "val_images_sliced")):
        print("Sliced dataset already exists in local", local_data_path)
    else:
        subprocess.call(
            [
                "python3",
                "tools/sahi_slice_val.py",
                local_data_path,
                str(crop_size_w),
                str(crop_size_h),
            ]
        )
