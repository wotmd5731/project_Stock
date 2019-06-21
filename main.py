"""
Kiwoom 클래스는 OCX를 통해 API 함수를 호출할 수 있도록 구현되어 있습니다.
OCX 사용을 위해 QAxWidget 클래스를 상속받아서 구현하였으며,
주식(현물) 거래에 필요한 메서드들만 구현하였습니다.

author: Jongyeol Yang
last edit: 2017. 02. 23
"""
import sys
import logging
import logging.config
import PyQt5
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtCore import QEventLoop
from PyQt5.QtWidgets import QApplication
from pandas import DataFrame
import time
import numpy as np
from datetime import datetime
from define import *
from class_real_cond_order import Kiwoom_real_cond_order
import pandas as pd



class Kiwoom(Kiwoom_real_cond_order):
    def __init__(self):
        super().__init__()


    def get_code_list(self, *market):
        """
        여러 시장의 종목코드를 List 형태로 반환하는 헬퍼 메서드.

        :param market: Tuple - 여러 개의 문자열을 매개변수로 받아 Tuple로 처리한다.
        :return: List
        """
        code_list = []
        for m in market:
            tmp_list = self.get_codelist_by_market(m)
            code_list += tmp_list
        return code_list

    def get_master_code_name(self, code):
        """
        종목코드의 한글명을 반환한다.

        :param code: string - 종목코드
        :return: string - 종목코드의 한글명
        """

        if not self.get_connect_state():
            raise KiwoomConnectError()

        if not isinstance(code, str):
            raise ParameterTypeError()

        cmd = 'GetMasterCodeName("%s")' % code
        name = self.dynamicCall(cmd)
        return name

    def change_format(self, data, percent=0):
        if percent == 0:
            d = int(data)
            format_data = '{:-,d}'.format(d)
        elif percent == 1:
            f = float(data)
            f -= 100
            format_data = '{:-,.2f}'.format(f)
        elif percent == 2:
            f = float(data)
            format_data = '{:-,.2f}'.format(f)
        return format_data





        
#        self.tr_event_loop.exec_()
    def read_stock_info(self, code='005930'):
        self.data=[]
        self.set_input_value("종목코드"	,  code)
        ret = self.CommRqData( "주식기본정보요청"	,  "opt10001"	, 0 , '0001')
        
        print('return :',self.data)
        return self.data
#        self.request_loop = QEventLoop()
#        self.request_loop.exec_()
        
        
        


#
#class kiwoom_wrap():
#
#    def logger(origin):
#        global kk
#        return kk.logger(origin)
#    
#    def event_connect(self, return_code):
#        pass
#
#    def receive_msg(self, screen_no, request_name, tr_code, msg):
#        pass
#    def on_receive_tr_data(self, screen_no, request_name, tr_code, record_name, inquiry, unused0, unused1, unused2,
#                           unused3):
#        pass
#    def receive_real_data(self, code, real_type, real_data):
#        pass
#    def on_receive_chejan_data(self, gubun, item_cnt, fid_list):
#        pass
#    def get_codelist_by_market(self, market):
#        pass
#    def comm_connect(self):
#        global kk
#        return kk.comm_connect()
#    
#    def get_connect_state(self):
#        global kk
#        return kk.get_connect_state()
#    
#    
#    def get_login_info(self, tag, is_connect_state=False):
#        pass
#    def set_input_value(self, id, value):
#        pass
#    def comm_rq_data(self, request_name, tr_code, inquiry, screen_no):
#        pass
#    def comm_get_data(self, code, real_type, field_name, index, item_name):
#        pass
#    def get_repeat_cnt(self, tr_code, request_name):
#        pass
#    def get_comm_data_ex(self, tr_code, multi_data_name):
#        pass
#    def commKwRqData(self, codes, inquiry, codeCount, requestName, screenNo, typeFlag=0):
#        pass
#    def disconnect_real_data(self, screen_no):
#        pass
#    def get_comm_real_data(self, code, fid):
#        pass
#    def set_real_reg(self, screen_no, codes, fids, real_reg_type):
#        pass
#    def set_real_remove(self, screen_no, code):
#        pass
#    def receive_condition_ver(self, receive, msg):
#        pass
#    def receive_tr_condition(self, screen_no, codes, condition_name, condition_index, inquiry):
#        pass
#    def receive_real_condition(self, code, event, condition_name, condition_index):
#        pass
#    def get_condition_load(self):
#        pass
#    def get_condition_name_list(self):
#        pass
#    def send_condition(self, screen_no, condition_name, condition_index, is_real_time):
#        pass
#    def send_condition_stop(self, screen_no, condition_name, condition_index):
#        pass
#    def send_order(self, request_name, screen_no, account_no, order_type, code, qty, price, hoga_type, origin_order_no):
#        pass
#    def GetChejanData(self, nFid):
#        pass
#    def get_code_list(self, *market):
#
#        pass
#    def get_master_code_name(self, code):
#
#        pass
#    def change_format(self, data, percent=0):
#        pass
#
#    def opw_data_reset(self):
#        pass
#
#    pass



