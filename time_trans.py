# encoding: utf-8
"""
@author:  lingxiao he
@contact: xiaomingzhidao1@gmail.com
"""

import time
import datetime


def time_to_unix(dt):
    #转换成时间数组
    timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
    #转换成时间戳
    unixtime = time.mktime(timeArray)
    return unixtime

# 正确10位长度的时间戳可精确到秒，11-14位长度则是包含了毫秒
def unix_to_time(intValue):
	if len(str(intValue)) == 10:
		# 精确到秒
		timeValue = time.localtime(intValue)
		tempDate = time.strftime("%Y-%m-%d %H:%M:%S", timeValue)
		datetimeValue = datetime.datetime.strptime(tempDate, "%Y-%m-%d %H:%M:%S")
	elif 10 <len(str(intValue)) and len(str(intValue)) < 15:
		# 精确到毫秒
		k = len(str(intValue)) - 10
		timetamp = datetime.datetime.fromtimestamp(intValue/(1* 10**k))
		datetimeValue = timetamp.strftime("%Y-%m-%d %H:%M:%S.%f")
	else:
		return -1
	return datetimeValue


                    
    