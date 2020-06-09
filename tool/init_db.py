from config import DATABASE
from models.user import Point_Info, Point_Setting, User_Point, User_PointBill, Product_Point, \
    Product_Point_Detail, Express_Info, My_Express_Info, My_Exchange_Info, My_History_Address, My_Address, Area
from models.tbk import Tao_Channel_Info, Tao_Promote_Info, Tao_Banner_Info, Tao_Recommend_Info, \
    Tao_Collect_Info


def init():
    # 生成表
    # DATABASE.create_tables([Point_Info, Point_Setting, User_Point, User_PointBill, Product_Point, Product_Point_Detail])
    # DATABASE.create_tables([
    #     Express_Info, My_Express_Info,
    #     Product_Point, Product_Point_Detail, My_Exchange_Info, My_History_Address,
    #     Area, My_Address,
    # ])
    # DATABASE.create_tables([Area,My_Address])
    DATABASE.create_tables([Tao_Channel_Info])
    # DATABASE.create_tables([Tao_Promote_Info,Tao_Banner_Info,Tao_Recommend_Info,Tao_Collect_Info])


if __name__ == "__main__":
    '''
    如果有创建表
    1、models/base.py  把 BaseModel打开
    2、需要把config里面的DATABASE 切换类型
    '''
    init()