#def test_to_get_account():
#    kiwoom.set_input_value("계좌번호", "8086919011")
#    kiwoom.set_input_value("비밀번호", "0000")
#    kiwoom.comm_rq_data("계좌평가잔고내역요청", "opw00018", 2, "2000")
#    while kiwoom.inquiry == '2':
#        time.sleep(0.2)
#        kiwoom.set_input_value("계좌번호", "8086919011")
#        kiwoom.set_input_value("비밀번호", "0000")
#        kiwoom.comm_rq_data("계좌평가잔고내역요청", "opw00018", 2, "2")
#
#    print(kiwoom.data_opw00018['account_evaluation'])
#    print(kiwoom.data_opw00018['stocks'])
#
#
#def test_to_get_opt10081():
#    kiwoom.set_input_value("종목코드", "035420")
#    kiwoom.set_input_value("기준일자", "20170101")
#    kiwoom.set_input_value("수정주가구분", 1)
#    kiwoom.comm_rq_data("주식일봉차트조회요청", "opt10081", 0, "0101")
#    while kiwoom.inquiry == '2':
#        time.sleep(0.2)
#        kiwoom.set_input_value("종목코드", "035420")
#        kiwoom.set_input_value("기준일자", "20170101")
#        kiwoom.set_input_value("수정주가구분", 1)
#        kiwoom.comm_rq_data("주식일봉차트조회요청", "opt10081", 2, "0101")
##
#
#def test_to_get_opt10086():
#    kiwoom.set_input_value("종목코드", "035420")
#    kiwoom.set_input_value("조회일자", "20170101")
#    kiwoom.set_input_value("표시구분", 1)
#    kiwoom.comm_rq_data("일별주가요청", "opt10086", 0, "0101")
#    while kiwoom.inquiry == '2':
#        time.sleep(0.2)
#        kiwoom.set_input_value("종목코드", "035420")
#        kiwoom.set_input_value("조회일자", "20170101")
#        kiwoom.set_input_value("표시구분", 1)
#        kiwoom.comm_rq_data("일별주가요청", "opt10086", 2, "0101")





def get_day_info(self, code='005930', start='20100101', end='20190601'):
    self.data=[]
    self.set_input_value("종목코드", code)
    self.set_input_value("조회일자", end)
    self.set_input_value("표시구분", 0)
    self.comm_rq_data("opt10086_req", "opt10086", 0, "0101")

    while self.inquiry == True:
        time.sleep(0.2)
        self.set_input_value("종목코드", code)
        self.set_input_value("조회일자", end)
        self.set_input_value("표시구분", 0)
        self.comm_rq_data("opt10086_req", "opt10086", 2, "0101")
        s_data = self.data[-1][0]
        if s_data < start:
            self.inquiry = False
            
    data = pd.DataFrame(self.data)
    col_name = ['날짜', '시가', '고가', '저가', '종가', '전일비', '등락률'
                ,'거래량','금액','신용비','개인','기관','외인수량','외국계'
                ,'프로그램','외인비','체결강도','외인보유','외인비중'
                ,'외인순매수','기관순매수','개인순매수','신용잔고율']
    data.columns = col_name
    data = data[data['날짜']>start]
    
    return data

  
