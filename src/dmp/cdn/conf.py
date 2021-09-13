import os

AWS_S3_ENDPOINT_URL = "https://sfo3.digitaloceanspaces.com"
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME=os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_OBJECT_PARAMETERS = {
    "CacheControl": "max-age=86400",
}
AWS_LOCATION = "https://plannit-spaces.sfo3.digitaloceanspaces.com/"

DEFAULT_FILE_STORAGE = "dmp.cdn.backends.StaticRootS3Boto3Storage"
STATICFILE_STORAGE = "dmp.cdn.backends.MediaRootS3Boto3Storage"