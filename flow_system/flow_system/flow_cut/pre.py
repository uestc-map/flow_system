import dpkt
import os
import socket
import csv
from .constants import PRETTY_NAMES


# dataset = "stratosphere"
# dataset = "lastline"
dataset = "non_vpn"
class flow():
    def __init__(self, data):
        self.data = data

def pretty_name(name_type, name_value):
    """Returns the pretty name for type name_type."""
    if name_type in PRETTY_NAMES:
        if name_value in PRETTY_NAMES[name_type]:
            name_value = PRETTY_NAMES[name_type][name_value]
        else:
            name_value = '{0}: unknown value {1}'.format(name_value, name_type)
    else:
        name_value = 'unknown type: {0}'.format(name_type)
    return name_value


def flow_pre_cut(type):

    dir = "/Users/xuhao/研一项目/检测系统/flow_system/flow_system/flow_system/data_raw/"

    for i, filename in enumerate(os.listdir(dir)):
        if 'pcap' in filename: 
            pcap_ana(dir + filename, filename)


def flow_ana(flow_record, type):
    base_path = "/Users/xuhao/研一项目/检测系统/flow_system/flow_system/flow_system/data_cut/"
    if not os.path.exists(base_path):
        os.mkdir(base_path)
    if not os.path.exists(base_path + 'flow/'):
        os.mkdir(base_path + 'flow/')
    if not os.path.exists(base_path + 'tls/'):
        os.mkdir(base_path + 'tls/')
    for key in flow_record:
        flag = False
        for record in flow_record[key]:
            eth = record[0]
            ip = eth.data

            if isinstance(ip.data, dpkt.tcp.TCP) and len(ip.data.data) != 0:
                stream = ip.data.data
                if (stream[0] ==128):
                    flag = True
                    break
                elif stream[0] in {20, 21, 22, 23}:
                    try:
                        records, bytes_used = dpkt.ssl.tls_multi_factory(stream)
                        for rec in records:
                            record_type = pretty_name('tls_record', rec.type)
                            if record_type == 'handshake' and len(rec.data) > 2 and ord(rec.data[:1]) == 1:
                                flag = True
                                break
                    except dpkt.ssl.SSL3Exception as exception:
                        pass
                    

        if flag:
            path = base_path + 'tls/' + str(key)
            test = open(path + ".pcap", "ab")
            writer = dpkt.pcap.Writer(test)
            timestamp = flow_record[key][0][1]

            for record in flow_record[key]:
                eth = record[0]
                timestamp = record[1]
                writer.writepkt(eth, ts=timestamp)
            test.flush()
            test.close()
        else:
            path = base_path + 'flow/' + str(key) 
            test = open(path + ".pcap", "ab")
            writer = dpkt.pcap.Writer(test)
            timestamp = flow_record[key][0][1]

            for record in flow_record[key]:
                eth = record[0]
                timestamp = record[1]
                writer.writepkt(eth, ts=timestamp)
            test.flush()
            test.close()




def pcap_ana(filename, type):
    with open(filename, 'rb') as f:
        try:
            if "pcapng" in filename:
                capture = dpkt.pcapng.Reader(f)
            elif "pcap" in filename:
                capture = dpkt.pcap.Reader(f)
        except ValueError as e:
            # Invalid tcpdump header
            capture = []
            print("wrong:", filename)

        # try:
        #     capture = dpkt.pcap.Reader(f)
        # except:
        #     f.seek(0, 0)
        #     capture = dpkt.pcapng.Reader(f)
        #     # print("wrong:",filename)

        flow_record = {}
        i = 0
        for timestamp, packet in capture:
            i += 1
            eth = dpkt.ethernet.Ethernet(packet)
            ip = eth.data
            try:
                dport = ip.data.dport
                sport = ip.data.sport
                flag = socket.inet_ntoa(ip.src) + '-' + str(sport) + '->' + socket.inet_ntoa(ip.dst) + '-' + str(dport)
                flag_rev = socket.inet_ntoa(ip.dst) + '-' + str(dport) + '->' + socket.inet_ntoa(ip.src) + '-' + str(sport)
                # if dport == 443 or sport == 443:
                if flag in flow_record.keys():
                    flow_record[flag].append([eth, timestamp])
                elif flag_rev in flow_record.keys():
                    flow_record[flag_rev].append([eth, timestamp])
                else:
                    flow_record[flag] = []
                    flow_record[flag].append([eth, timestamp])
            except AttributeError:
                pass
            except:
                pass
        if filename == "AIMchat1.pcapng":
            print("123")
        flow_ana(flow_record, type)