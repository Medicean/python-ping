#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Author:Medici.Yan
import os
import argparse
import socket
import struct
import time


def checksum(data):
    s = 0
    n = len(data) % 2
    for i in range(0, len(data) - n, 2):
        s += (ord(data[i]) << 8) + (ord(data[i + 1]))
    if n:
        s += (ord(data[i + 1]) << 8)
    while (s >> 16):
        s = (s & 0xFFFF) + (s >> 16)
    s = ~s & 0xFFFF
    return s


def sendOnePing(seq, dest_addr, ttl, timeout=2, packetsize=64):
    if packetsize:
        ICMP_LEN_BYTES = packetsize
    else:
        ICMP_LEN_BYTES = 64

    socket.setdefaulttimeout(timeout)
    try:
        icmp = socket.getprotobyname('icmp')
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
    except socket.error, (errno, msg):
        if errno == 1:
            msg = "%s : running as root" % msg
            raise socket.error(msg)

    ICMP_ECHO_REQUEST = 8
    ICMP_CODE = 0
    ICMP_ID = os.getpid() & 0xFFFF
    ICMP_CHECKSUM = 0
    ICMP_SEQ = seq

    dest_addr = socket.gethostbyname(dest_addr)
    # 1字节类型 1字节代码 2字节checksum 2字节标识符 2字节序号
    header = struct.pack(
        "bbHHh", ICMP_ECHO_REQUEST,
        ICMP_CODE, ICMP_CHECKSUM, ICMP_ID, ICMP_SEQ)
    bytesInDouble = struct.calcsize("d")
    data = "%s%s" % (
        "Medici.Yan", (
            ICMP_LEN_BYTES - len('Medici.Yan') - bytesInDouble) * "M")
    data = struct.pack("d", time.time()) + data

    ICMP_CHECKSUM = checksum(header + data)

    header = struct.pack(
        "bbHHh", ICMP_ECHO_REQUEST, ICMP_CODE,
        socket.htons(ICMP_CHECKSUM), ICMP_ID, ICMP_SEQ)

    packet = header + data

    s.sendto(packet, (dest_addr, 0))

    while True:
        try:
            recPacket, addr = s.recvfrom(1024)
            timeReceived = time.time()
            icmpHeader = recPacket[20:28]
            _type, _code, _checksum, _packetID, _sequence = struct.unpack(
                'bbHHh', icmpHeader)
            if _packetID == ICMP_ID:
                _ttl = struct.unpack("B", recPacket[8])[0]
                timeSent = struct.unpack(
                    "d", recPacket[28:28 + bytesInDouble])[0]
                delay = (timeReceived - timeSent) * 1000
                print (
                    "%d Bytes from %s : icmp_seq=%d ttl=%d time=%0.4fms"
                    % (len(recPacket)-28, addr[0], ICMP_SEQ, _ttl, delay))
                time.sleep(1)
                return delay
        except socket.timeout:
            print "Request timeout for icmp_seq %d" % (ICMP_SEQ)
            return False
        except Exception, e:
            raise e


def ping(conf):
    count = conf['count']
    ttl = conf['ttl']
    host = conf['host']
    packetsize = conf['packetsize']
    timeout = conf['timeout']
    dest_addr = socket.gethostbyname(host)
    if not packetsize or packetsize < 11:
        packetsize = 64
    if not count:
        count = 3
    if not timeout:
        timeout = 2
    print "PING %s(%s): %s data bytes" % (host, dest_addr, packetsize)
    result = []
    try:
        for i in range(count):
            delay = sendOnePing(
                seq=i, dest_addr=dest_addr, ttl=ttl,
                timeout=timeout, packetsize=packetsize)
            result.append(delay)
    except:
        pass
    finally:
        statisticPing(result, host)


def statisticPing(result, host):
    ping_count = len(result)
    failnum = result.count(False)
    max_time = 0
    min_time = 0
    ave_time = 0
    lostdegree = 0
    for i in range(failnum):
        result.remove(False)
    if result:
        max_time = max(result)
        min_time = min(result)
        ave_time = sum(result) / (ping_count - failnum)
    res = "--- %s ping statistics ---\n"
    res = res + "%d packets transmitted, %d packets received, %0.1f%% "
    res = res + "packet loss\nround-trip min/avg/max = %0.4f/%0.4f/%0.4f ms"
    
    if ping_count != 0:
        lostdegree = (1.0 * failnum / ping_count) * 100
    print res % (
        host, ping_count, (ping_count - failnum), lostdegree,
        min_time, ave_time, max_time)


def parseCmdOptions():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter, add_help=False)
    parser.add_argument(
        "-h", "--help", action="help", help="Show help message and exit")
    parser.add_argument(
        "--version", action="version",
        version="1.0", help="Show program's version number and exit")
    parser.add_argument(
        "-c", dest="count", help="Send count ECHO_REQUEST packets (default:3)",
        default=3, type=int)
    parser.add_argument(
        "-t", dest="ttl", help="Set the IP Time to Live (default:64)",
        default=64, type=int)
    parser.add_argument(
        "-s", dest="packetsize",
        help="Set the sending packet size (default:64)",
        default=64, type=int)
    parser.add_argument(
        "--timeout", dest="timeout", help="Set the timeout (default: 2s)",
        default=2, type=int)
    parser.add_argument("host", help="Target host")
    args = parser.parse_args()
    return args.__dict__


def main():
    conf = parseCmdOptions()
    ping(conf)

if __name__ == '__main__':
    main()
