import argparse
import subprocess
import re
from mmengine.config import Config


def parse_args():
    parser = argparse.ArgumentParser(description="Train a model with S3 data")
    # Arguments for downloading S3 files
    parser.add_argument(
        "--s3-url", required=True, help="S3 URL of the folder to download"
    )
    parser.add_argument(
        "--local-data-path",
        default="./data",
        help="Local directory for downloaded S3 files",
    )
    # Arguments for training configuration
    parser.add_argument(
        "--config", required=True, help="Path to training configuration file"
    )
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
    """Updates the config file with the new cv_mode."""
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


def main():
    args = parse_args()

    # Extract cv_mode from the S3 URL
    cv_mode = extract_cv_mode(args.s3_url)

    # Update the config file with the new cv_mode
    update_config_file(args.config, cv_mode)
    (crop_size_w, crop_size_h) = read_crop_size(args.config)

    # Run the download script
    subprocess.call(
        ["python3", "tools/download_s3.py", args.s3_url, args.local_data_path]
    )

    subprocess.call(
        [
            "python3",
            "tools/sahi_slice_val.py",
            args.local_data_path,
            str(crop_size_w),
            str(crop_size_h),
        ]
    )

    # Build the command to run the training script, now with the updated configuration
    train_cmd = [
        "python3",
        "tools/train.py",
        "--config",
        args.config,
    ]

    if args.work_dir:
        train_cmd.extend(["--work-dir", args.work_dir])

    # Execute the train command
    subprocess.run(train_cmd)


if __name__ == "__main__":
    main()
