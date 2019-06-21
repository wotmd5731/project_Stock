# -*- coding: utf-8 -*-
"""
Created on Thu May 16 21:56:10 2019

@author: JAE
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
from define import RealType,FidList,ReturnCode

import queue

from multiprocessing import Process, Lock


class mylock():
    def __init__(self):
        self.lock = Lock()
        self.name = ""
        self.data = []
        self.tr_code = 0
    def __enter__(self):
        self.lock.acquire()
    def __exit__(self, type, value, traceback):
        self.lock.release()
        

class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        print('setup kiwoom')
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        self.scr_num ='99'
#        self.q = queue.Queue(maxsize=1)
        
        self.lock = mylock()
        
        
        
            
        # Loop 변수
        # 비동기 방식으로 동작되는 이벤트를 동기화(순서대로 동작) 시킬 때
        self.login_loop = None
        self.request_loop = None
        self.order_loop = None
        self.condition_loop = None
        self.tr_event_loop = None
        # 서버구분
        self.server_gubun = None

        # 조건식
        self.condition = None

        # 에러
        self.error = None

        # 주문번호
        self.order_no = ""

        # 조회
        self.inquiry = 0

        # 서버에서 받은 메시지
        self.msg = ""

        # 예수금 d+2
#        self.data_opw00001 = 0
#
#        # 보유종목 정보
#        self.data_opw00018 = {'account_evaluation': [], 'stocks': []}
#
#        # 주가상세정보
#        self.data_opt10081 = [] * 15
#        self.data_opt10086 = [] * 23

        # signal & slot
        self.OnEventConnect.connect(self._OnEventConnect)
        self.OnReceiveTrData.connect(self._OnReceiveTrData)
#        self.OnReceiveChejanData.connect(self.on_receive_chejan_data)
#        self.OnReceiveRealData.connect(self.receive_real_data)
        self.OnReceiveMsg.connect(self._OnReceiveMsg)
#        self.OnReceiveConditionVer.connect(self.receive_condition_ver)
#        self.OnReceiveTrCondition.connect(self.receive_tr_condition)
#        self.OnReceiveRealCondition.connect(self.receive_real_condition)
        self.dic = {
            '주식기본정보요청':'OPT10001',
            '주식거래원요청':'OPT10002',
            '체결정보요청':'OPT10003',
            '주식호가요청':'OPT10004',
            '주식일주월시분요청':'OPT10005',
            '주식시분요청':'OPT10006',
            '시세표성정보요청':'OPT10007',
            '주식외국인요청':'OPT10008',
            '주식기관요청':'OPT10009',
            '업종프로그램요청':'OPT10010',
            '투자자정보요청':'OPT10011',
            '주문체결요청':'OPT10012',
            '신용매매동향요청':'OPT10013',
            '공매도추위요청':'OPT10014',
            '일별거래상세요청':'OPT10015',
            '신고저가요청':'OPT10016',
            '상하한가요청':'OPT10017',
            '고저가근접요청':'OPT10018',
            '가격급등락요청':'OPT10019',
            '호가잔량상위요청':'OPT10020',
            '호가잔량급증요청':'OPT10021',
            '잔량율급증요청':'OPT10022',
            '거래량급증요청':'OPT10023',
            '거래량갱신요청':'OPT10024',
            '매물대집중요청':'OPT10025',
            '고저PER됴청':'OPT10026',
            '전일대비등락율상위요청':'OPT10027',
            '시가대비등락율요쳥':'OPT10028',
            '예상체결등락률상위요청':'OPT10029',
            '당일거래량상위요청':'OPT10030',
            '전일거래량상위요청':'OPT10031',
            '거래대금상위요청':'OPT10032',
            '신용비율상위요청':'OPT10033',
            '외인기간별매매상위요청':'OPT10034',
            '외인연속순매매상위요청':'OPT10035',
            '매매상위요청':'OPT10036',
            '외국계창구매매상위요청':'OPT10037',
            '종목별증권사순위요청':'OPT10038',
            '증권사별매매상위요청':'OPT10039',
            '당일주요거래원요청':'OPT10040',
            '조기종료통화단위요청':'OPT10041',
            '순매수거래원순위요청':'OPT10042',
            '거래원매물대분석요청':'OPT10043',
            '일별기관매매종목요청':'OPT10044',
            '종목별기관매매추이요청':'OPT10045',
            '투자자별일별매매종목요청':'OPT10058',
            '종목별투자자기관별요청':'OPT10059',
            '종목별투자자기관별차트요청':'OPT10060',
            '종목별투자자기관별합계요청':'OPT10061',
            '동일순매매순위요청':'OPT10062',
            '장중투자자별매매요청':'OPT10063',
            '장중투자자별매매차트요청':'OPT10064',
            '장중투자자별매매상위요청':'OPT10065',
            '일자별실현손익요청':'OPT10074',
            '실시간미체결요청':'OPT10075',
            '실시간체결요청':'OPT10076',
            '당일실현손익상세요청':'OPT10077',
           }            
    
    def _OnReceiveTrData(self, screen_no, request_name, tr_code, record_name, sPrevNext, unused0, unused1, unused2,
                           unused3):
        print('_OnReceiveTrData,',screen_no,request_name,tr_code,record_name,sPrevNext)
        """
        BSTR sScrNo,       // 화면번호
          BSTR sRQName,      // 사용자 구분명
          BSTR sTrCode,      // TR이름
          BSTR sRecordName,  // 레코드 이름
          BSTR sPrevNext,    // 연속조회 유무를 판단하는 값 0: 연속(추가조회)데이터 없음, 1:연속(추가조회) 데이터 있음
          LONG nDataLength,  // 사용안함.
        """
        if screen_no != self.scr_num:
            print('diff scr num')
            
#        with self.lock:
#            self.lock.name = request_name
#            self.lock.tr_code = tr_code
#            self.lock.data = []
            
        if request_name=='주식기본정보요청':
            temp_dic = {}
            lst = ['종목코드','종목명','자본금','액면가','상장주식','신용비율','외인소진률','시가총액','PER','EPS','BPS','PBR','매출액','영업이익','당기순이익','시가','고가','저가','기준가','현재가','전일대비','등락율','거래량','거래대비','유통주식','유통비율']
            for st in lst:
                temp_dic[st] = self.GetCommData(tr_code,"", request_name, 0,st)
            self.lock.data = temp_dic
            
#        if request_name=='주식거래원요청' or \
#            request_name=='체결정보요청' or \
#            request_name=='주식호가요청' or\
#            request_name=='주식일주월시분요청' or\
#            request_name=='주식시분요청' :
#            self.lock.data= self.GetCommDataEx(tr_code,record_name)
                
        if request_name=='조건검색A':
            pass
        
        
#        dic_list = self.dic.keys()
#        if request_name==dic_list[0] and tr_code == 'opt10079':
#            print(self.GetCommDataEx(tr_code,record_name))
        
        
        
#        if request_name=='틱정보' and tr_code == 'opt10079':
#            print(self.GetCommDataEx(tr_code,record_name))
#            
#        if request_name=='일데이터' and tr_code == 'opt10081':
#            print(self.GetCommDataEx(tr_code,record_name))
        
            
            
        self.tr_event_loop.exit()
        

    def _OnEventConnect(self, return_code):
        """
        통신 연결 상태 변경시 이벤트
        return_code 0이면 로그인 성공
        그 외에는 ReturnCode 클래스 참조.
        :param return_code: int
        """
        if return_code==0:
            print('event : login Success')
        else:
            print('event : login Fail')
        self.login_loop.exit()
        
    def _OnReceiveMsg(self, screen_no, request_name, tr_code, msg):
        print('msg :',screen_no,request_name, tr_code, msg)
        """
        수신 메시지 이벤트

        서버로 어떤 요청을 했을 때(로그인, 주문, 조회 등), 그 요청에 대한 처리내용을 전달해준다.

        :param screen_no: string - 화면번호(4자리, 사용자 정의, 서버에 조회나 주문을 요청할 때 이 요청을 구별하기 위한 키값)
        :param request_name: string - TR 요청명(사용자 정의)
        :param tr_code: string
        :param msg: string - 서버로 부터의 메시지
        """
    def GetRepeatCnt(self, tr_code, request_name):
        """
        서버로 부터 전달받은 데이터의 갯수를 리턴합니다.(멀티데이터의 갯수)

        receiveTrData() 이벤트 메서드가 호출될 때, 그 안에서 사용해야 합니다.

        키움 OpenApi+에서는 데이터를 싱글데이터와 멀티데이터로 구분합니다.
        싱글데이터란, 서버로 부터 전달받은 데이터 내에서, 중복되는 키(항목이름)가 하나도 없을 경우.
        예를들면, 데이터가 '종목코드', '종목명', '상장일', '상장주식수' 처럼 키(항목이름)가 중복되지 않는 경우를 말합니다.
        반면 멀티데이터란, 서버로 부터 전달받은 데이터 내에서, 일정 간격으로 키(항목이름)가 반복될 경우를 말합니다.
        예를들면, 10일간의 일봉데이터를 요청할 경우 '종목코드', '일자', '시가', '고가', '저가' 이러한 항목이 10번 반복되는 경우입니다.
        이러한 멀티데이터의 경우 반복 횟수(=데이터의 갯수)만큼, 루프를 돌면서 처리하기 위해 이 메서드를 이용하여 멀티데이터의 갯수를 얻을 수 있습니다.

        :param tr_code: string
        :param request_name: string - TR 요청명(comm_rq_data() 메소드 호출시 사용된 request_name)
        :return: int
        """
        ret = self.dynamicCall("GetRepeatCnt(QString, QString)", tr_code, request_name)
        return ret
    def GetCommDataEx(self, tr_code, multi_data_name):
        """
        멀티데이터 획득 메서드

        receiveTrData() 이벤트 메서드가 호출될 때, 그 안에서 사용해야 합니다.

        :param tr_code: string
        :param multi_data_name: string - KOA에 명시된 멀티데이터명
        :return: list - 중첩리스트
        """
        data = self.dynamicCall("GetCommDataEx(QString, QString)", tr_code, multi_data_name)
        return data
    def GetCommData(self, tr_code, real_type, rqname, index, item_name):
        ret = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", tr_code,
                               real_type, rqname, index, item_name)
        return ret.strip()

    
    def CommConnect(self):
        self.dynamicCall('CommConnect()')
        self.login_loop = QEventLoop()
        self.login_loop.exec_()
    
    
    def GetConnectState(self):
        if self.dynamicCall('GetConnectState()') == 1:
            return True
        return False
    

        
    def GetLoginInfo(self):
        """
        "ACCOUNT_CNT" : 보유계좌 수를 반환합니다.
          "ACCLIST" 또는 "ACCNO" : 구분자 ';'로 연결된 보유계좌 목록을 반환합니다.
          "USER_ID" : 사용자 ID를 반환합니다.
          "USER_NAME" : 사용자 이름을 반환합니다.
          "KEY_BSECGB" : 키보드 보안 해지여부를 반환합니다.(0 : 정상, 1 : 해지)
          "FIREW_SECGB" : 방화벽 설정여부를 반환합니다.(0 : 미설정, 1 : 설정, 2 : 해지)
          "GetServerGubun" : 접속서버 구분을 반환합니다.(1 : 모의투자, 나머지 : 실서버)
        """
        dic={}
        for tag in ["ACCOUNT_CNT","ACCNO","USER_ID","USER_NAME","GetServerGubun" ]:
            dic[tag] = self.dynamicCall('GetLoginInfo("{0}")'.format(tag))
        if dic['GetServerGubun']=='1':
            dic['GetServerGubun'] = '모의서버'
        else:
            dic['GetServerGubun'] = '실서버'
        return dic
#        self.login_loop = QEventLoop()
#        self.login_loop.exec_()
#        
    
    def CommRqData(self,sRQName, sTrCode, nPrevNext, sScreenNo ):
#        self.dynamicCall('CommRqData({},{},{},{})'.format(sRQName, sTrCode, nPrevNext, sScreenNo)) 
        return self.dynamicCall("CommRqData(QString, QString, int, QString)", sRQName, sTrCode, nPrevNext, sScreenNo)
    def CommKwRqData(self,Arrcode , bnext, nCodecount,ntypeflag, sRQname, sScreenNo ):
#        self.dynamicCall('CommRqData({},{},{},{})'.format(sRQName, sTrCode, nPrevNext, sScreenNo)) 
        return self.dynamicCall("CommKwRqData(QString, int , int, int, QString,QString)",Arrcode , bnext, nCodecount,ntypeflag, sRQname, sScreenNo)
       
    def SetInputValue(self, id, value):
        self.dynamicCall("SetInputValue(QString, QString)", id, value)
    
    
    

    

    def read_opt(self,req='체결정보요청', code='005930'):
        
        opt = self.dic[req]
        self.SetInputValue("종목코드"	,  code)
        ret = self.CommRqData( req,  opt	,  "0"	,  self.scr_num)
        print('return :',ret)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()
        
        with self.lock:
            print(self.lock.name,
            self.lock.tr_code ,
            self.lock.data)
            
        return 
    
    def read_kwrq(self,req='체결정보요청', code='005930'):
        
        opt = self.dic[req]
        self.SetInputValue("종목코드"	,  code)
        codelist = ['005930','005930','005930']
        
        ret = self.CommKwRqData(codelist ,  0	, len(codelist), 0	,'KW100_REQ', self.scr_num)
        print('return :',ret)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()
        
        
            
        return 
    
        
    def read_tick(self, code='005930',tick='30'):
    #        ['1','3','6','10','30']
        self.SetInputValue("종목코드"	,  code)
    	#틱범위 = 1:1틱, 3:3틱, 5:5틱, 10:10틱, 30:30틱
        self.SetInputValue("틱범위"	,  tick)
    #    	수정주가구분 = 0 or 1, 수신데이터 1:유상증자, 2:무상증자, 4:배당락, 8:액면분할, 16:액면병합, 32:기업합병, 64:감자, 256:권리락
        self.SetInputValue("수정주가구분"	,  "1")
    #        InputValue("수정주가구분"	,  "1");
        ret = self.CommRqData( "틱정보"	,  "opt10079"	,  "0"	,  self.scr_num)
        print('return :',ret)
        
        self.tr_event_loop.exec_()
        
        
        
        
    
    def read_day(self, code='005930', date='20160102'):
    #        ['1','3','6','10','30']
        self.SetInputValue("종목코드"	,  code)
    #	기준일자 = YYYYMMDD (20160101 연도4자리, 월 2자리, 일 2자리 형식)
        self.SetInputValue("기준일자"	,  date)
    #    	수정주가구분 = 0 or 1, 수신데이터 1:유상증자, 2:무상증자, 4:배당락, 8:액면분할, 16:액면병합, 32:기업합병, 64:감자, 256:권리락
        self.SetInputValue("수정주가구분"	,  "1")
    #        InputValue("수정주가구분"	,  "1");
        ret = self.CommRqData( "일데이터"	,  "opt10081"	,  "0"	,  self.scr_num)
        print('return :',ret)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()
    
    def read_stock_code(self, code='005930'):
        self.SetInputValue("종목코드"	,  code)
        ret = self.CommRqData( "주식기본정보요청"	,  "opt10001"	,  "0"	,  self.scr_num)
        print('return :',ret)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()
        
        
    


app = QApplication(sys.argv)
kk = Kiwoom()
kk.CommConnect()
print(kk.GetConnectState())
print(kk.GetLoginInfo())


