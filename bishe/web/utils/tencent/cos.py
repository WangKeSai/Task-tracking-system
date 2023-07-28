# -*- coding=utf-8
from qcloud_cos import CosConfig, CosServiceError
from qcloud_cos import CosS3Client
import sys
import logging
from django.conf import settings
from sts.sts.sts import Sts


def creat_bucket(region, bucket):
    # 正常情况日志级别使用INFO，需要定位时可以修改为DEBUG，此时SDK会打印和服务端的通信信息
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    config = CosConfig(Region=region, SecretId=settings.SECRET_ID, SecretKey=settings.SECRET_KEY)
    client = CosS3Client(config)

    response = client.create_bucket(
        Bucket=bucket,
        ACL='public-read',
    )
    cors_config = {
        "CORSRule": [
            {
                "AllowedOrigin": '*',
                "AllowedMethod": ['GET', 'PUT', 'POST', 'DELETE'],
                "AllowedHeader": '*',
                "ExposeHeader": '*',
                "MaxAgeSeconds": 500
            }
        ]
    }
    client.put_bucket_cors(
        Bucket=bucket,
        CORSConfiguration=cors_config
    )


def check_file(bucket, region, key):
    config = CosConfig(Region=region, SecretId=settings.SECRET_ID, SecretKey=settings.SECRET_KEY)
    client = CosS3Client(config)

    data = client.head_object(
        Bucket=bucket,
        Key=key
    )

    return data


def credential(bucket, region):
    """ 获取cos上传临时凭证 """

    config = {
        # 临时密钥有效时长，单位是秒（30分钟=1800秒）
        'duration_seconds': 5,
        # 固定密钥 id
        'secret_id': settings.SECRET_ID,
        # 固定密钥 key
        'secret_key': settings.SECRET_KEY,
        # 换成你的 bucket
        'bucket': bucket,
        # 换成 bucket 所在地区
        'region': region,
        # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
        # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
        'allow_prefix': '*',
        # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
        'allow_actions': [
            # "name/cos:PutObject",
            # 'name/cos:PostObject',
            # 'name/cos:DeleteObject',
            # "name/cos:UploadPart",
            # "name/cos:UploadPartCopy",
            # "name/cos:CompleteMultipartUpload",
            # "name/cos:AbortMultipartUpload",
            "*",
        ],

    }

    sts = Sts(config)
    result_dict = sts.get_credential()
    return result_dict


def upload_file(region, bucket, file, key):

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    config = CosConfig(Region=region, SecretId=settings.SECRET_ID, SecretKey=settings.SECRET_KEY)
    client = CosS3Client(config)

    response = client.upload_file_from_buffer(
        Bucket=bucket,
        Body=file,
        Key=key
    )
    return 'https://{}.cos.{}.myqcloud.com/{}'.format(bucket, region, key)


def delete_file(region, bucket, key):

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    config = CosConfig(Region=region, SecretId=settings.SECRET_ID, SecretKey=settings.SECRET_KEY)
    client = CosS3Client(config)

    client.delete_object(
        Bucket=bucket,
        Key=key
    )


def delete_files(region, bucket, key_list):

    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    config = CosConfig(Region=region, SecretId=settings.SECRET_ID, SecretKey=settings.SECRET_KEY)
    client = CosS3Client(config)
    objects = {
        "Quiet": "true",
        "Object": key_list
    }
    client.delete_objects(
        Bucket=bucket,
        Delete=objects
    )


def delete_bucket(bucket, region):
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    config = CosConfig(Region=region, SecretId=settings.SECRET_ID, SecretKey=settings.SECRET_KEY)
    client = CosS3Client(config)
    try:
        # 找到文件 & 删除
        while True:
            part_objects = client.list_objects(bucket)

            # 已经删除完毕，获取不到值
            contents = part_objects.get('Contents')
            if not contents:
                break

            # 批量删除
            objects = {
                "Quiet": "true",
                "Object": [{'Key': item["Key"]} for item in contents]
            }
            client.delete_objects(bucket, objects)

            if part_objects['IsTruncated'] == "false":
                break

        # 找到碎片 & 删除
        while True:
            part_uploads = client.list_multipart_uploads(bucket)
            uploads = part_uploads.get('Upload')
            if not uploads:
                break
            for item in uploads:
                client.abort_multipart_upload(bucket, item['Key'], item['UploadId'])
            if part_uploads['IsTruncated'] == "false":
                break

        client.delete_bucket(bucket)
    except CosServiceError as e:
        pass

