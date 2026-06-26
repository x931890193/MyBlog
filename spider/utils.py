from pymongo import MongoClient
from constants import MONGO_URI, MONGODB_NAME, QINIU_ACCESS_KEY, QINIU_SECRET_KEY, QINIU_BUCKET_NAME
from qiniu import Auth, put_data


def get_mongo():
    return MongoClient(
        MONGO_URI,
        connect=False,
        serverSelectionTimeoutMS=2000,
        connectTimeoutMS=2000,
        socketTimeoutMS=3000,
    )[MONGODB_NAME]


class QiNiu(object):
    def __init__(self):
        self.user = Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)
        self.bucket_name = QINIU_BUCKET_NAME

    def up_stream(self, stream, key):
        token = self.user.upload_token(self.bucket_name, key, 3600)
        return put_data(token, key, stream, progress_handler=True)


mongodb = get_mongo()
qiniu_client = QiNiu()
