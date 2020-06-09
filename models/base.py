from datetime import datetime

from peewee import *
from torpeewee import Model as torpeewee_model

from config import DATABASE


class PeeModel(Model):
    createTime = DateTimeField(default=datetime.now, verbose_name="创建时间")

    class Meta:
        database = DATABASE


class BaseModel(PeeModel, torpeewee_model):
    pass

# 建表时打开
# delete FROM `bt_area` where level=4

# class BaseModel(Model):
#     createTime = DateTimeField(default=datetime.now, verbose_name="创建时间")
#
#     class Meta:
#         database = DATABASE
