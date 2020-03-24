# coding=utf-8
class RET:
    # 0: 响应正常
    OK = 0

    # 1 - 1000: 网络请求错误
    NORCV = 1
    SNTERR = 2 # 发送方请求方法错误

    # 1001 - 2000: 数据库错误
    NODATA = 1001

    
    # 2001 - 3000: 用户登录错误
    AUTHERR = 2002

    # 8001 - 9000: 特殊操作请求


    UNKNOWN = 9999

ret_map = {
    RET.OK: u"成功",
    RET.NORCV: u"未收到数据",
    RET.SNTERR: u"发送数据错误",
    RET.NODATA: u"无相应数据",
    RET.AUTHERR: u"认证错误",
    RET.UNKNOWN: u"未知错误"
}