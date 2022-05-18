from fileinput import filename
import socket
import time
import os
import time

TCP_IP = '140.112.20.183'
TCP_PORT = 3230
BUFFER_SIZE = 1024

devicename = open("device.txt", "r").readline()
devicename = devicename if '\n' not in devicename else devicename[:-1]

target_dir1 = r"/sdcard/handoff_study/socket_program/pcapdir"
target_dir3 = r"/sdcard/handoff_study/socket_program/ss"
target_dir2 = r"/sdcard/Android/data/com.example.cellinfomonitor/files/Documents"
target_dir4 = r"/sdcard/mobileinsight/log"
target_dir5 = r"/home/wmnlab/data"

def senddir(target_dir):
    if not os.path.exists(target_dir):
        print(target_dir, "not exists")
        return
    dirlist = os.listdir(target_dir)

    for filename in dirlist:
        if os.path.isdir(os.path.join(target_dir, filename)):
            continue
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((TCP_IP, TCP_PORT))
        print("devicename", devicename)
        print("filename", filename)
        s.sendall(devicename.encode())
        time.sleep(0.5)
        s.sendall(filename.encode())
        time.sleep(0.5)
        msg = s.recv(65535)
        if msg == b'NO':
            s.close()
            print("PASS", filename)
            continue
        elif msg == b'OK':
            print("start to send file...")
        f = open(os.path.join(target_dir, filename), 'rb')

        s.sendfile(f)
        f.close()
        s.close()
        print('Successfully send the file', filename)
        print('connection closed')
        time.sleep(1)

senddir(target_dir5)
senddir(target_dir4)
senddir(target_dir3)
senddir(target_dir2)
senddir(target_dir1)
