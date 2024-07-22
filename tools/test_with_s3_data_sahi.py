import os
import subprocess
import glob
from utils import (
    parse_args,
    extract_cv_mode,
    read_crop_size,
    create_local_data_path,
    update_config_file,
    download_and_slice_data,
)


def main():
    args = parse_args()
    # Extract cv_mode from the S3 URL
    cv_mode = extract_cv_mode(args.s3_url)
    # Update the config file with the new cv_mode
    update_config_file(args.config, cv_mode)
    (crop_size_w, crop_size_h) = read_crop_size(args.config)
    local_data_path = create_local_data_path(args.s3_url, crop_size_w)
    env_vars = os.environ.copy()
    env_vars["DATASET_ROOT"] = local_data_path

    download_and_slice_data(args.s3_url, local_data_path, crop_size_w, crop_size_h)

    base_file = os.path.basename(args.config).split(".")[0]
    work_dir = os.path.join("work_dirs", base_file)
    test_dir = os.path.join("test_dirs", base_file)
    best_model_ckpt = glob.glob(os.path.join(work_dir, "best_*"))[-1]

    # Build the command to run the test script, now with the updated configuration
    test_cmd = [
        "python3",
        "tools/test.py",
        args.config,
        best_model_ckpt,
        "--show-dir",
        "test_imgs",
        "--work-dir",
        test_dir,
    ]

    # Execute the test command
    subprocess.run(test_cmd, env=env_vars)


if __name__ == "__main__":
    main()
