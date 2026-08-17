from pathlib import Path
from typing import Iterator
import boto3
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
    
def write_mnb_excel(content: str) -> str:
    key = "mnb/alapkamat.xlsx"
    s3.put_object(
        Bucket=settings.s3_bucket,
        Key=key,
        Body=content,
        ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    
    return key