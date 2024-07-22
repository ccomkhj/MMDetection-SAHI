from utils import (
    parse_args,
    extract_cv_mode,
    read_crop_size,
    create_local_data_path,
    update_config_file,
    download_and_slice_data,
)
import subprocess
import os


def main():
    args = parse_args()

    # Extract cv_mode from the S3 URL
    env_vars = os.environ.copy()
    s3_urls = args.s3_url

    for idx, s3_url in enumerate(s3_urls):

        cv_mode = extract_cv_mode(s3_url)
        # Update the config file with the new cv_mode
        update_config_file(args.config, cv_mode)
        (crop_size_w, crop_size_h) = read_crop_size(args.config)
        local_data_path = create_local_data_path(s3_url, crop_size_w)
        print(f"DATASET_ROOT{idx+1} is added into env_vars")

        env_vars[f"DATASET_ROOT{idx+1}"] = local_data_path

        download_and_slice_data(s3_url, local_data_path, crop_size_w, crop_size_h)

        # Build the command to run the training script, now with the updated configuration
        train_cmd = [
            "python3",
            "tools/train.py",
            "--config",
            args.config,
        ]
    # Execute the train command
    subprocess.run(train_cmd, env=env_vars)


if __name__ == "__main__":
    main()
