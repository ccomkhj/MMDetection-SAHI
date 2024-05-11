import argparse
import os
from sahi.slicing import slice_coco
from sahi.utils.file import save_json


def sahi_slice(
    image_dir,
    coco_annotation_file_path,
    output_coco_annotation_file_path,
    output_dir_images,
    crop_size_height,
    crop_size_width,
    overlap_height_ratio=0.1,
    overlap_width_ratio=0.1,
):
    if not os.path.exists(output_dir_images):
        os.makedirs(output_dir_images)

    coco_dict, _ = slice_coco(
        coco_annotation_file_path=coco_annotation_file_path,
        output_coco_annotation_file_name="",
        image_dir=image_dir,
        output_dir=output_dir_images,
        slice_height=crop_size_height,
        slice_width=crop_size_width,
        overlap_height_ratio=overlap_height_ratio,
        overlap_width_ratio=overlap_width_ratio,
        verbose=True,
        min_area_ratio=0.1,
    )

    save_json(coco_dict, output_coco_annotation_file_path)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Slice images and annotations according to the specified configurations."
    )
    parser.add_argument("local_path", help="Local path where the datasets are stored")
    parser.add_argument("crop_size_w", type=int, help="Crop size width for slicing.")
    parser.add_argument("crop_size_h", type=int, help="Crop size height for slicing.")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    crop_size_w = args.crop_size_w
    crop_size_h = args.crop_size_h
    local_path = args.local_path

    image_dir = os.path.join(local_path, "val_images")
    output_dir_images = os.path.join(local_path, "val_images_sliced")
    coco_dir = local_path  # Since only the file name is changed, no need to create a separate directory
    coco_annotation_file_path = os.path.join(coco_dir, "val.json")
    output_coco_annotation_file_path = os.path.join(coco_dir, "val_sliced.json")

    sahi_slice(
        image_dir=image_dir,
        coco_annotation_file_path=coco_annotation_file_path,
        output_coco_annotation_file_path=output_coco_annotation_file_path,
        output_dir_images=output_dir_images,
        crop_size_height=crop_size_h,
        crop_size_width=crop_size_w,
    )
