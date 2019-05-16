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




class Kiwoom(QAxWidget):
    def __init__(self):
        super().__init__()
        print('setup kiwoom')
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")
        self.scr_num ='99'
        # Loop 변수
        # 비동기 방식으로 동작되는 이벤트를 동기화(순서대로 동작) 시킬 때
        self.login_loop = None
        self.request_loop = None
        self.order_loop = None
        self.condition_loop = None

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
    
    
    def _OnReceiveTrData(self, screen_no, request_name, tr_code, record_name, sPrevNext, unused0, unused1, unused2,
                           unused3):
        print('_OnReceiveTrData,',screen_no,request_name,tr_code,sPrevNext)
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
        if request_name=='틱정보' and tr_code == 'opt10079':
            print(self.GetCommDataEx(tr_code,record_name))
            
        if request_name=='일데이터' and tr_code == 'opt10081':
            print(self.GetCommDataEx(tr_code,record_name))
        
        

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
    
    def SetInputValue(self, id, value):
        self.dynamicCall("SetInputValue(QString, QString)", id, value)
    
def read_tick(self,tick='30'):
#        ['1','3','6','10','30']
    self.SetInputValue("종목코드"	,  "005930")
	#틱범위 = 1:1틱, 3:3틱, 5:5틱, 10:10틱, 30:30틱
    self.SetInputValue("틱범위"	,  tick)
#    	수정주가구분 = 0 or 1, 수신데이터 1:유상증자, 2:무상증자, 4:배당락, 8:액면분할, 16:액면병합, 32:기업합병, 64:감자, 256:권리락
    self.SetInputValue("수정주가구분"	,  "1")
#        InputValue("수정주가구분"	,  "1");
    ret = self.CommRqData( "틱정보"	,  "opt10079"	,  "0"	,  self.scr_num)
    print('return :',ret)

def read_day(self, date='20160102'):
#        ['1','3','6','10','30']
    self.SetInputValue("종목코드"	,  "005930")
#	기준일자 = YYYYMMDD (20160101 연도4자리, 월 2자리, 일 2자리 형식)
    self.SetInputValue("기준일자"	,  date)
#    	수정주가구분 = 0 or 1, 수신데이터 1:유상증자, 2:무상증자, 4:배당락, 8:액면분할, 16:액면병합, 32:기업합병, 64:감자, 256:권리락
    self.SetInputValue("수정주가구분"	,  "1")
#        InputValue("수정주가구분"	,  "1");
    ret = self.CommRqData( "일데이터"	,  "opt10081"	,  "0"	,  self.scr_num)
    print('return :',ret)



            
    
app = QApplication(sys.argv)
kk = Kiwoom()
kk.CommConnect()
print(kk.GetConnectState())
print(kk.GetLoginInfo())


