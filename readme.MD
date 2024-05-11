# MMDetection Support Tools for S3 and SAHI

This repository provides support tools to facilitate the use of MMDetection with datasets stored in AWS S3 buckets and integration with the SAHI library for performing slice aware object detection. The tools here are designed to streamline training and inferencing pipelines by allowing direct access to data stored in S3 buckets and leveraging the powerful functionality of SAHI for handling large and high-resolution images efficiently.

## Features

- Seamless integration with AWS S3 for data storage and retrieval.
- Support for SAHI, a library for slice-aware handling of high-resolution images in object detection tasks.
- Easy-to-use command-line interfaces for training and inference tasks.
- Flexible configuration options to customize the deep learning models, training parameters, and slicing strategies.

## How to Use

### Prerequisites

Before you begin, ensure you have the following installed:
- Python 3.x
- boto3
- MMDetection
- SAHI


### Sample Commands

Below are sample commands to run training sessions using datasets from S3 and with SAHI integration:

**Training without SAHI:**

```bash
python3 ./tools/train_with_s3_data.py \
  --s3-url s3://sample_path/2024-04-08_13-00-40 \
  --local-data-path ./data/2024-04-08_13-00-40 \
  --config ./configs/configuration.py
```

**Training with SAHI:**

```bash
python3 ./tools/train_with_s3_data_sahi.py \
  --s3-url s3://sample_path/2024-05-10_15-42-00 \
  --local-data-path ./data/2024-05-10_15-42-00 \
  --config ./configs/configuration.py
```

[Note] in the configuration, follow the file structure below.
```
data_root = "./data/2024-05-10_15-42-00" # same with your --local-data-path

crop_size = (720, 720) # It is required for automatic SAHI slicing

train_dataloader = dict(
    batch_size=batch_size,
    num_workers=batch_size,
    persistent_workers=True,
    sampler=dict(type="DefaultSampler", shuffle=True),
    batch_sampler=dict(type="AspectRatioBatchSampler"),
    dataset=dict(
        type=dataset_type,
        metainfo=meta_info,
        data_root=None,
        ann_file=data_root + "/train.json",
        data_prefix=dict(img=data_root + "/train_images"),
        filter_cfg=dict(filter_empty_gt=True, min_size=32),
        pipeline=train_pipeline,
        backend_args=None,
    ),
)
val_dataloader = dict(
    batch_size=1,
    num_workers=2,
    persistent_workers=True,
    drop_last=False,
    sampler=dict(type="DefaultSampler", shuffle=False),
    dataset=dict(
        type=dataset_type,
        metainfo=meta_info,
        data_root=None,
        ann_file=data_root + "/val_sliced.json",
        data_prefix=dict(img=data_root + "/val_images_sliced"),
        test_mode=True,
        pipeline=test_pipeline,
        backend_args=None,
    ),
)
val_evaluator = dict(
    type="CocoMetric",
    ann_file=data_root + "/val_sliced.json",
    metric="bbox",
    format_only=False,
    backend_args=None,
)
test_evaluator = val_evaluator
test_dataloader = val_dataloader
```

### Note

- Ensure that the `--s3-url` is correctly pointing to your dataset's location within the S3 bucket.
- The `--local-data-path` should point to where you want the dataset to be downloaded locally for the training session.
- Modify the `--config` flag with the path to your own training configuration file as required.
- To handle multiple COCO dataset, I maintain GUI-managetool [cvOps](https://github.com/ccomkhj/cvOps). Feel free to utilize. 