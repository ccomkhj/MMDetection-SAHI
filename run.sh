#!/bin/bash

S3_VAL_URL="s3://bucket/path_for_val/"
CONFIG_FILE="configs/config_file.py" # DO NOT start with ./
# Example additional URLs, replace these with your actual URLs or a process to generate them
S3_TRAIN_URLS=(
  "s3://bucket/path_for_train/"
  "s3://bucket/path_for_train2/"
)

# Construct the training command
TRAIN_COMMAND="python3 /mmdet/tools/train_with_s3_data_sahi.py --s3-url"
for url in "${S3_TRAIN_URLS[@]}"; do
  TRAIN_COMMAND+=" \"$url\""
done
TRAIN_COMMAND+=" --config /mmdet/${CONFIG_FILE}"

FILE="docker-compose.train_test.yaml"
PROJECT=$(basename "$(pwd)" | tr '[:upper:]' '[:lower:]') # Extract the current directory name

# Export variables to be used by Docker Compose
export S3_VAL_URL
export CONFIG_FILE

echo "FUll CMD: docker compose -f $FILE run mm_train $TRAIN_COMMAND"

# # # Build services
docker compose -f $FILE build mm_train # --no-cache
docker compose -f $FILE build mm_test # --no-cache

# # # Run the mm_train service with the dynamically generated command
docker compose -f $FILE run mm_train bash -c "$TRAIN_COMMAND"

# Wait for the first service to complete
docker compose -f $FILE wait "${PROJECT}-mm_train"

# Start the second mmdetection service
docker compose -f $FILE up mm_test
