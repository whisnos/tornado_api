from datetime import datetime

from peewee import *

from config import DATABASE
from models.base import BaseModel


class User(BaseModel):
    userName = CharField(max_length=50, verbose_name='名')
    certificationStatus = IntegerField(verbose_name="认证状态")
    status = IntegerField(verbose_name="状态")
