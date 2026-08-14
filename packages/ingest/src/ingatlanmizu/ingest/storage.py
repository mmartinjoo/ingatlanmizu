from pathlib import Path
from typing import Iterator
import boto3
from botocore.exceptions import ClientError
from ingatlanmizu.core.config import settings
import mimetypes

s3 = boto3.client(
    "s3",
    endpoint_url=settings.s3_endpoint_url,
    aws_access_key_id=settings.s3_access_key,
    aws_secret_access_key=settings.s3_secret_key,
)

try:
    s3.head_bucket(Bucket=settings.s3_bucket)
except Exception:
    s3.create_bucket(Bucket=settings.s3_bucket)

def write_html(source: str, external_id: str, html: str, run_id: int) -> str:
    key = _html_file_path_for(source, external_id, run_id=run_id)
    s3.put_object(
        Bucket=settings.s3_bucket,
        Key=key,
        Body=html,
        ContentType="text/plain"
    )
    return key
    
def read_html(source: str, external_id: str, run_id: int) -> tuple[str, str]:
    key = _html_file_path_for(source, external_id, run_id=run_id)
    resp = s3.get_object(
        Bucket=settings.s3_bucket,
        Key=key
    )
    
    return key, resp["Body"].read().decode("utf-8")

def has_images(source: str, external_id: str, ext: str = ".webp") -> bool:
    folder = folder_for_images(source, external_id)
    files = _list_files(folder)
    images = [f for f in files if f.endswith(ext)]
    
    return len(images) > 0

def write_image(source: str, external_id: str, image_url: str, data: bytes) -> None:
    folder = folder_for_images(source, external_id)
    image_name = Path(image_url).name
    key = f"{folder}/{image_name}" 
    content_type, _ = mimetypes.guess_type(image_name)
    s3.put_object(
        Bucket=settings.s3_bucket,
        Key=key,
        Body=data,
        ContentType=content_type or "application/octet-stream"
    )

def folder_for_images(source: str, external_id: str) -> str:
    return f"{source}/images/{external_id}"

def _html_file_path_for(source: str, external_id: str, run_id: int) -> str:
    key = f"{source}/{run_id}/{external_id}/{external_id}.html"
    return key

def _list_files(directory: str) -> Iterator[str]:
    resp = s3.list_objects_v2(
        Bucket=settings.s3_bucket,
        Prefix=directory,
    )
    
    for obj in resp.get("Contents", []):
        yield obj["Key"]