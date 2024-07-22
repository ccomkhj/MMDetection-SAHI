import argparse
import subprocess
import re
from utils import (
    parse_args,
    update_config_file,
    extract_cv_mode,
    read_crop_size,
    create_local_data_path,
)


def main():
    args = parse_args()

    # Extract cv_mode from the S3 URL
    cv_mode = extract_cv_mode(args.s3_url)
    (crop_size_w, crop_size_h) = read_crop_size(args.config)
    local_data_path = create_local_data_path(args.s3_url, crop_size_w)

    # Update the config file with the new cv_mode
    update_config_file(args.config, cv_mode)

    # Run the download script
    subprocess.call(["python3", "tools/download_s3.py", args.s3_url, local_data_path])

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
