import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
LANGUAGE_CODE = 'zh-hans'

######### sms短信 ##########
APP_ID = 1400761903
APP_KEY = '092512163be1f9a25bdec153797a9328'


SMS_SIGN = 'WANGKS公众号'


TENCENT_SMS_TEMPLATE = {
    'register':1599367,
    'login':1599370,
}


############## cos存储桶 #################
SECRET_ID = 'AKIDYzGNJ7lBOSODsSxKTM9mvvjNwKWVK4bu'
SECRET_KEY = 'BAwVvDNL7nKfzUt68501wjN3bzDi4FGL'


CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379", # 安装redis的主机的 IP 和 端口
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": 1000,
                "encoding": 'utf-8'
            },
            "PASSWORD": "123456" # redis密码
        }
    }
}


##############阿里支付########################
ALI_APPID = '2021000122607964'
ALI_GATEWAY = 'https://openapi.alipaydev.com/gateway.do'
ALI_PRI_KEY_PATH = os.path.join(BASE_DIR,'file/应用私钥.txt')
ALI_PUB_KEY_PATH = os.path.join(BASE_DIR,'file/支付宝公钥.txt')
ALI_NOTIFY_URL = 'http://127.0.0.1:8000/pay/notify/'
ALI_RETURN_URL = 'http://127.0.0.1:8000/pay/notify/'