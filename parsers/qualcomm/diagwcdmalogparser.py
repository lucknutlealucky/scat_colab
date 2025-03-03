#!/usr/bin/env python3

import util

import struct
import calendar
import logging
import math
from collections import namedtuple
import binascii

class DiagWcdmaLogParser:
    def __init__(self, parent):
        self.parent = parent
        self.process = {
            # WCDMA Layer 1
            0x4005: lambda x, y, z: self.parse_wcdma_search_cell_reselection(x, y, z), # WCDMA Search Cell Reselection Rank
            #0x4179 WCDMA PN Search Edition 2
            # 05 00 01 94 FE 00 02 00 02 00 02 00 FE 00 FE 00 A7 29 FF FF FF FF FF FF 00 00 01 04 01 23 00 00 CB 69 D0 18 C0 00 00 00 00 00 00 00 00 00 00 00 00 00 00 5C 51 03 00 AC 4F 03 00 F8 52 03 00 24 51 03 00 18 54 03 00 04 54 03 00 08 02 00 00 78 00 00 00 78 00 00 00 74 00 00 00 71 00 00 00 70 00 00 00
            # 05 00 01 74 FE 00 02 00 02 00 02 00 FE 00 FE 00 A7 29 FF FF FF FF FF FF 00 00 02 04 01 23 00 00 CB 69 D0 18 C0 00 04 01 23 00 00 56 5C 50 12 C0 00 04 00 00 00 00 00 00 00 00 00 00 00 00 5C 51 03 00 48 4F 03 00 88 4E 03 00 4C 51 03 00 2C 52 03 00 6C 52 03 00 BE 03 00 00 86 00 00 00 7E 00 00 00 75 00 00 00 6F 00 00 00 6F 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 B8 E5 02 00 3C E6 02 00 24 E8 02 00 08 E3 02 00 9C E3 02 00 80 E5 02 00 98 02 00 00 7F 00 00 00 78 00 00 00 77 00 00 00 77 00 00 00 76 00 00 00
            #0x41B0 WCDMA Freq Scan
            # 01 03 1E FE 01 A3 FF A7 29

            # WCDMA Layer 2
            0x4135: lambda x, y, z: self.parse_wcdma_rlc_dl_am_signaling_pdu(x, y, z), # WCDMA RLC DL AM Signaling PDU
            0x413C: lambda x, y, z: self.parse_wcdma_rlc_ul_am_signaling_pdu(x, y, z), # WCDMA RLC UL AM Signaling PDU
            0x4145: lambda x, y, z: self.parse_wcdma_rlc_ul_am_control_pdu_log(x, y, z), # WCDMA RLC UL AM Control PDU Log
            0x4146: lambda x, y, z: self.parse_wcdma_rlc_dl_am_control_pdu_log(x, y, z), # WCDMA RLC DL AM Control PDU Log
            0x4168: lambda x, y, z: self.parse_wcdma_rlc_dl_pdu_cipher_packet(x, y, z), # WCDMA RLC DL PDU Cipher Packet
            0x4169: lambda x, y, z: self.parse_wcdma_rlc_ul_pdu_cipher_packet(x, y, z), # WCDMA RLC UL PDU Cipher Packet

            # WCDMA RRC
            0x4127: lambda x, y, z: self.parse_wcdma_cell_id(x, y, z), # WCDMA Cell ID
            0x412F: lambda x, y, z: self.parse_wcdma_rrc(x, y, z), # WCDMA Signaling Messages
        }

    def get_real_rscp(self, rscp):
        return rscp - 21

    def get_real_ecio(self, ecio):
        return ecio / 2

    # WCDMA Layer 1
    def parse_wcdma_search_cell_reselection(self, pkt_header, pkt_body, args):
        pkt_version = (pkt_body[0] >> 6) # upper 2b
        num_wcdma_cells = pkt_body[0] & 0x3f # lower 6b
        num_gsm_cells = pkt_body[1] & 0x3f # lower 6b
        stdout = ''

        cell_search_v0_3g = namedtuple('QcDiagWcdmaSearchCellReselectionV03G',
            'uarfcn psc rscp rank_rscp ecio rank_ecio')
        cell_search_v0_2g = namedtuple('QcDiagWcdmaSearchCellReselectionV02G',
            'arfcn bsic rssi rank')
        cell_search_v1_3g = namedtuple('QcDiagWcdmaSearchCellReselectionV13G',
            'uarfcn psc rscp rank_rscp ecio rank_ecio resel_status')
        cell_search_v1_2g = namedtuple('QcDiagWcdmaSearchCellReselectionV12G',
            'arfcn bsic rssi rank resel_status')
        cell_search_v2_3g = namedtuple('WcdmaSearchCellReselectionV23G',
            'uarfcn psc rscp rank_rscp ecio rank_ecio resel_status hcs_priority h_value hcs_cell_qualify')
        cell_search_v2_2g = namedtuple('WcdmaSearchCellReselectionV22G',
            'arfcn bsic rssi rank resel_status hcs_priority h_value hcs_cell_qualify')

        if pkt_version not in (0, 1, 2):
            self.parent.logger.log(logging.WARNING, 'Unsupported WCDMA search cell reselection version {}'.format(pkt_version))
            self.parent.logger.log(logging.DEBUG, util.xxd(pkt_body))
            return None

        stdout += 'WCDMA Search Cell: {} 3G cells, {} 2G cells\n'.format(num_wcdma_cells, num_gsm_cells)
        pos = 2
        if pkt_version == 2:
            pos += 5

        for i in range(num_wcdma_cells):
            if pkt_version == 0:
                cell_3g = cell_search_v0_3g._make(struct.unpack('<HHbhbh', pkt_body[pos:pos+10]))
                pos += 10
            elif pkt_version == 1:
                cell_3g = cell_search_v1_3g._make(struct.unpack('<HHbhbhb', pkt_body[pos:pos+11]))
                pos += 11
            elif pkt_version == 2:
                cell_3g = cell_search_v2_3g._make(struct.unpack('<HHbhbhbhhb', pkt_body[pos:pos+16]))
                pos += 16

            stdout += 'WCDMA Search Cell: 3G Cell {}: UARFCN {}, PSC {:3d}, RSCP {}, Ec/Io {:.2f}\n'.format(i,
                    cell_3g.uarfcn, cell_3g.psc,
                    self.get_real_rscp(cell_3g.rscp), self.get_real_ecio(cell_3g.ecio))

        for i in range(num_gsm_cells):
            if pkt_version == 0:
                cell_2g = cell_search_v0_2g._make(struct.unpack('<HHbh', pkt_body[pos:pos+7]))
                pos += 7
            elif pkt_version == 1:
                cell_2g = cell_search_v1_2g._make(struct.unpack('<HHbhb', pkt_body[pos:pos+8]))
                pos += 8
            elif pkt_version == 2:
                cell_2g = cell_search_v2_2g._make(struct.unpack('<HHbhbhhb', pkt_body[pos:pos+13]))
                pos += 13

            stdout += 'WCDMA Search Cell: 2G Cell {}: ARFCN {}, RSSI {:.2f}, Rank {}'.format(i,
                    cell_2g.arfcn & 0xfff, cell_2g.rssi, cell_2g.rank)

        return {'stdout': stdout.rstrip()}

    # WCDMA Layer 2
    def parse_wcdma_rlc_dl_am_signaling_pdu(self, pkt_header, pkt_body, args):
        pkt_ts = util.parse_qxdm_ts(pkt_header.timestamp)
        item_struct = namedtuple('QcDiagWcdmaRlcDlAmSignalingPdu', 'lcid pdu_count pdu_size')
        num_packets = pkt_body[0]
        packets = []

        pos = 1
        for x in range(num_packets):
            item = item_struct._make(struct.unpack('<BHH', pkt_body[pos:pos+5]))
            pos += 5
            actual_pdu_size = min(math.ceil(item.pdu_size / 8), len(pkt_body) - pos)
            rlc_pdu = pkt_body[pos:pos+actual_pdu_size]
            pos += actual_pdu_size

            # Directly pack RLC PDU on UDP packet, see epan/packet-umts_rlc-lte.h of Wireshark
            # Has header on PDU, CP (0x01), no ROHC
            # Direction: Downlink (0x01)
            ws_hdr = struct.pack('!BBBBB',
                util.wcdma_rlc_tags.RLC_MODE_TAG,
                util.wcdma_rlc_mode_types.RLC_AM,
                util.wcdma_rlc_tags.RLC_DIRECTION_TAG,
                util.wcdma_rlc_direction_types.DIRECTION_DOWNLINK,
                util.wcdma_rlc_tags.RLC_PAYLOAD_TAG)

            packets.append(b'umts-rlc' + ws_hdr + rlc_pdu)

        return {'up': packets, 'ts': pkt_ts}

    def parse_wcdma_rlc_ul_am_signaling_pdu(self, pkt_header, pkt_body, args):
        print('WCDMARLCAMUL ' + binascii.hexlify(pkt_body).decode('utf-8'))

    def parse_wcdma_rlc_dl_am_control_pdu_log(self, pkt_header, pkt_body, args):
        pkt_ts = util.parse_qxdm_ts(pkt_header.timestamp)
        lcid, pdu_size = struct.unpack('<BH', pkt_body[0:3])
        rlc_pdu = pkt_body[3:3+pdu_size]
        # rlc_pdu = pkt_body[3:]

        # Directly pack RLC PDU on UDP packet, see epan/packet-umts_rlc-lte.h of Wireshark
        # Has header on PDU, CP (0x01), no ROHC
        # Direction: Downlink (0x01)
        ws_hdr = struct.pack('!BBBBB',
            util.wcdma_rlc_tags.RLC_MODE_TAG,
            util.wcdma_rlc_mode_types.RLC_AM,
            util.wcdma_rlc_tags.RLC_DIRECTION_TAG,
            util.wcdma_rlc_direction_types.DIRECTION_DOWNLINK,
            util.wcdma_rlc_tags.RLC_PAYLOAD_TAG)

        return {'up': [b'umts-rlc' + ws_hdr + rlc_pdu], 'ts': pkt_ts}

    def parse_wcdma_rlc_ul_am_control_pdu_log(self, pkt_header, pkt_body, args):
        pkt_ts = util.parse_qxdm_ts(pkt_header.timestamp)
        lcid, pdu_size = struct.unpack('<BH', pkt_body[0:3])
        rlc_pdu = pkt_body[3:3+pdu_size]
        # rlc_pdu = pkt_body[3:]

        # Directly pack RLC PDU on UDP packet, see epan/packet-umts_rlc-lte.h of Wireshark
        # Has header on PDU, CP (0x01), no ROHC
        # Direction: Downlink (0x01)
        ws_hdr = struct.pack('!BBBBB',
            util.wcdma_rlc_tags.RLC_MODE_TAG,
            util.wcdma_rlc_mode_types.RLC_AM,
            util.wcdma_rlc_tags.RLC_DIRECTION_TAG,
            util.wcdma_rlc_direction_types.DIRECTION_UPLINK,
            util.wcdma_rlc_tags.RLC_PAYLOAD_TAG)

        return {'up': [b'umts-rlc' + ws_hdr + rlc_pdu], 'ts': pkt_ts}

    def parse_wcdma_rlc_dl_pdu_cipher_packet(self, pkt_header, pkt_body, args):
        num_packets = struct.unpack('<H', pkt_body[0:2])[0]
        pos = 2
        stdout = ''
        item_struct = namedtuple('QcDiagWcdmaDlRlcCipherPdu', 'rlc_id ck ciph_alg ciph_msg count_c')

        for x in range(num_packets):
            item = item_struct._make(struct.unpack('<BLBLL', pkt_body[pos:pos+14]))
            pos += 14
            if item.ciph_alg == 0xff:
                continue
            stdout += "WCDMA RLC Cipher DL PDU: LCID: {}, CK = {:#x}, Algorithm = UEA{}, Message = {:#x}, Count C = 0x{:x}\n".format(item.rlc_id,
                item.ck, item.ciph_alg, item.ciph_msg, item.count_c)

        return {'stdout': stdout.rstrip()}

    def parse_wcdma_rlc_ul_pdu_cipher_packet(self, pkt_header, pkt_body, args):
        num_packets = struct.unpack('<H', pkt_body[0:2])[0]
        pos = 2
        stdout = ''
        item_struct = namedtuple('QcDiagWcdmaUlRlcCipherPdu', 'rlc_id ck ciph_alg count_c')

        for x in range(num_packets):
            item = item_struct._make(struct.unpack('<BLBL', pkt_body[pos:pos+10]))
            pos += 10
            if item.ciph_alg == 0xff:
                continue
            stdout += "WCDMA RLC Cipher UL PDU: LCID: {}, CK = {:#x}, Algorithm = UEA{}, Count C = 0x{:x}\n".format(item.rlc_id,
                item.ck, item.ciph_alg, item.count_c)

        return {'stdout': stdout.rstrip()}

    # WCDMA RRC
    def parse_wcdma_cell_id(self, pkt_header, pkt_body, args):
        radio_id = 0
        if args is not None and 'radio_id' in args:
            radio_id = args['radio_id']
        item_struct = namedtuple('QcDiagWcdmaRrcCellId', 'ul_uarfcn dl_uarfcn cell_id ura_id flags access psc mcc mnc lac rac')
        if len(pkt_body) < 32:
            pkt_body += b'\x00' * (32 - len(pkt_body))
        item = item_struct._make(struct.unpack('<LL LH BB H 3s 3s LL', pkt_body[0:32]))

        psc = item.psc >> 4
        # UARFCN UL, UARFCN DL, CID, URA_ID, FLAGS, PSC, PLMN_ID, LAC, RAC
        # PSC needs to be >>4'ed
        if self.parent:
            self.parent.umts_last_uarfcn_ul[radio_id] = item.ul_uarfcn
            self.parent.umts_last_uarfcn_dl[radio_id] = item.dl_uarfcn
            self.parent.umts_last_cell_id[radio_id] = psc
        return {'stdout': 'WCDMA Cell ID: UARFCN {}/{}, PSC {}, xCID/xLAC/xRAC {:x}/{:x}/{:x}, MCC {}, MNC {}'.format(item.dl_uarfcn,
            item.ul_uarfcn, psc, item.cell_id, item.lac, item.rac,
            binascii.hexlify(item.mcc).decode('utf-8'), binascii.hexlify(item.mnc).decode('utf-8'))}

    def parse_wcdma_rrc(self, pkt_header, pkt_body, args):
        item_struct = namedtuple('QcDiagWcdmaRrcOtaPacket', 'channel_type rbid len')
        item = item_struct._make(struct.unpack('<BBH', pkt_body[0:4]))
        msg_content = b''
        radio_id = 0
        if args is not None and 'radio_id' in args:
            radio_id = args['radio_id']

        channel_type_map = {
            0: util.gsmtap_umts_rrc_types.UL_CCCH,
            1: util.gsmtap_umts_rrc_types.UL_DCCH,
            2: util.gsmtap_umts_rrc_types.DL_CCCH,
            3: util.gsmtap_umts_rrc_types.DL_DCCH,
            4: util.gsmtap_umts_rrc_types.BCCH_BCH, # Encoded
            5: util.gsmtap_umts_rrc_types.BCCH_FACH, # Encoded
            6: util.gsmtap_umts_rrc_types.PCCH,
            7: util.gsmtap_umts_rrc_types.MCCH,
            8: util.gsmtap_umts_rrc_types.MSCH,
            10: util.gsmtap_umts_rrc_types.System_Information_Container,
        }

        channel_type_map_extended_type = {
            9: util.gsmtap_umts_rrc_types.BCCH_BCH, # Extension SIBs
            0xFE: util.gsmtap_umts_rrc_types.BCCH_BCH, # Decoded
            0xFF: util.gsmtap_umts_rrc_types.BCCH_FACH # Decoded
        }

        sib_type_map = {
            0: util.gsmtap_umts_rrc_types.MasterInformationBlock,
            1: util.gsmtap_umts_rrc_types.SysInfoType1,
            2: util.gsmtap_umts_rrc_types.SysInfoType2,
            3: util.gsmtap_umts_rrc_types.SysInfoType3,
            4: util.gsmtap_umts_rrc_types.SysInfoType4,
            5: util.gsmtap_umts_rrc_types.SysInfoType5,
            6: util.gsmtap_umts_rrc_types.SysInfoType6,
            7: util.gsmtap_umts_rrc_types.SysInfoType7,
            8: util.gsmtap_umts_rrc_types.SysInfoType8,
            9: util.gsmtap_umts_rrc_types.SysInfoType9,
            10: util.gsmtap_umts_rrc_types.SysInfoType10,
            11: util.gsmtap_umts_rrc_types.SysInfoType11,
            12: util.gsmtap_umts_rrc_types.SysInfoType12,
            13: util.gsmtap_umts_rrc_types.SysInfoType13,
            14: util.gsmtap_umts_rrc_types.SysInfoType13_1,
            15: util.gsmtap_umts_rrc_types.SysInfoType13_2,
            16: util.gsmtap_umts_rrc_types.SysInfoType13_3,
            17: util.gsmtap_umts_rrc_types.SysInfoType13_4,
            18: util.gsmtap_umts_rrc_types.SysInfoType14,
            19: util.gsmtap_umts_rrc_types.SysInfoType15,
            20: util.gsmtap_umts_rrc_types.SysInfoType15_1,
            21: util.gsmtap_umts_rrc_types.SysInfoType15_2,
            22: util.gsmtap_umts_rrc_types.SysInfoType15_3,
            23: util.gsmtap_umts_rrc_types.SysInfoType16,
            24: util.gsmtap_umts_rrc_types.SysInfoType17,
            25: util.gsmtap_umts_rrc_types.SysInfoType15_4,
            26: util.gsmtap_umts_rrc_types.SysInfoType18,
            27: util.gsmtap_umts_rrc_types.SysInfoTypeSB1,
            28: util.gsmtap_umts_rrc_types.SysInfoTypeSB2,
            29: util.gsmtap_umts_rrc_types.SysInfoType15_5,
            30: util.gsmtap_umts_rrc_types.SysInfoType5bis,
            31: util.gsmtap_umts_rrc_types.SysInfoType11bis,
            # Extension SIB
            66: util.gsmtap_umts_rrc_types.SysInfoType11bis,
            67: util.gsmtap_umts_rrc_types.SysInfoType19
        }

        channel_type_map_new = {
            0x80: util.gsmtap_umts_rrc_types.UL_CCCH,
            0x81: util.gsmtap_umts_rrc_types.UL_DCCH,
            0x82: util.gsmtap_umts_rrc_types.DL_CCCH,
            0x83: util.gsmtap_umts_rrc_types.DL_DCCH,
            0x84: util.gsmtap_umts_rrc_types.BCCH_BCH, # Encoded
            0x85: util.gsmtap_umts_rrc_types.BCCH_FACH, # Encoded
            0x86: util.gsmtap_umts_rrc_types.PCCH,
            0x87: util.gsmtap_umts_rrc_types.MCCH,
            0x88: util.gsmtap_umts_rrc_types.MSCH,
        }
        channel_type_map_new_extended_type = {
            0x89: util.gsmtap_umts_rrc_types.BCCH_BCH, # Extension SIBs
            0xF0: util.gsmtap_umts_rrc_types.BCCH_BCH, # Decoded
        }
        sib_type_map_new = {
            0: util.gsmtap_umts_rrc_types.MasterInformationBlock,
            1: util.gsmtap_umts_rrc_types.SysInfoType1,
            2: util.gsmtap_umts_rrc_types.SysInfoType2,
            3: util.gsmtap_umts_rrc_types.SysInfoType3,
            4: util.gsmtap_umts_rrc_types.SysInfoType4,
            5: util.gsmtap_umts_rrc_types.SysInfoType5,
            6: util.gsmtap_umts_rrc_types.SysInfoType6,
            7: util.gsmtap_umts_rrc_types.SysInfoType7,
            8: util.gsmtap_umts_rrc_types.SysInfoType8,
            9: util.gsmtap_umts_rrc_types.SysInfoType9,
            10: util.gsmtap_umts_rrc_types.SysInfoType10,
            11: util.gsmtap_umts_rrc_types.SysInfoType11,
            12: util.gsmtap_umts_rrc_types.SysInfoType12,
            13: util.gsmtap_umts_rrc_types.SysInfoType13,
            14: util.gsmtap_umts_rrc_types.SysInfoType13_1,
            15: util.gsmtap_umts_rrc_types.SysInfoType13_2,
            16: util.gsmtap_umts_rrc_types.SysInfoType13_3,
            17: util.gsmtap_umts_rrc_types.SysInfoType13_4,
            18: util.gsmtap_umts_rrc_types.SysInfoType14,
            19: util.gsmtap_umts_rrc_types.SysInfoType15,
            20: util.gsmtap_umts_rrc_types.SysInfoType15_1,
            21: util.gsmtap_umts_rrc_types.SysInfoType15_2,
            22: util.gsmtap_umts_rrc_types.SysInfoType15_3,
            23: util.gsmtap_umts_rrc_types.SysInfoType16,
            24: util.gsmtap_umts_rrc_types.SysInfoType17,
            25: util.gsmtap_umts_rrc_types.SysInfoType15_4,
            26: util.gsmtap_umts_rrc_types.SysInfoType18,
            27: util.gsmtap_umts_rrc_types.SysInfoTypeSB1,
            28: util.gsmtap_umts_rrc_types.SysInfoTypeSB2,
            29: util.gsmtap_umts_rrc_types.SysInfoType15_5,
            30: util.gsmtap_umts_rrc_types.SysInfoType5bis,
            31: util.gsmtap_umts_rrc_types.SysInfoType19,
            # Extension SIB
            66: util.gsmtap_umts_rrc_types.SysInfoType11bis,
            67: util.gsmtap_umts_rrc_types.SysInfoType19
        }

        if item.channel_type in channel_type_map.keys():
            arfcn = self.parent.umts_last_uarfcn_dl[radio_id]
            if item.channel_type == 0 or item.channel_type == 1:
                arfcn = self.parent.umts_last_uarfcn_ul[radio_id]

            subtype = channel_type_map[item.channel_type]
            msg_content = pkt_body[4:]
        elif item.channel_type in channel_type_map_extended_type.keys():
            arfcn = self.parent.umts_last_uarfcn_dl[radio_id]

            # uint8 subtype, uint8 msg[]
            if pkt_body[4] in sib_type_map.keys():
                subtype = sib_type_map[pkt_body[4]]
                msg_content = pkt_body[5:]
            else:
                self.parent.logger.log(logging.WARNING, "Unknown WCDMA SIB Class {}".format(pkt_body[4]))
                return None
        elif item.channel_type in channel_type_map_new.keys():
            # uint16 uarfcn, uint16 psc, uint8 msg[]
            arfcn, psc = struct.unpack('<HH', pkt_body[4:8])

            subtype = channel_type_map_new[item.channel_type]
            msg_content = pkt_body[8:]
        elif item.channel_type in channel_type_map_new_extended_type.keys():
            # uint16 uarfcn, uint16 psc, uint8 subtype, uint8 msg[]
            arfcn, psc = struct.unpack('<HH', pkt_body[4:8])

            if pkt_body[8] in sib_type_map_new.keys():
                subtype = sib_type_map_new[pkt_body[8]]
                msg_content = pkt_body[9:]
            else:
                self.parent.logger.log(logging.WARNING, "Unknown WCDMA new SIB Class {}".format(pkt_body[8]))
                return None
        else:
            self.parent.logger.log(logging.WARNING, "Unknown WCDMA RRC channel type {}".format(pkt_body[0]))
            self.parent.logger.log(logging.DEBUG, util.xxd(pkt_body))
            return None

        pkt_ts = util.parse_qxdm_ts(pkt_header.timestamp)
        ts_sec = calendar.timegm(pkt_ts.timetuple())
        ts_usec = pkt_ts.microsecond

        gsmtap_hdr = util.create_gsmtap_header(
            version = 3,
            payload_type = util.gsmtap_type.UMTS_RRC,
            arfcn = arfcn,
            sub_type = subtype,
            device_sec = ts_sec,
            device_usec = ts_usec)

        return {'cp': [gsmtap_hdr + msg_content], 'ts': pkt_ts}
