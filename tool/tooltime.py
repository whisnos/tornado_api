import datetime
import time

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
TIME_FORMAT = "%H:%M:%S"
 
# 获取当前时间戳
def curTimeStamp():
    return time.time()

#当前毫秒数
def curMilis():
    return int(time.time() * 1000)
 
#当前秒数
def curSeconds():
    return int(time.time())
 
#当前日期 格式%Y-%m-%d %H:%M:%S
def curDatetime():
    # 返回当前日期格式化字符串
    return time.strftime(DATETIME_FORMAT)
    
    # return datetime.datetime.strftime(datetime.datetime.now(), DATETIME_FORMAT)

def curDatetimeObj():
    # 返回当前日期对象
    return datetime.datetime.now()

#当前日期 格式%Y-%m-%d
def curDate():
    return datetime.date.today()
 
#当前时间 格式%Y-%m-%d
def curTime():
    return time.strftime(TIME_FORMAT)
 
#秒转日期
def secondsToDatetime(seconds):
    return time.strftime(DATETIME_FORMAT, time.localtime(seconds))
 
#毫秒转日期
def milisToDatetime(milix):
    return time.strftime(DATETIME_FORMAT, time.localtime(milix//1000))
 
#日期转毫秒
def datetimeToMilis(datetimestr):
    strf = time.strptime(datetimestr, DATETIME_FORMAT)
    return int(time.mktime(strf)) * 1000
 
#日期转秒
def datetimeToSeconds(datetimestr):
    strf = time.strptime(datetimestr, DATETIME_FORMAT)
    return int(time.mktime(strf))
 
#当前年
def curYear():
    return datetime.datetime.now().year
#当前月
def curMonth():
    return datetime.datetime.now().month
 
#当前日
def curDay():
    return datetime.datetime.now().day
 
#当前时
def curHour():
    return datetime.datetime.now().hour
 
#当前分
def curMinute():
    return datetime.datetime.now().minute
 
#当前秒
def curSecond():
    return datetime.datetime.now().second
 
#星期几
def curWeek():
    return datetime.datetime.now().weekday()
 
#几天前的时间
def nowDaysAgo(days):
    daysAgoTime = datetime.datetime.now() - datetime.timedelta(days = days)
    return time.strftime(DATETIME_FORMAT, daysAgoTime.timetuple())
 
#几天后的时间
def nowDaysAfter(days):
    daysAgoTime = datetime.datetime.now() + datetime.timedelta(days = days)
    return time.strftime(DATETIME_FORMAT, daysAgoTime.timetuple())
 
#某个日期几天前的时间
def dtimeDaysAgo(dtimestr,days):
    daysAgoTime = datetime.datetime.strptime(dtimestr,DATETIME_FORMAT) - datetime.timedelta(days = days)
    return time.strftime(DATETIME_FORMAT, daysAgoTime.timetuple())
 
#某个日期几天前的时间
def dtimeDaysAfter(dtimestr,days):
    daysAgoTime = datetime.datetime.strptime(dtimestr,DATETIME_FORMAT) + datetime.timedelta(days = days)
    return time.strftime(DATETIME_FORMAT, daysAgoTime.timetuple())


UTC_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
LOCAL_FORMAT = "%Y-%m-%d %H:%M:%S"

def utc2local(utc_st):
    '''UTC时间转本地时间（+8:00）'''
    now_stamp = time.time()
    local_time = datetime.datetime.fromtimestamp(now_stamp)
    utc_time = datetime.datetime.utcfromtimestamp(now_stamp)
    offset = local_time - utc_time
    local_st = utc_st + offset
    return local_st

def local2utc(local_st):
    '''本地时间转UTC时间（-8:00）'''
    time_struct = time.mktime(local_st.timetuple())
    utc_st = datetime.datetime.utcfromtimestamp(time_struct)
    return utc_st

def get_local_to_utc(local_time):
    ''' 本地时间转换UTC时间 '''
    temp_time = datetime.datetime.strptime(local_time, LOCAL_FORMAT)
    return local2utc(temp_time)


def get_utc_Timestamp(utc_time):
    ''' 获取UTC时间的时间戳 '''
    temp_time = datetime.datetime.strptime(utc_time, UTC_FORMAT)
    local_time = utc2local(temp_time)
    return time.mktime(local_time.timetuple())

def get_utc_localtime(utc_time):
    ''' 获取UTC时间的本地时间(字符串) '''
    temp_time = datetime.datetime.strptime(utc_time, UTC_FORMAT)
    local_time = utc2local(temp_time)
    return local_time.strftime(LOCAL_FORMAT)

def get_utc_datatime(utc_time):
    ''' 获取UTC时间的 本地时间(datatime对象) '''
    temp_time = datetime.datetime.strptime(utc_time, UTC_FORMAT)
    local_time = utc2local(temp_time)
    return local_time

def string_to_time(tstring, tformat=LOCAL_FORMAT):
    ''' 字符串转时间对象 '''
    return time.strftime(tstring, tformat)

def rest_of_day():
    """
    :return: 截止到目前当日剩余时间
    """
    today = datetime.datetime.strptime(str(datetime.date.today()), "%Y-%m-%d")
    tomorrow = today + datetime.timedelta(days=1)
    nowTime = datetime.datetime.now()
    # return (tomorrow - nowTime).microseconds  # 获取毫秒值
    return (tomorrow - nowTime).seconds  # 获取秒
    # return (tomorrow - nowTime).min  # 获取分钟

if __name__ == '__main__':
    rest_of_day()
    print(get_utc_Timestamp('2019-09-03T08:17:59Z') - time.time())
    print(type(get_utc_localtime('2019-09-03T08:17:59Z')))

    d_local_time = get_utc_datatime('2019-09-03T08:17:59Z')
    print(str(d_local_time))
    print(d_local_time.year)
    print(d_local_time.month)
    print(d_local_time.day)
    print(d_local_time.hour)
    print(d_local_time.minute)
    print(d_local_time.second)
    print(d_local_time.microsecond)

    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print(get_local_to_utc('2019-09-03 16:07:40'))
    # print(utc_to_local())
    # print(utc2local('2019-09-03T07:50:29Z'))

    # print(utc2local('2019-09-03T07:50:29Z'))
    '''
    secondStamp = curSeconds()
    print("当前秒：",secondStamp)
    milisStamp = curMilis()
    print("当前毫秒：",milisStamp)

    curdTime = curDatetime()
    print("当前时间：",curdTime)
    curDate = curDate()
    print("当前日期：",curDate)
    curT = curTime()
    print("当前时刻：",curT)


    stdtime = secondsToDatetime(secondStamp)
    print("秒转时间：",stdtime)
    mtdtime = milisToDatetime(milisStamp)
    print("毫秒转时间：",mtdtime)
    dtimetm = datetimeToMilis(mtdtime)
    print("时间转毫秒：",dtimetm)
    dtimets = datetimeToSeconds(mtdtime)
    print("时间转秒：",dtimets)

    year = curYear()
    print("年：",year)
    month = curMonth()
    print("月：",month)
    day = curDay()
    print("日：",day)
    hour = curHour()
    print("时：",hour)
    minute = curMinute()
    print("分：",minute)
    second = curSecond()
    print("秒：",second)
    week = curWeek()
    print("星期：",week)
    '''