def get_day(self, code='005930', start='20100101', end='20161218'):
    self.data=[]
    
    self.set_input_value("종목코드", code)
    self.set_input_value("기준일자", end)
    self.set_input_value("수정주가구분", 1)
    self.comm_rq_data("opt10081_req", "opt10081", 0, "0101")

    while self.inquiry == True:
        time.sleep(0.2)
        self.set_input_value("종목코드", code)
        self.set_input_value("기준일자", end)
        self.set_input_value("수정주가구분", 1)
        self.comm_rq_data("opt10081_req", "opt10081", 2, "0101")
        s_data = self.data[-1][4]
        if s_data < start:
            self.inquiry = False
            
    data = pd.DataFrame(self.data).drop([0,8,9,10,11,12,13,14],axis=1)
    col_name = ['현재가', '거래량', '거래대금', '일자', '시가', '고가', '저가']
    data.columns = col_name
    data = data[data['일자']>start]
    
    return data
def get_week(self, code='005930', start='20100101', end='20161218'):
    self.data=[]
    
    self.set_input_value("종목코드", code)
    self.set_input_value("기준일자", start)
    self.set_input_value("끝일자", end)
    self.set_input_value("수정주가구분", 1)
    self.comm_rq_data("opt10082_req", "opt10082", 0, "0101")

    while self.inquiry == True:
        time.sleep(0.2)
        self.set_input_value("종목코드", code)
        self.set_input_value("기준일자", start)
        self.set_input_value("끝일자", end)
        self.set_input_value("수정주가구분", 1)
        self.comm_rq_data("opt10082_req", "opt10082", 2, "0101")
            
    data = pd.DataFrame(self.data).drop([7,8,9,10,11,12,13],axis=1)
    col_name = ['현재가', '거래량', '거래대금', '일자', '시가', '고가', '저가']
    data.columns = col_name
    
    return data


def get_month(self, code='005930', start='20100101', end='20161218'):
    self.data=[]
    
    self.set_input_value("종목코드", code)
    self.set_input_value("기준일자", start)
    self.set_input_value("끝일자", end)
    self.set_input_value("수정주가구분", 1)
    self.comm_rq_data("opt10083_req", "opt10083", 0, "0101")

    while self.inquiry == True:
        time.sleep(0.2)
        self.set_input_value("종목코드", code)
        self.set_input_value("기준일자", start)
        self.set_input_value("끝일자", end)
        self.set_input_value("수정주가구분", 1)
        self.comm_rq_data("opt10083_req", "opt10083", 2, "0101")
            
    data = pd.DataFrame(self.data).drop([7,8,9,10,11,12,13],axis=1)
    col_name = ['현재가', '거래량', '거래대금', '일자', '시가', '고가', '저가']
    data.columns = col_name
    
    return data

def get_tick(self, code='005930', tick = 30, max_size = 100):
    self.data=[]
    assert(tick in [1,3,5,10,30])
    
    self.set_input_value("종목코드", code)
    self.set_input_value("틱범위", str(tick))
    self.set_input_value("수정주가구분", 1)
    self.comm_rq_data("opt10079_req", "opt10079", 0, "0101")

    while self.inquiry == True:
        time.sleep(0.2)
        self.set_input_value("종목코드", code)
        self.set_input_value("틱범위", str(tick))
        self.set_input_value("수정주가구분", 1)
        self.comm_rq_data("opt10079_req", "opt10079", 2, "0101")
        if len(self.data) >max_size:
            self.inquiry = False
            
    data = pd.DataFrame(self.data).drop([6,7,8,9,10,11,12],axis=1)
    col_name = ['현재가', '거래량', '체결시간', '시가', '고가', '저가']
    data.columns = col_name
    data = data[data.index<max_size]
    return data



