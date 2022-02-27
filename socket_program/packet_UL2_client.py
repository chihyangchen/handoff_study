#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ast import While
import socket
import time
import threading
import datetime as dt
import select
import sys
import os
import queue

if not hasattr(socket, 'SO_BINDTODEVICE'):
    socket.SO_BINDTODEVICE = 25

HOST = '140.112.20.183'
PORT = 3237
PORT2 = 3238
server_addr = (HOST, PORT)
server_addr2 = (HOST, PORT2)
thread_stop = False
exitprogram = False

thread_stop = False
exit_program = False
length_packet = 250
bandwidth = 200*1000
total_time = 10
expected_packet_per_sec = bandwidth / (length_packet << 3)
sleeptime = 1.0 / expected_packet_per_sec
prev_sleeptime = sleeptime
pcap_path = "pcapdir"
exitprogram = False



def connection_setup():
    error_count = 0
    interface1 = 'usb0'
    interface2 = 'usb1'
    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_tcp.connect((HOST, PORT))
    s_tcp.settimeout(2)
    s_udp1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("wait for bind to usb0...")
    s_udp1.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, ((interface1)+'\0').encode())
    s_udp2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print("wait for bind to usb1...")
    s_udp2.setsockopt(socket.SOL_SOCKET, socket.SO_BINDTODEVICE, ((interface2)+'\0').encode())

    print("wait for establish usb1 connection...")
    s_udp1.settimeout(1)
    s_udp1.sendto("123".encode(), server_addr) # Required! don't comment it
    indata = ""
    try:
        indata = s_tcp.recv(65535)
    except Exception as inst:
        print("Error: ", inst)
        error_count += 1

    while True:
        try:
            if indata == b'PHASE2 OK':
                print("PHASE2 OK")
                break

        except Exception as inst:
            print("Error: ", inst)
            error_count += 1

        try:
            s_udp1.sendto("123".encode(), server_addr) # Required! don't comment it
            indata = s_tcp.recv(65535)


        except Exception as inst:
            print("Error: ", inst)
            error_count += 1
        if error_count > 5:
            exit()


    print("wait for establish usb2 connection...")

    s_udp2.settimeout(1)

    s_udp2.sendto("456".encode(), server_addr2) # Required! don't comment it
    try:
        indata = s_tcp.recv(65535)

    except Exception as inst:
        print("Error: ", inst)

    while True:
        try:
            if indata == b'PHASE3 OK':
                print("PHASE3 OK")
                break
            else:
                print("indata = ", indata)
        except Exception as inst:
            print("Error: ", inst)
            error_count += 1


        print("wait for establish usb2 connection...")
        try:
            s_udp2.sendto("456".encode(), server_addr2) # Required! don't comment it
            indata = s_tcp.recv(65535)
        except Exception as inst:
            print("Error: ", inst)
            error_count += 1
        if error_count > 5:
            exit()

    print("connection_setup complete")
    s_tcp.sendall(b"OK")
    return s_tcp, s_udp1, s_udp2

def transmision(s_udp):
    print("start transmision to addr", s_udp)
    i = 0
    prev_transmit = 0
    ok = (1).to_bytes(1, 'big')
    start_time = time.time()
    count = 1
    sleeptime = 1.0 / expected_packet_per_sec
    prev_sleeptime = sleeptime
    while time.time() - start_time < total_time and not thread_stop:
        t = time.time()
        datetimedec = int(t)
        microsec = int(str(t - int(t))[2:10])
        z = i.to_bytes(8, 'big')
        redundent = os.urandom(250-8*3-1)
        outdata = datetimedec.to_bytes(8, 'big') + microsec.to_bytes(8, 'big') + z + ok +redundent
        s_udp.sendto(outdata, server_addr)
        s_udp.sendto(outdata, server_addr2)
        i += 1
        time.sleep(sleeptime)
        if time.time()-start_time > count:
            print("[%d-%d]"%(count-1, count), "transmit", i-prev_transmit)
            count += 1
            sleeptime = prev_sleeptime / expected_packet_per_sec * (i-prev_transmit) # adjust sleep time dynamically
            prev_transmit = i
            prev_sleeptime = sleeptime
    
    print("---transmision timeout---")


    ok = (0).to_bytes(1, 'big')
    redundent = os.urandom(250-8*3-1)
    outdata = datetimedec.to_bytes(8, 'big') + microsec.to_bytes(8, 'big') + z + ok +redundent
    s_udp.sendto(outdata, server_addr)

    print("transmit", i, "packets")


if not os.path.exists(pcap_path):
    os.system("mkdir %s"%(pcap_path))



while not exitprogram:
    try:
        x = input("Press Enter to start\n")
        if x == "EXIT":
            break
        now = dt.datetime.today()
        n = '-'.join([str(x) for x in[ now.year, now.month, now.day, now.hour, now.minute, now.second]])
        # os.system("tcpdump -i any net 140.112.20.183 -w %s.pcap &"%(n))
        s_tcp, s_udp1, s_udp2 = connection_setup()
    except Exception as inst:
        print("Error: ", inst)
        # os.system("pkill tcpdump")
        continue
    thread_stop = False
    t = threading.Thread(target=transmision, args=(s_udp1,))
    t.start()
    while True and t.is_alive():
        x = input("Enter STOP to Stop\n")
        if x == "STOP":
            thread_stop = True
            s_tcp.sendall("STOP".encode())
            break
        elif x == "EXIT":
            thread_stop = True
            exitprogram = True
            s_tcp.sendall("EXIT".encode())
    thread_stop = True
    t.join()
    s_tcp.close()
    s_udp1.close()
    s_udp2.close()

    # os.system("pkill tcpdump")
