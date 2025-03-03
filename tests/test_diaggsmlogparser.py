#!/usr/bin/env python3

import unittest
import binascii
import datetime
from collections import namedtuple

from parsers.qualcomm.diaggsmlogparser import DiagGsmLogParser

class TestDiagGsmLogParser(unittest.TestCase):
    parser = DiagGsmLogParser(parent=None)
    log_header = namedtuple('QcDiagLogHeader', 'cmd_code reserved length1 length2 log_id timestamp')

    def test_parse_gsm_fcch(self):
        payload = binascii.unhexlify('0c80010000000c853fff3fff00803805')
        result = self.parser.parse_gsm_fcch(None, payload, None)
        expected = {'stdout': 'GSM FCCH acquistion: ARFCN 12/Band 8', 'radio_id': 0}
        self.assertDictEqual(result, expected)

    def test_parse_gsm_sch(self):
        payload = binascii.unhexlify('0c8001000200000000000b00000077b02501789800002b000000be030000')
        result = self.parser.parse_gsm_sch(None, payload, None)
        expected = {'stdout': 'GSM SCH acquistion: ARFCN 12/Band 8, Data: 0000000000111011110110000', 'radio_id': 0}
        self.assertDictEqual(result, expected)

    def test_parse_gsm_l1_burst_metric(self):
        payload = binascii.unhexlify('03c30407002580985c3f0036fb2b0048fe040000008e6e00c4040700258066a8390031fbfe00e2fd02000000af4f0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000ff0000')
        result = self.parser.parse_gsm_l1_burst_metric(None, payload, None)
        expected = {'stdout': 'GSM Serving Cell Burst Metric: ARFCN 37/BC 8, RSSI 4152472, RxPwr -76.62\nGSM Serving Cell Burst Metric: ARFCN 37/BC 8, RSSI 3778662, RxPwr -76.94'}
        self.assertDictEqual(result, expected)

    def test_parse_gsm_l1_new_burst_metric(self):
        payload = binascii.unhexlify('0403c30407002580985c3f0036fb2b0048fe040000008e6e00003ed6a5000000605f0000000000c4040700258066a8390031fbfe00e2fd02000000af4f0000088777000000ad0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000050500000000000ff0000')
        result = self.parser.parse_gsm_l1_new_burst_metric(None, payload, None)
        expected = {'stdout': 'GSM Serving Cell New Burst Metric: ARFCN 37/BC 8, RSSI 4152472, RxPwr -76.62\nGSM Serving Cell New Burst Metric: ARFCN 37/BC 8, RSSI 3778662, RxPwr -76.94'}
        self.assertDictEqual(result, expected)

    def test_parse_gsm_l1_serv_aux_meas(self):
        payload = binascii.unhexlify('34fb00')
        result = self.parser.parse_gsm_l1_serv_aux_meas(None, payload, None)
        expected = {'stdout': 'GSM Serving Cell Aux Measurement: RxPwr -76.75'}
        self.assertDictEqual(result, expected)

    def test_parse_gsm_l1_surround_cell_ba(self):
        payload = binascii.unhexlify('0a048020f900000000000000000a8020f900000000000000000c8020f90000000000000000108020f900000000000000001f8020f900000000000000002a8020f900000000000000002b8020f900000000000000002d8020f900000000000000002f8020f90000000000000000318020f90000000000000000')
        result = self.parser.parse_gsm_l1_surround_cell_ba(None, payload, None)
        expected = {'stdout': 'GSM Surround Cell BA: 10 cells\nGSM Surround Cell BA: Cell 0: ARFCN 4/BC 8/BSIC N/A RxPwr 0.00\nGSM Surround Cell BA: Cell 1: ARFCN 10/BC 8/BSIC N/A RxPwr 0.00\nGSM Surround Cell BA: Cell 2: ARFCN 12/BC 8/BSIC N/A RxPwr 0.00\nGSM Surround Cell BA: Cell 3: ARFCN 16/BC 8/BSIC N/A RxPwr 0.00\nGSM Surround Cell BA: Cell 4: ARFCN 31/BC 8/BSIC N/A RxPwr 0.00\nGSM Surround Cell BA: Cell 5: ARFCN 42/BC 8/BSIC N/A RxPwr 0.00\nGSM Surround Cell BA: Cell 6: ARFCN 43/BC 8/BSIC N/A RxPwr 0.00\nGSM Surround Cell BA: Cell 7: ARFCN 45/BC 8/BSIC N/A RxPwr 0.00\nGSM Surround Cell BA: Cell 8: ARFCN 47/BC 8/BSIC N/A RxPwr 0.00\nGSM Surround Cell BA: Cell 9: ARFCN 49/BC 8/BSIC N/A RxPwr 0.00'}
        self.assertDictEqual(result, expected)

    def test_parse_gsm_l1_neig_aux_meas(self):
        payload = binascii.unhexlify('062a806cf9318058f92b805df92d805df92f805cf90c80dcf8')
        result = self.parser.parse_gsm_l1_neig_aux_meas(None, payload, None)
        expected = {'stdout': 'GSM Neighbor Cell Aux: 6 cells\nGSM Neighbor Cell Aux 0: ARFCN 42/BC 8, RxPwr -105.25\nGSM Neighbor Cell Aux 1: ARFCN 49/BC 8, RxPwr -106.50\nGSM Neighbor Cell Aux 2: ARFCN 43/BC 8, RxPwr -106.19\nGSM Neighbor Cell Aux 3: ARFCN 45/BC 8, RxPwr -106.19\nGSM Neighbor Cell Aux 4: ARFCN 47/BC 8, RxPwr -106.25\nGSM Neighbor Cell Aux 5: ARFCN 12/BC 8, RxPwr -114.25'}
        self.assertDictEqual(result, expected)

        payload = binascii.unhexlify('030a80fff80c8019f910800af9')
        result = self.parser.parse_gsm_l1_neig_aux_meas(None, payload, None)
        expected = {'stdout': 'GSM Neighbor Cell Aux: 3 cells\nGSM Neighbor Cell Aux 0: ARFCN 10/BC 8, RxPwr -112.06\nGSM Neighbor Cell Aux 1: ARFCN 12/BC 8, RxPwr -110.44\nGSM Neighbor Cell Aux 2: ARFCN 16/BC 8, RxPwr -111.38'}
        self.assertDictEqual(result, expected)

    def test_parse_gsm_rr_msg(self):
        payload = binascii.unhexlify('811b1749061b761762f2200141c8010a156544b800004e072b2b')
        pkt_header = self.log_header(cmd_code=0x10, reserved=0, length1=len(payload) + 12, length2=len(payload) + 12, log_id=0x512f, timestamp=0)
        result = self.parser.parse_gsm_rr(pkt_header, payload, None)
        expected = {'cp': [binascii.unhexlify('030701000000000000000000010000000000000012d53d800000000049061b761762f2200141c8010a156544b800004e072b2b')],
            'ts': datetime.datetime(1980, 1, 6, 0, 0),
            'radio_id': 0}
        self.assertDictEqual(result, expected)

        payload = binascii.unhexlify('833f1731063f100f707c7f502601010f4f3112050480e02b2b2b')
        pkt_header = self.log_header(cmd_code=0x10, reserved=0, length1=len(payload) + 12, length2=len(payload) + 12, log_id=0x512f, timestamp=0)
        result = self.parser.parse_gsm_rr(pkt_header, payload, None)
        expected = {'cp': [binascii.unhexlify('030701000000000000000000020000000000000012d53d800000000031063f100f707c7f502601010f4f3112050480e02b2b2b')],
            'ts': datetime.datetime(1980, 1, 6, 0, 0),
            'radio_id': 0}
        self.assertDictEqual(result, expected)

        payload = binascii.unhexlify('8321171506210001f02b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b')
        pkt_header = self.log_header(cmd_code=0x10, reserved=0, length1=len(payload) + 12, length2=len(payload) + 12, log_id=0x512f, timestamp=0)
        result = self.parser.parse_gsm_rr(pkt_header, payload, None)
        expected = {'cp': [binascii.unhexlify('030701000000000000000000020000000000000012d53d80000000001506210001f02b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b2b')],
            'ts': datetime.datetime(1980, 1, 6, 0, 0),
            'radio_id': 0}
        self.assertDictEqual(result, expected)

        payload = binascii.unhexlify('81071705060764a0312aa5d047fbfe01ff04332b2b2b2b2b2b2b')
        pkt_header = self.log_header(cmd_code=0x10, reserved=0, length1=len(payload) + 12, length2=len(payload) + 12, log_id=0x512f, timestamp=0)
        result = self.parser.parse_gsm_rr(pkt_header, payload, None)
        expected = {'cp': [binascii.unhexlify('030701000000000000000000010000000000000012d53d800000000005060764a0312aa5d047fbfe01ff04332b2b2b2b2b2b2b')],
            'ts': datetime.datetime(1980, 1, 6, 0, 0),
            'radio_id': 0}
        self.assertDictEqual(result, expected)

    def test_parse_gsm_cell_info(self):
        payload = binascii.unhexlify('10800401187662f220014100ff')
        result = self.parser.parse_gsm_cell_info(None, payload, None)
        expected = {'stdout': 'GSM RR Cell Info: ARFCN 16/Band 8, BCC 4, NCC 1, xCID 7618, xLAI 62f2200141'}
        self.assertDictEqual(result, expected)

        payload = binascii.unhexlify('df830304dff362f23056040088')
        result = self.parser.parse_gsm_cell_info(None, payload, None)
        expected = {'stdout': 'GSM RR Cell Info: ARFCN 991/Band 8, BCC 3, NCC 4, xCID f3df, xLAI 62f2305604'}
        self.assertDictEqual(result, expected)

        payload = binascii.unhexlify('25800303177662f220014100ff')
        result = self.parser.parse_gsm_cell_info(None, payload, None)
        expected = {'stdout': 'GSM RR Cell Info: ARFCN 37/Band 8, BCC 3, NCC 3, xCID 7617, xLAI 62f2200141'}
        self.assertDictEqual(result, expected)

if __name__ == '__main__':
    unittest.main()