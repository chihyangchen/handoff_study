import os
import sys
import datetime as dt




if __name__ == '__main__':

    t = dt.datetime.today()
    n = '-'.join([str(x) for x in[ t.year, t.month, t.day, t.hour, t.minute, t.second]])

    # print(len(sys.argv))
    # print(sys.argv)
    print("All supported port: 3231-3238, odd number for Uplink, even number for Downlink. ")
    print("------------------------------")
    print("You may type: ")
    print("(1) \'python3 iperf_server.py start\'")
    print("     to open port 3231-3238. ")
    print("(2) \'python3 iperf_server.py start 3231\'")
    print("     to open port 3231-3232. ")
    print("(3) \'python3 iperf_server.py start 3235 3237 3231\'")
    print("     to open port 3231-3232 & 3235-3238. ")
    print("(4) \'python3 iperf_server.py stop\'")
    print("     to close all the listening ports. ")
    print("------------------------------")

    # dirname = os.path.abspath(os.path.dirname(__file__))
    try: 
        os.mkdir(os.path.join('..', 'tcpdump'))
        os.mkdir(os.path.join('..', 'serverlog'))
    except: 
        pass

    _l = []
    if len(sys.argv) == 1: 
        print("Error: Please specify \'start\' or \'stop\'. ")
    elif len(sys.argv) == 2: 
        if sys.argv[1] == 'start': 
            for port in range(3231, 3239, 2): 
                _l.append('iperf3 -s -B 0.0.0.0 -p {} -V --logfile '.format(port)   + os.path.join('..', 'serverlog', n + '_serverLog_{}_UL.log'.format(port)  ))
                _l.append('iperf3 -s -B 0.0.0.0 -p {} -V --logfile '.format(port+1) + os.path.join('..', 'serverlog', n + '_serverLog_{}_DL.log'.format(port+1)))
            _l.append('echo wmnlab | sudo -S su')
            for port in range(3231, 3239, 2): 
                _l.append('echo wmnlab | sudo tcpdump port {} -w '.format(port)   + os.path.join('..', 'tcpdump', n + '_serverDump_{}_UL.pcap'.format(port)  ))
                _l.append('echo wmnlab | sudo tcpdump port {} -w '.format(port+1) + os.path.join('..', 'tcpdump', n + '_serverDump_{}_DL.pcap'.format(port+1)))
            for l in _l: 
                print(l)
                os.system(l + '&')
        elif sys.argv[1] == 'stop': 
            os.system('echo wmnlab | sudo killall -9 tcpdump ')
            os.system('killall -9 iperf3')
            # os.system("echo wmnlab | sudo -S su")
            # os.system('taskkill /IM "iperf3.exe" /F')
        else: 
            print("Error: Please specify \'start\' or \'stop\'. ")
    else: 
        if sys.argv[1] == 'start': 
            for i in range(2, len(sys.argv)): 
                _l.append('iperf3 -s -B 0.0.0.0 -p {} -V --logfile '.format(int(sys.argv[i]))   + os.path.join('..', 'serverlog', n + '_serverLog_{}_UL.log'.format(int(sys.argv[i]))  ))
                _l.append('iperf3 -s -B 0.0.0.0 -p {} -V --logfile '.format(int(sys.argv[i])+1) + os.path.join('..', 'serverlog', n + '_serverLog_{}_DL.log'.format(int(sys.argv[i])+1)))
            _l.append('echo wmnlab | sudo -S su')
            for i in range(2, len(sys.argv)): 
                _l.append('echo wmnlab | sudo tcpdump port {} -w '.format(int(sys.argv[i]))   + os.path.join('..', 'tcpdump', n + '_serverDump_{}_UL.pcap'.format(int(sys.argv[i]))  ))
                _l.append('echo wmnlab | sudo tcpdump port {} -w '.format(int(sys.argv[i])+1) + os.path.join('..', 'tcpdump', n + '_serverDump_{}_DL.pcap'.format(int(sys.argv[i])+1)))
            for l in _l: 
                print(l)
                os.system(l + '&')
        else: 
            print("Error: You can only specify \'start\' followed with a list of specified ports. ")

