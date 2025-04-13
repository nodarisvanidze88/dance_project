from uuid import uuid4
from django.conf import settings
from mimetypes import guess_type
import boto3
def str_to_bool(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        value = value.lower()
        if value in ('true', '1', 'yes'):
            return True
        elif value in ('false', '0', 'no'):
            return False
        

# def upload_image_to_spaces(file_obj, folder="category_images/"):
#     """
#     Uploads an image file to the specified folder in S3 storage.
#     """
#     file_extension = file_obj.name.split('.')[-1]
#     file_name = f"{folder}{uuid4()}.{file_extension}"
#     session = boto3.session.Session()
#     client = session.client(
#         's3',
#         region_name='lon1',
#         endpoint_url=settings.AWS_S3_ENDPOINT_URL,
#         aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
#         aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
#     )
#     content_type,_=guess_type(file_obj.name)
#     client.put_object(
#         Bucket=settings.AWS_STORAGE_BUCKET_NAME,
#         Key=file_name,
#         Body=file_obj.read(),
#         ACL='public-read',
#         ContentType=content_type or 'application/octet-stream'
#     )
#     return f"{settings.AWS_S3_ENDPOINT_URL}/{file_name}"