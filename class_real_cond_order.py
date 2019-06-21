# -*- coding: utf-8 -*-
"""
Created on Tue May 28 15:03:26 2019

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
from define import *
from class_request import Kiwoom_request


class Kiwoom_real_cond_order(Kiwoom_request):
    def __init__(self):
        super().__init__()
        # 조건식
        self.condition = None
        self.condition_loop = None
        self.condition_code = 0
        self.OnReceiveConditionVer.connect(self.receive_condition_ver)
        self.OnReceiveTrCondition.connect(self.receive_tr_condition)
        self.OnReceiveRealCondition.connect(self.receive_real_condition)
        
    def send_order(self, request_name, screen_no, account_no, order_type, code, qty, price, hoga_type, origin_order_no):
        """
        주식 주문 메서드

        send_order() 메소드 실행시,
        OnReceiveMsg, OnReceiveTrData, OnReceiveChejanData 이벤트가 발생한다.
        이 중, 주문에 대한 결과 데이터를 얻기 위해서는 OnReceiveChejanData 이벤트를 통해서 처리한다.
        OnReceiveTrData 이벤트를 통해서는 주문번호를 얻을 수 있는데, 주문후 이 이벤트에서 주문번호가 ''공백으로 전달되면,
        주문접수 실패를 의미한다.

        :param request_name: string - 주문 요청명(사용자 정의)
        :param screen_no: string - 화면번호(4자리)
        :param account_no: string - 계좌번호(10자리)
        :param order_type: int - 주문유형(1: 신규매수, 2: 신규매도, 3: 매수취소, 4: 매도취소, 5: 매수정정, 6: 매도정정)
        :param code: string - 종목코드
        :param qty: int - 주문수량
        :param price: int - 주문단가
        :param hoga_type: string - 거래구분(00: 지정가, 03: 시장가, 05: 조건부지정가, 06: 최유리지정가, 그외에는 api 문서참조)
        :param origin_order_no: string - 원주문번호(신규주문에는 공백, 정정및 취소주문시 원주문번호르 입력합니다.)
        """
        if not self.get_connect_state():
            raise KiwoomConnectError()

        if not (isinstance(request_name, str)
                and isinstance(screen_no, str)
                and isinstance(account_no, str)
                and isinstance(order_type, int)
                and isinstance(code, str)
                and isinstance(qty, int)
                and isinstance(price, int)
                and isinstance(hoga_type, str)
                and isinstance(origin_order_no, str)):
            raise ParameterTypeError()

        return_code = self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                                       [request_name, screen_no, account_no, order_type, code, qty, price, hoga_type,
                                        origin_order_no])

        if return_code != ReturnCode.OP_ERR_NONE:
            raise KiwoomProcessingError("send_order(): " + ReturnCode.CAUSE[return_code])

        # receiveTrData() 에서 루프종료
        self.order_loop = QEventLoop()
        self.order_loop.exec_()

        
    
    def receive_condition_ver(self, receive, msg):
        """
        getConditionLoad() 메서드의 조건식 목록 요청에 대한 응답 이벤트

        :param receive: int - 응답결과(1: 성공, 나머지 실패)
        :param msg: string - 메세지
        """

        try:
            if not receive:
                return

            self.condition = self.get_condition_name_list()
#            print("조건식 개수: ", len(self.condition))

#            for key in self.condition.keys():
#                print("조건식: ", key, ": ", self.condition[key])
#                print("key type: ", type(key))

        except Exception as e:
            print(e)

        finally:
            self.condition_loop.exit()

    def receive_tr_condition(self, screen_no, codes, condition_name, condition_index, inquiry):
        """
        (1회성, 실시간) 종목 조건검색 요청시 발생되는 이벤트

        :param screen_no: string
        :param codes: string - 종목코드 목록(각 종목은 세미콜론으로 구분됨)
        :param condition_name: string - 조건식 이름
        :param condition_index: int - 조건식 인덱스
        :param inquiry: int - 조회구분(0: 남은데이터 없음, 2: 남은데이터 있음)
        """

        print("[receive_tr_condition]")

        try:
            if codes == "":
                return

            code_list = codes.split(';')
            del code_list[-1]
            self.condition_code = code_list
#            print(code_list)
#            print("종목개수: ", len(code_list))

        finally:
            self.condition_loop.exit()

    def receive_real_condition(self, code, event, condition_name, condition_index):
        """
        실시간 종목 조건검색 요청시 발생되는 이벤트

        :param code: string - 종목코드
        :param event: string - 이벤트종류("I": 종목편입, "D": 종목이탈)
        :param condition_name: string - 조건식 이름
        :param condition_index: string - 조건식 인덱스(여기서만 인덱스가 string 타입으로 전달됨)
        """

        print("[receive_real_condition]")

        print("종목코드: ", code)
        print("이벤트: ", "종목편입" if event == "I" else "종목이탈")

    def get_condition_load(self):
        """ 조건식 목록 요청 메서드 """

        if not self.get_connect_state():
            raise KiwoomConnectError()

        is_load = self.dynamicCall("GetConditionLoad()")
        
        # 요청 실패시
        if not is_load:
            return False
#            raise KiwoomProcessingError("getConditionLoad(): 조건식 요청 실패")

        # receiveConditionVer() 이벤트 메서드에서 루프 종료
        self.condition_loop = QEventLoop()
        self.condition_loop.exec_()
        return True
    
    def get_condition_name_list(self):
        """
        조건식 획득 메서드

        조건식을 딕셔너리 형태로 반환합니다.
        이 메서드는 반드시 receiveConditionVer() 이벤트 메서드안에서 사용해야 합니다.

        :return: dict - {인덱스:조건명, 인덱스:조건명, ...}
        """

        data = self.dynamicCall("GetConditionNameList()")
#        print(data)
        if data == None:
            raise KiwoomProcessingError("GetConditionNameList(): 사용자 조건식이 없습니다.")
        
        conditionList = data.split(';')
        del conditionList[-1]

        condition_dictionary = {}

        for condition in conditionList:
            key, value = condition.split('^')
            condition_dictionary[int(key)] = value

        return condition_dictionary

    def send_condition(self, screen_no, condition_name, condition_index, is_real_time):
        """
        종목 조건검색 요청 메서드

        이 메서드로 얻고자 하는 것은 해당 조건에 맞는 종목코드이다.
        해당 종목에 대한 상세정보는 set_real_reg() 메서드로 요청할 수 있다.
        요청이 실패하는 경우는, 해당 조건식이 없거나, 조건명과 인덱스가 맞지 않거나, 조회 횟수를 초과하는 경우 발생한다.

        조건검색에 대한 결과는
        1회성 조회의 경우, receiveTrCondition() 이벤트로 결과값이 전달되며
        실시간 조회의 경우, receiveTrCondition()과 receiveRealCondition() 이벤트로 결과값이 전달된다.

        :param screen_no: string
        :param condition_name: string - 조건식 이름
        :param condition_index: int - 조건식 인덱스
        :param is_real_time: int - 조건검색 조회구분(0: 1회성 조회, 1: 실시간 조회)
        """

        if not self.get_connect_state():
            raise KiwoomConnectError()

        if not (isinstance(screen_no, str)
                and isinstance(condition_name, str)
                and isinstance(condition_index, int)
                and isinstance(is_real_time, int)):
            raise ParameterTypeError()

        is_request = self.dynamicCall("SendCondition(QString, QString, int, int",
                                      screen_no, condition_name, condition_index, is_real_time)

        if not is_request:
            raise KiwoomProcessingError("sendCondition(): 조건검색 요청 실패")

        # receiveTrCondition() 이벤트 메서드에서 루프 종료
        self.condition_loop = QEventLoop()
        self.condition_loop.exec_()

    def send_condition_stop(self, screen_no, condition_name, condition_index):
        """ 종목 조건검색 중지 메서드 """

        if not self.get_connect_state():
            raise KiwoomConnectError()

        if not (isinstance(screen_no, str)
                and isinstance(condition_name, str)
                and isinstance(condition_index, int)):
            raise ParameterTypeError()

        self.dynamicCall("SendConditionStop(QString, QString, int)", screen_no, condition_name, condition_index)
