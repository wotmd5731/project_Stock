# -*- coding: utf-8 -*-
"""
Created on Tue May 28 14:53:38 2019

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
from class_login import Kiwoom_login
import queue



class Kiwoom_request(Kiwoom_login):
    def __init__(self):
        super().__init__()
        self.login_loop = None
        self.request_loop = None
        # 예수금 d+2
        self.data_opw00001 = 0

        # 보유종목 정보
        self.data_opw00018 = {'account_evaluation': [], 'stocks': []}

        # 주가상세정보
        self.data_opt10081 = [] * 15
        self.data_opt10086 = [] * 23
        
        
        self.q = queue.Queue(10)
        self.ret = 0
        # Loop 변수
        # 비동기 방식으로 동작되는 이벤트를 동기화(순서대로 동작) 시킬 때
        
        # signal & slot
        self.OnReceiveTrData.connect(self.on_receive_tr_data)
        self.OnReceiveChejanData.connect(self.on_receive_chejan_data)
#        self.OnReceiveRealData.connect(self.receive_real_data)
#        self.OnReceiveConditionVer.connect(self.receive_condition_ver)
#        self.OnReceiveTrCondition.connect(self.receive_tr_condition)
#        self.OnReceiveRealCondition.connect(self.receive_real_condition)

    def GetChejanData(self, nFid):
        cmd = 'GetChejanData("%s")' % nFid
        ret = self.dynamicCall(cmd)
        return ret
    
    
    def on_receive_chejan_data(self, gubun, item_cnt, fid_list):
        print("gubun: ", gubun)
        print(self.GetChejanData(9203))
        print(self.GetChejanData(302))
        print(self.GetChejanData(900))
        print(self.GetChejanData(901))

    def get_codelist_by_market(self, market):
        func = 'GetCodeListByMarket("%s")' % market
        codes = self.dynamicCall(func)
        return codes.split(';')    
        
    
    
    def set_input_value(self, id, value):
        self.dynamicCall("SetInputValue(QString, QString)", id, value)

    def comm_rq_data(self, request_name, tr_code, inquiry, screen_no):
        """
        키움서버에 TR 요청을 한다.

        조회요청메서드이며 빈번하게 조회요청시, 시세과부하 에러값 -200이 리턴된다.

        :param request_name: string - TR 요청명(사용자 정의)
        :param tr_code: string
        :param inquiry: int - 조회(0: 조회, 2: 남은 데이터 이어서 요청)
        :param screen_no: string - 화면번호(4자리)
        """

#        if not self.get_connect_state():
#            raise KiwoomConnectError()
#
        if not (isinstance(request_name, str)
                and isinstance(tr_code, str)
                and isinstance(inquiry, int)
                and isinstance(screen_no, str)):
            raise ParameterTypeError()

        return_code = self.dynamicCall("CommRqData(QString, QString, int, QString)", request_name, tr_code, inquiry,
                                       screen_no)

        if return_code != ReturnCode.OP_ERR_NONE:
            raise KiwoomProcessingError("comm_rq_data(): " + ReturnCode.CAUSE[return_code])

        # 루프 생성: receive_tr_data() 메서드에서 루프를 종료시킨다.
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

    def comm_get_data(self, code, real_type, field_name, index, item_name):
        """
        데이터 획득 메서드

        receiveTrData() 이벤트 메서드가 호출될 때, 그 안에서 조회데이터를 얻어오는 메서드입니다.

        :param code: string
        :param real_type: string - TR 요청시 ""(빈문자)로 처리
        :param field_name: string - TR 요청명(comm_rq_data() 메소드 호출시 사용된 field_name)
        :param index: int
        :param item_name: string - 수신 데이터에서 얻고자 하는 값의 키(출력항목이름)
        :return: string
        """
        ret = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", code, real_type,
                               field_name, index, item_name)
        return ret.strip()
    def get_comm_data(self, strTrCode, strRecordName, nIndex, strItemName):
        """
        데이터 획득 메서드

        receiveTrData() 이벤트 메서드가 호출될 때, 그 안에서 조회데이터를 얻어오는 메서드입니다.

        GetCommData(
          BSTR strTrCode,   // TR 이름
          BSTR strRecordName,   // 레코드이름
          long nIndex,      // TR반복부
          BSTR strItemName) // TR에서 얻어오려는 출력항목이름
          
        """
        ret = self.dynamicCall("GetCommData(QString, QString, int, QString)", strTrCode, strRecordName,
                               nIndex, strItemName)
        return ret.strip()
    
    def get_repeat_cnt(self, tr_code, request_name):
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

    def get_comm_data_ex(self, tr_code, multi_data_name):
        """
        멀티데이터 획득 메서드

        receiveTrData() 이벤트 메서드가 호출될 때, 그 안에서 사용해야 합니다.

        :param tr_code: string
        :param multi_data_name: string - KOA에 명시된 멀티데이터명
        :return: list - 중첩리스트
        """

        if not (isinstance(tr_code, str)
                and isinstance(multi_data_name, str)):
            raise ParameterTypeError()

        data = self.dynamicCall("GetCommDataEx(QString, QString)", tr_code, multi_data_name)
        return data

    def commKwRqData(self, codes, inquiry, codeCount, requestName, screenNo, typeFlag=0):
        """
        복수종목조회 메서드(관심종목조회 메서드라고도 함).

        이 메서드는 setInputValue() 메서드를 이용하여, 사전에 필요한 값을 지정하지 않는다.
        단지, 메서드의 매개변수에서 직접 종목코드를 지정하여 호출하며,
        데이터 수신은 receiveTrData() 이벤트에서 아래 명시한 항목들을 1회 수신하며,
        이후 receiveRealData() 이벤트를 통해 실시간 데이터를 얻을 수 있다.

        복수종목조회 TR 코드는 OPTKWFID 이며, 요청 성공시 아래 항목들의 정보를 얻을 수 있다.

        종목코드, 종목명, 현재가, 기준가, 전일대비, 전일대비기호, 등락율, 거래량, 거래대금,
        체결량, 체결강도, 전일거래량대비, 매도호가, 매수호가, 매도1~5차호가, 매수1~5차호가,
        상한가, 하한가, 시가, 고가, 저가, 종가, 체결시간, 예상체결가, 예상체결량, 자본금,
        액면가, 시가총액, 주식수, 호가시간, 일자, 우선매도잔량, 우선매수잔량,우선매도건수,
        우선매수건수, 총매도잔량, 총매수잔량, 총매도건수, 총매수건수, 패리티, 기어링, 손익분기,
        잔본지지, ELW행사가, 전환비율, ELW만기일, 미결제약정, 미결제전일대비, 이론가,
        내재변동성, 델타, 감마, 쎄타, 베가, 로

        :param codes: string - 한번에 100종목까지 조회가능하며 종목코드사이에 세미콜론(;)으로 구분.
        :param inquiry: int - api 문서는 bool 타입이지만, int로 처리(0: 조회, 1: 남은 데이터 이어서 조회)
        :param codeCount: int - codes에 지정한 종목의 갯수.
        :param requestName: string
        :param screenNo: string
        :param typeFlag: int - 주식과 선물옵션 구분(0: 주식, 3: 선물옵션), 주의: 매개변수의 위치를 맨 뒤로 이동함.
        :return: list - 중첩 리스트 [[종목코드, 종목명 ... 종목 정보], [종목코드, 종목명 ... 종목 정보]]
        """

        if not self.get_connect_state():
            raise KiwoomConnectError()

        if not (isinstance(codes, str)
                and isinstance(inquiry, int)
                and isinstance(codeCount, int)
                and isinstance(requestName, str)
                and isinstance(screenNo, str)
                and isinstance(typeFlag, int)):
            raise ParameterTypeError()

        returnCode = self.dynamicCall("CommKwRqData(QString, QBoolean, int, int, QString, QString)",
                                      codes, inquiry, codeCount, typeFlag, requestName, screenNo)

        if returnCode != ReturnCode.OP_ERR_NONE:
            raise KiwoomProcessingError("commKwRqData(): " + ReturnCode.CAUSE[returnCode])

        # 루프 생성: receiveTrData() 메서드에서 루프를 종료시킨다.
        self.requestLoop = QEventLoop()
        self.requestLoop.exec_()

    def on_receive_tr_data(self, screen_no, request_name, tr_code, record_name, inquiry, unused0, unused1, unused2,
                           unused3):
        """
        TR 수신 이벤트

        조회요청 응답을 받거나 조회데이터를 수신했을 때 호출됩니다.
        request_name tr_code comm_rq_data()메소드의 매개변수와 매핑되는 값 입니다.
        조회데이터는 이 이벤트 메서드 내부에서 comm_get_data() 메서드를 이용해서 얻을 수 있습니다.

        :param screen_no: string - 화면번호(4자리)
        :param request_name: string - TR 요청명(comm_rq_data() 메소드 호출시 사용된 requestName)
        :param tr_code: string
        :param record_name: string
        :param inquiry: string - 조회('0': 남은 데이터 없음, '2': 남은 데이터 있음)
        """
        print('next : ',inquiry)
        print("on_receive_tr_data 실행: screen_no: %s, request_name: %s, tr_code: %s, record_name: %s, inquiry: %s" % (
            screen_no, request_name, tr_code, record_name, inquiry))
        
        if inquiry == '2':
            self.inquiry = True
        else:
            self.inquiry = False

        # get data according to tr
        if request_name in ["opt10081_req", "opt10079_req", 
                            "opt10080_req","opt10082_req",
                            "opt10083_req",'opt10086_req',
                            "opt10008_req",'opt10009_req',
                            "opt10014_req",'opt10009_req',
                            ]:
            data = self.get_comm_data_ex(tr_code,request_name)
            print(data)
            self.data.extend(data)
            
            
        elif request_name == '주식기본정보요청':
            ret={}
            items = ['종목명','결산월','액면가','자본금','상장주식',
                  '신용비율','시가총액','시가총액비중','외인소진률',
                  'PER','EPS','ROE','PBR','EV','BPS','매출액','영업이익',
                  '당기순이익','유통주식','유통비율','전일대비']
            nidx = self.get_repeat_cnt(tr_code, request_name[:-2])
            for item in items:
                ret[item] = self.get_comm_data(tr_code, request_name[:-2], nidx, item)
            self.data = ret 

        # exit event loop for tr
        
        try:
            self.tr_event_loop.exit()
        except AttributeError:
            pass
        
        # 주문번호와 주문루프
#        self.order_no = self.comm_get_data(tr_code, "", request_name, 0, "주문번호")
#        self.get_comm_data(tr_code, request_name[:-2])
#        nidx = self.get_repeat_cnt(tr_code, request_name[:-2])
#        vol = self.get_comm_data(tr_code, request_name[:-2], nidx, "거래량")
#        print('repeat count :', nidx, '거래량 : ',vol)
        
        
#        else:
#            self.ret = self.get_comm_data_ex(tr_code, request_name[:-2] )
            
#        print(ret)
#        put_data={'req_name':request_name, 'tr_code':tr_code,'data':ret}
#        self.q.put_nowait(put_data)
        
#        put_data['single'] = self.get_comm_data(tr_code, request_name[:-2])
        
        
#        try:
#            self.request_loop.exit()
#        except AttributeError:
#            pass
        
#        try:
#            self.order_loop.exit()
#        except AttributeError:
#            pass
#
#        self.inquiry = inquiry
#
#        if request_name == "관심종목정보요청":
#            data = self.get_comm_data_ex(tr_code, "관심종목정보")
#
#            """ commGetData
#            cnt = self.getRepeatCnt(trCode, requestName)
#
#            for i in range(cnt):
#                data = self.commGetData(trCode, "", requestName, i, "종목명")
#                print(data)
#            """
#        if request_name == "틱차트조회요청":
#            self.data = self.get_comm_data_ex(tr_code, record_name)
##            print(data)
#            pass
#        
#            
#        if request_name == "주식일봉차트조회요청":
#            data = self.get_comm_data_ex(tr_code, "주식일봉차트조회")
#            if data is not None:
#                data = list(map(lambda x: list(map(lambda y: y.replace('+','').replace('--','-'), x)), np.array(data)[:,1:8].tolist()))
#                data = list(map(lambda x: list(map(lambda y: int(y) if y != '' else 0, x)), data))
#                self.data_opt10081.extend(data)
#                date = str(data[0][3])
#                dt = datetime.strptime(date, "%Y%m%d")
##                if dt <= self.start_date:
##                    self.inquiry = 0
#            if inquiry == "0" or self.inquiry == 0:
#                col_name = ['현재가', '거래량', '거래대금', '일자', '시가', '고가', '저가']
#                self.data_opt10081 = DataFrame(self.data_opt10081, columns=col_name)
#
#        if request_name == "일별주가요청":
#            data = self.get_comm_data_ex(tr_code, "일별주가요청")
#            if data is not None:
#                data = list(map(lambda x: list(map(lambda y: y.replace('+','').replace('--','-'), x)), data))
#                data = list(map(lambda x: list(map(lambda y: float(y) if y != '' else 0, x)), data))
#                self.data_opt10086.extend(data)
#                date = str(int(data[0][0]))
#                dt = datetime.strptime(date, "%Y%m%d")
##                if dt <= self.start_date:
##                    self.inquiry = 0
#            if inquiry == "0" or self.inquiry == 0:
#                col_name = ['일자', '시가', '고가', '저가', '종가', '전일비', '등락률', '거래량', '금액(백만)', '신용비', '개인',
#                            '기관', '외인수량', '외국계', '프로그램', '외인비', '체결강도', '외인보유', '외인비중', '외인순매수',
#                            '기관순매수', '개인순매수', '신용잔고율']
#                self.data_opt10086 = DataFrame(self.data_opt10086, columns=col_name)
#
#        if request_name == "예수금상세현황요청":
#            estimate_day2_deposit = self.comm_get_data(tr_code, "", request_name, 0, "d+2추정예수금")
#            estimate_day2_deposit = self.change_format(estimate_day2_deposit)
#            self.data_opw00001 = estimate_day2_deposit
#
#        if request_name == '계좌평가잔고내역요청':
#            # 계좌 평가 정보
#            account_evaluation = []
#            key_list = ["총매입금액", "총평가금액", "총평가손익금액", "총수익률(%)", "추정예탁자산"]
#
#            for key in key_list:
#                value = self.comm_get_data(tr_code, "", request_name, 0, key)
#
#                if key.startswith("총수익률"):
#                    value = self.change_format(value, 1)
#                else:
#                    value = self.change_format(value)
#                account_evaluation.append(value)
#            self.data_opw00018['account_evaluation'] = account_evaluation
#
#            # 보유 종목 정보
#            cnt = self.get_repeat_cnt(tr_code, request_name)
#            key_list = ["종목명", "보유수량", "매입가", "현재가", "평가손익", "수익률(%)", "종목번호"]
#            for i in range(cnt):
#                stock = []
#                for key in key_list:
#                    value = self.comm_get_data(tr_code, "", request_name, i, key)
#                    if key.startswith("수익률"):
#                        value = self.change_format(value, 2)
#                    elif key != "종목명" and key != "종목번호":
#                        value = self.change_format(value)
#                    stock.append(value)
#                self.data_opw00018['stocks'].append(stock)
        
    
    ###############################################################
    # 메서드 정의: 실시간 데이터 처리 관련 메서드                           #
    ###############################################################

    def disconnect_real_data(self, screen_no):
        """
        해당 화면번호로 설정한 모든 실시간 데이터 요청을 제거합니다.

        화면을 종료할 때 반드시 이 메서드를 호출해야 합니다.

        :param screen_no: string
        """

        if not self.get_connect_state():
            raise KiwoomConnectError()

        if not isinstance(screen_no, str):
            raise ParameterTypeError()

        self.dynamicCall("DisconnectRealData(QString)", screen_no)

    def get_comm_real_data(self, code, fid):
        """
        실시간 데이터 획득 메서드

        이 메서드는 반드시 receiveRealData() 이벤트 메서드가 호출될 때, 그 안에서 사용해야 합니다.

        :param code: string - 종목코드
        :param fid: - 실시간 타입에 포함된 fid
        :return: string - fid에 해당하는 데이터
        """

        if not (isinstance(code, str)
                and isinstance(fid, int)):
            raise ParameterTypeError()

        value = self.dynamicCall("GetCommRealData(QString, int)", code, fid)

        return value

    def set_real_reg(self, screen_no, codes, fids, real_reg_type):
        """
        실시간 데이터 요청 메서드

        종목코드와 fid 리스트를 이용해서 실시간 데이터를 요청하는 메서드입니다.
        한번에 등록 가능한 종목과 fid 갯수는 100종목, 100개의 fid 입니다.
        실시간등록타입을 0으로 설정하면, 첫 실시간 데이터 요청을 의미하며
        실시간등록타입을 1로 설정하면, 추가등록을 의미합니다.

        실시간 데이터는 실시간 타입 단위로 receiveRealData() 이벤트로 전달되기 때문에,
        이 메서드에서 지정하지 않은 fid 일지라도, 실시간 타입에 포함되어 있다면, 데이터 수신이 가능하다.

        :param screen_no: string
        :param codes: string - 종목코드 리스트(종목코드;종목코드;...)
        :param fids: string - fid 리스트(fid;fid;...)
        :param real_reg_type: string - 실시간등록타입(0: 첫 등록, 1: 추가 등록)
        """

        if not self.get_connect_state():
            raise KiwoomConnectError()

        if not (isinstance(screen_no, str)
                and isinstance(codes, str)
                and isinstance(fids, str)
                and isinstance(real_reg_type, str)):
            raise ParameterTypeError()

        self.dynamicCall("SetRealReg(QString, QString, QString, QString)",
                         screen_no, codes, fids, real_reg_type)

    def set_real_remove(self, screen_no, code):
        """
        실시간 데이터 중지 메서드

        set_real_reg() 메서드로 등록한 종목만, 이 메서드를 통해 실시간 데이터 받기를 중지 시킬 수 있습니다.

        :param screen_no: string - 화면번호 또는 ALL 키워드 사용가능
        :param code: string - 종목코드 또는 ALL 키워드 사용가능
        """

        if not self.get_connect_state():
            raise KiwoomConnectError()

        if not (isinstance(screen_no, str)
                and isinstance(code, str)):
            raise ParameterTypeError()

        self.dynamicCall("SetRealRemove(QString, QString)", screen_no, code)

    def receive_real_data(self, code, real_type, real_data):
        """
        실시간 데이터 수신 이벤트

        실시간 데이터를 수신할 때 마다 호출되며,
        set_real_reg() 메서드로 등록한 실시간 데이터도 이 이벤트 메서드에 전달됩니다.
        get_comm_real_data() 메서드를 이용해서 실시간 데이터를 얻을 수 있습니다.

        :param code: string - 종목코드
        :param real_type: string - 실시간 타입(KOA의 실시간 목록 참조)
        :param real_data: string - 실시간 데이터 전문
        """

        try:
            self.log.debug("[receiveRealData]")
            self.log.debug("({})".format(real_type))

            if real_type not in RealType.REALTYPE:
                return

            data = []

            if code != "":
                data.append(code)
                codeOrNot = code
            else:
                codeOrNot = real_type

            for fid in sorted(RealType.REALTYPE[real_type].keys()):
                value = self.get_comm_real_data(codeOrNot, fid)
                data.append(value)

            # TODO: DB에 저장
            self.log.debug(data)

        except Exception as e:
            self.log.error('{}'.format(e))












