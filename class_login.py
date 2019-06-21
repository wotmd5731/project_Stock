# -*- coding: utf-8 -*-
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

class Kiwoom_login(QAxWidget):
    def __init__(self):
        super().__init__()
        print('setup kiwoom')
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

        # Loop 변수
        # 비동기 방식으로 동작되는 이벤트를 동기화(순서대로 동작) 시킬 때
        
        self.order_loop = None
        

        # 서버구분
        self.server_gubun = None

        

        # 에러
        self.error = None

        # 주문번호
        self.order_no = ""

        # 조회
        self.inquiry = 0
        self.data = 0
        
        # 서버에서 받은 메시지
        self.msg = ""

        

        # signal & slot
        self.OnEventConnect.connect(self.event_connect)
#        self.OnReceiveTrData.connect(self.on_receive_tr_data)
#        self.OnReceiveChejanData.connect(self.on_receive_chejan_data)
#        self.OnReceiveRealData.connect(self.receive_real_data)
        self.OnReceiveMsg.connect(self.receive_msg)
#        self.OnReceiveConditionVer.connect(self.receive_condition_ver)
#        self.OnReceiveTrCondition.connect(self.receive_tr_condition)
#        self.OnReceiveRealCondition.connect(self.receive_real_condition)
        logging.config.fileConfig('logging.conf')
        self.log = logging.getLogger('Kiwoom')
        # 로깅용 설정파일
        
        # read excel 
    
    def logger(origin):
        def wrapper(*args, **kwargs):
            args[0].log.debug('{} args - {}, kwargs - {}'.format(origin.__name__, args, kwargs))
            return origin(*args, **kwargs)

        return wrapper
    def receive_msg(self, screen_no, request_name, tr_code, msg):
        print('msg :',screen_no,request_name, tr_code, msg)
        """
        수신 메시지 이벤트

        서버로 어떤 요청을 했을 때(로그인, 주문, 조회 등), 그 요청에 대한 처리내용을 전달해준다.

        :param screen_no: string - 화면번호(4자리, 사용자 정의, 서버에 조회나 주문을 요청할 때 이 요청을 구별하기 위한 키값)
        :param request_name: string - TR 요청명(사용자 정의)
        :param tr_code: string
        :param msg: string - 서버로 부터의 메시지
        """

        if request_name == "서버구분":

            if msg.find('모의투자') < 0:
                self.server_gubun = 1

            else:
                self.server_gubun = 0

            try:
                self.order_loop.exit()
            except AttributeError:
                pass
            finally:
                return

        self.msg += request_name + ": " + msg + "\r\n\r\n"

    def event_connect(self, return_code):
        """
        통신 연결 상태 변경시 이벤트

        return_code 0이면 로그인 성공
        그 외에는 ReturnCode 클래스 참조.

        :param return_code: int
        """
        try:
            if return_code == ReturnCode.OP_ERR_NONE:
                if self.GetLoginInfo("GetServerGubun", True):
                    self.msg += "실서버 연결 성공" + "\r\n\r\n"
                    print("실서버 연결 성공" + "\r\n\r\n")
                else:
                    self.msg += "모의투자서버 연결 성공" + "\r\n\r\n"
                    print("모의투자서버 연결 성공" + "\r\n\r\n")
            else:
                self.msg += "연결 끊김: 원인 - " + ReturnCode.CAUSE[return_code] + "\r\n\r\n"
                print("연결 끊김: 원인 - " + ReturnCode.CAUSE[return_code] + "\r\n\r\n")
        except Exception as error:
            self.log.error('eventConnect {}'.format(error))
        finally:
            # commConnect() 메서드에 의해 생성된 루프를 종료시킨다.
            # 로그인 후, 통신이 끊길 경우를 대비해서 예외처리함.
            try:
                self.login_loop.exit()
            except AttributeError:
                pass
    def CommConnect(self):
        """
        로그인을 시도합니다.

        수동 로그인일 경우, 로그인창을 출력해서 로그인을 시도.
        자동 로그인일 경우, 로그인창 출력없이 로그인 시도.
        """
        print('comm connect')
        self.dynamicCall("CommConnect()")
        "call --> On EventConnect"
        self.login_loop = QEventLoop()
        self.login_loop.exec_()
        return 0
    def get_connect_state(self):
        """
        현재 접속상태를 반환합니다.

        반환되는 접속상태는 아래와 같습니다.
        0: 미연결, 1: 연결

        :return: int
        """
        ret = self.dynamicCall("GetConnectState()")
        return ret
    
    
   
    
#    def GetLoginInfo_All(self):
#        lst = ['ACCOUNT_CNT', 'ACCNO', 'USER_ID', 'USER_NAME']
#        dic = {}
#        
#        for n in lst:
#            dic[n] = self.GetLoginInfo(n)
#        return dic
    
        
        
    def GetLoginInfo(self):
        """
        사용자의 tag에 해당하는 정보를 반환한다.

        tag에 올 수 있는 값은 아래와 같다.
        ACCOUNT_CNT: 전체 계좌의 개수를 반환한다.
        ACCNO: 전체 계좌 목록을 반환한다. 계좌별 구분은 ;(세미콜론) 이다.
        USER_ID: 사용자 ID를 반환한다.
        USER_NAME: 사용자명을 반환한다.
        GetServerGubun: 접속서버 구분을 반환합니다.(0: 모의투자, 그외: 실서버)

        :param tag: string
        :param is_connect_state: bool - 접속상태을 확인할 필요가 없는 경우 True로 설정.
        :return: string
        """
#        if not is_connect_state:
#            if not self.get_connect_state():
#                raise KiwoomConnectError()

#        if not isinstance(tag, str):
#            raise ParameterTypeError()

#        if tag not in ['ACCOUNT_CNT', 'ACCNO', 'USER_ID', 'USER_NAME']:
#            raise ParameterValueError()
#
#        cmd = 'GetLoginInfo("%s")' % tag
#        info = self.dynamicCall(cmd)
        
        dic={}
        for tag in ["ACCOUNT_CNT","ACCNO","USER_ID","USER_NAME","GetServerGubun" ]:
            dic[tag] = self.dynamicCall('GetLoginInfo("{0}")'.format(tag))
        if dic['GetServerGubun']=='1':
            dic['GetServerGubun'] = '모의서버'
        else:
            dic['GetServerGubun'] = '실서버'
        return dic
        