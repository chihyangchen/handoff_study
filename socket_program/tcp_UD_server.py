#!/usr/bin/env python3

import socket
import time
import threading
import os
import datetime as dt
import argparse
import subprocess
import re
parser = argparse.ArgumentParser()
parser.add_argument("-p", "--port", type=int,
                    help="port to bind", default=3237)
args = parser.parse_args()
print(args.port)

IP_MTU_DISCOVER   = 10
IP_PMTUDISC_DONT  =  0  # Never send DF frames.
IP_PMTUDISC_WANT  =  1  # Use per route hints.
IP_PMTUDISC_DO    =  2  # Always DF.
IP_PMTUDISC_PROBE =  3  # Ignore dst pmtu.
TCP_CONGESTION = 13


HOST = '192.168.1.248'
PORT = args.port
PORT = 3233
thread_stop = False
exit_program = False
length_packet = 362
bandwidth = 20000*1000
total_time = 3600
cong_algorithm = 'reno'
expected_packet_per_sec = bandwidth / (length_packet << 3)
sleeptime = 1.0 / expected_packet_per_sec
prev_sleeptime = sleeptime
pcap_path = "/home/wmnlab/D/pcap_data"
ss_dir = "/home/wmnlab/D/ss"
hostname = str(PORT) + ":"
cong = 'reno'.encode()

def connection():
    s_tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_tcp.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s_tcp.setsockopt(socket.IPPROTO_TCP, TCP_CONGESTION, cong)


    s_tcp.bind((HOST, PORT))
    s_tcp.listen(1)
    conn, tcp_addr = s_tcp.accept()

    return s_tcp, conn, tcp_addr

def get_ss(port):
    now = dt.datetime.today()
    n = '-'.join([str(x) for x in[ now.year, now.month, now.day, now.hour, now.minute, now.second]])
    f = open(os.path.join(ss_dir, n), 'a+')
    while not thread_stop:
        proc = subprocess.Popen(["ss -ai dst :%d"%(port)], stdout=subprocess.PIPE, shell=True)
        line = proc.stdout.readline()
        line = proc.stdout.readline()
        line = proc.stdout.readline().decode().strip()
        f.write(",".join([str(dt.datetime.now())]+ re.split("[: \n\t]", line))+'\n')
        time.sleep(1)
    f.close()
def transmision(conn):
    print("start transmision to addr", conn)
    i = 0
    prev_transmit = 0
    ok = (1).to_bytes(1, 'big')
    start_time = time.time()
    count = 1
    sleeptime = 1.0 / expected_packet_per_sec
    prev_sleeptime = sleeptime
    global thread_stop
    while time.time() - start_time < total_time and not thread_stop:
        try:
            t = time.time()
            datetimedec = int(t)
            microsec = int(str(t - int(t))[2:10])
            z = i.to_bytes(8, 'big')
            redundent = os.urandom(length_packet-8*3-1)
            outdata = datetimedec.to_bytes(8, 'big') + microsec.to_bytes(8, 'big') + z + ok +redundent
            conn.sendall(outdata)
            i += 1
            time.sleep(sleeptime)
            if time.time()-start_time > count:
                #print("[%d-%d]"%(count-1, count), "transmit", i-prev_transmit)
                count += 1
                sleeptime = prev_sleeptime / expected_packet_per_sec * (i-prev_transmit) # adjust sleep time dynamically
                prev_transmit = i
                prev_sleeptime = sleeptime
        except:
            break    
    print("---transmision timeout---")


    ok = (0).to_bytes(1, 'big')
    redundent = os.urandom(length_packet-8*3-1)
    outdata = datetimedec.to_bytes(8, 'big') + microsec.to_bytes(8, 'big') + z + ok +redundent
    conn.sendall(outdata)

    print("transmit", i, "packets")


def receive(conn):
    conn.settimeout(3)
    print("wait for indata...")
    i = 0
    start_time = time.time()
    count = 1
    seq = 0
    prev_capture = 0
    prev_loss = 0
    global thread_stop
    while not thread_stop:
        try:
            indata = conn.recv(65535)
            if not indata:
                print("close")
                break
            duplicate_num = len(indata) // length_packet
            if len(indata) % length_packet != 0:
                print("WTF", len(indata))
            for j in range(duplicate_num):
                seq = int(indata[16+j*length_packet:24+j*length_packet].hex(), 16)
                # ts = int(int(indata[0:8].hex(), 16)) + float("0." + str(int(indata[8:16].hex(), 16)))
                # print(dt.datetime.fromtimestamp(time.time())-dt.datetime.fromtimestamp(ts)-dt.timedelta(seconds=0.28))
                # s_local.sendall(indata)
                ok = int(indata[24+j*length_packet:25+j*length_packet].hex(), 16)
                if ok == 0:
                    break
                else:
                    i += 1
            if time.time()-start_time > count:
                print("[%d-%d]"%(count-1, count), "capture", i-prev_capture)
                prev_loss += seq-i+1-prev_loss
                count += 1
                prev_capture = i
        except Exception as inst:
            print("Error: ", inst)
            thread_stop = True
    thread_stop = True
    print("[%d-%d]"%(count-1, count), "capture", i-prev_capture, "loss", seq-i+1-prev_loss, sep='\t')
    print("---Experiment Complete---")
    print("Total capture: ", i, "Total lose: ", seq - i + 1)
    print("STOP bypass")


if not os.path.exists(pcap_path):
    os.system("mkdir %s"%(pcap_path))

if not os.path.exists(ss_dir):
    os.system("mkdir %s"%(ss_dir))


# os.system("kill -9 $(ps -A | grep python | awk '{print $1}')") 

while not exit_program:

    now = dt.datetime.today()
    n = '-'.join([str(x) for x in[ now.year, now.month, now.day, now.hour, now.minute, now.second]])
    #os.system("echo wmnlab | sudo -S pkill tcpdump")
    # os.system("echo wmnlab | sudo -S tcpdump -i any port %s -w %s/%s_%s.pcap&"%(PORT, pcap_path,PORT, n))
    tcpproc =  subprocess.Popen(["tcpdump -i any port %s -w %s/%s_%s.pcap&"%(PORT, pcap_path,PORT, n)], shell=True)
    time.sleep(1)
    try:
        s_tcp, conn, tcp_addr = connection()
    except Exception as inst:
        print("Connection Error:", inst)
        continue
    thread_stop = False
    t = threading.Thread(target = transmision, args = (conn, ))
    t1 = threading.Thread(target = receive, args = (conn,))
    t2 = threading.Thread(target = get_ss, args = (PORT,))
    t.start()
    t1.start()
    t2.start()
    try:
        t.join()
        t1.join()
        t2.join()
    except KeyboardInterrupt:
        print("finish")
    except Exception as inst:
        print("Error:", inst)
        print("finish")
    finally:
        thread_stop = True
        s_tcp.close()
        conn.close()
        tcpproc.terminate()