def get_min(self, code='005930',  tick = 30, max_size = 100):
    self.data=[]
    assert(tick in [1,3,5,10,15,30,45,60])
    
    self.set_input_value("종목코드", code)
    self.set_input_value("틱범위", str(tick))
    self.set_input_value("수정주가구분", 1)
    self.comm_rq_data("opt10080_req", "opt10080", 0, "0101")

    while self.inquiry == True:
        time.sleep(0.2)
        self.set_input_value("종목코드", code)
        self.set_input_value("틱범위", str(tick))
        self.set_input_value("수정주가구분", 1)
        self.comm_rq_data("opt10080_req", "opt10080", 2, "0101")
        if len(self.data) >max_size:
            self.inquiry = False
            
    data = pd.DataFrame(self.data).drop([6,7,8,9,10,11,12],axis=1)
    col_name = ['현재가', '거래량', '체결시간', '시가', '고가', '저가']
    data.columns = col_name
    data = data[data.index<max_size]
    return data

def get_day_foreigner(self, code='005930', max_size = 100):
    self.data=[]
    
    self.set_input_value("종목코드", code)
    self.comm_rq_data("opt10008_req", "opt10008", 0, "0101")

    while self.inquiry == True:
        time.sleep(0.2)
        self.set_input_value("종목코드", code)
        self.comm_rq_data("opt10008_req", "opt10008", 2, "0101")
        if len(self.data) >max_size:
            self.inquiry = False
            
    data = pd.DataFrame(self.data)
#    col_name = ['a', 'b', 'c', 'd', 'e', 'f']
#    data.columns = col_name
    data = data[data.index<max_size]
    return data

def get_day_gigwan(self, code='005930', max_size = 100):
    self.data=[]
    
    self.set_input_value("종목코드", code)
    self.comm_rq_data("opt10009_req", "opt10009", 0, "0101")

    while self.inquiry == True:
        time.sleep(0.2)
        self.set_input_value("종목코드", code)
        self.comm_rq_data("opt10009_req", "opt10009", 2, "0101")
        if len(self.data) >max_size:
            self.inquiry = False
            
    data = pd.DataFrame(self.data)
#    col_name = ['a', 'b', 'c', 'd', 'e', 'f']
#    data.columns = col_name
    data = data[data.index<max_size]
    return data


def get_day_gongmae(self, code='005930',start='20160101', max_size = 100):
    self.data=[]
    
    self.set_input_value("종목코드", code)
    self.set_input_value("시간구분", "0")
    self.set_input_value("시작일자", start)
    self.set_input_value("종료일자", start)
    
    self.comm_rq_data("opt10014_req", "opt10014", 0, "0101")

    while self.inquiry == True:
        time.sleep(0.2)
        self.set_input_value("종목코드", code)
        self.set_input_value("시간구분", "0")
        self.set_input_value("시작일자", start)
        self.set_input_value("종료일자", start)
    
        self.comm_rq_data("opt10014_req", "opt10014", 2, "0101")
        if len(self.data) >max_size:
            self.inquiry = False
            
    data = pd.DataFrame(self.data)
#    col_name = ['a', 'b', 'c', 'd', 'e', 'f']
#    data.columns = col_name
    data = data[data.index<max_size]
    return data


def condition_search(self):
    if self.get_condition_load():
        print(self.condition)
    self.condition_code = []
    self.send_condition("0156",self.condition[0],0,0)
    print(self.condition_code)

def get_gigwan(self):
    
    pass
def get_outer(self):
    pass
    



#if __name__ == "__main__":
app = QApplication(sys.argv)
kk = Kiwoom()
kk.CommConnect()
print(kk.GetLoginInfo())
print(kk.data_opt10081)



#aa = get_day_info(kk)

#kk.read_day()
#kk.read_tick()

#kiwoom.disconnect_real_data('0001')
#print(kiwoom.data_opt10081)



#kiwoom.dynamicCall('GetLoginInfo("ACCNO")')
#kiwoom.dynamicCall("""CommKwRqData("005930;005930;005930",0,3,0,"관심종목정보요청",0)""")
#arr = 
#          BSTR sArrCode,    // 조회하려는 종목코드 리스트
#          BOOL bNext,   // 연속조회 여부 0:기본값, 1:연속조회(지원안함)
#          int nCodeCount,   // 종목코드 갯수
#          int nTypeFlag,    // 0:주식 관심종목, 3:선물옵션 관심종목
#          BSTR sRQName,   // 사용자 구분명
#          BSTR sScreenNo    // 화면번호
#          )


#test0()

    # Test Code
    

#    data = kiwoom.get_data_opt10086("035420", "20170101")
#    print(len(data))