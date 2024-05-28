import logging
import boto3
from botocore.exceptions import ClientError

import os
import base64

from dotenv import load_dotenv
load_dotenv()


def upload_file(
    file_name,
    bucket,
    object_name=None,
    meta=None
):
    if object_name is None:
        object_name = os.path.basename(file_name)

    s3_client = boto3.client(
        's3',
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_KEY_ACCESS'),
        region_name=os.getenv('AWS_REGION')
    )
    
    try:
        if meta:
            meta_to_string = str(meta).encode('utf-8')
            base_64_meta = base64.b64encode(meta_to_string)
            base_64_meta_string = base_64_meta.decode('utf-8')

            ExtraArgs = {'Metadata': {'file_info': base_64_meta_string}}
        else:
            ExtraArgs = None
            
        response = s3_client.upload_file(file_name, bucket, object_name,
                                         ExtraArgs=ExtraArgs)
    except ClientError as e:
        logging.error(e)
        return False
    
    return True
