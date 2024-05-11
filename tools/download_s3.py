import argparse
import boto3
import botocore
from urllib.parse import urlparse
import os

def download_s3_folder(s3_url, local_path, aws_access_key_id=None, aws_secret_access_key=None, aws_session_token=None):
    # Parse the S3 URL
    parsed_url = urlparse(s3_url)
    bucket_name = parsed_url.netloc
    folder_key = parsed_url.path.lstrip('/')

    # Read from environment variables if command-line args not provided
    access_key_id = aws_access_key_id or os.getenv('AWS_ACCESS_KEY_ID')
    secret_access_key = aws_secret_access_key or os.getenv('AWS_SECRET_ACCESS_KEY')
    session_token = aws_session_token or os.getenv('AWS_SESSION_TOKEN')

    # Initialize S3 client with credentials
    s3 = boto3.client('s3', aws_access_key_id=access_key_id,
                      aws_secret_access_key=secret_access_key,
                      aws_session_token=session_token)

    try:
        # List objects in the folder
        objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=folder_key).get('Contents', [])

        if objects:
            # Create local folder if it doesn't exist
            os.makedirs(local_path, exist_ok=True)

            for obj in objects:
                object_key = obj['Key']
                
                # Check if the object is considered a "directory"; skip if true
                if object_key.endswith('/'):
                    continue

                local_file_path = os.path.join(local_path, object_key[len(folder_key):].lstrip('/'))

                # Create subdirectories if they don't exist
                os.makedirs(os.path.dirname(local_file_path), exist_ok=True)

                # Download the file
                s3.download_file(bucket_name, object_key, local_file_path)
                print(f"File {object_key} downloaded successfully to {local_file_path}")

            print(f"All files in the folder downloaded successfully to {local_path}")
    except botocore.exceptions.ClientError as e:
        print(f"Error: {e}")

def parse_args():
    parser = argparse.ArgumentParser(description="Download files from an S3 folder with specified credentials or from environment.")
    parser.add_argument("s3_url", help="S3 URL of the folder to download")
    parser.add_argument("local_path", help="Local path to save the downloaded files")
    parser.add_argument("--aws-access-key-id", help="AWS Access Key ID (optional, uses environment variable if not provided)")
    parser.add_argument("--aws-secret-access-key", help="AWS Secret Access Key (optional, uses environment variable if not provided)")
    parser.add_argument("--aws-session-token", help="AWS Session Token (optional, uses environment variable if not provided)")

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    download_s3_folder(
        args.s3_url,
        args.local_path,
        args.aws_access_key_id,
        args.aws_secret_access_key,
        args.aws_session_token
    )