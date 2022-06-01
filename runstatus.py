#!/usr/bin/env python3
# -*- coding: ascii -*-

import sys, os

pidfile = ".runner.pid"
statusfilename = ".runner.status"


#
# open the pidfile and read the process id
#    give an error message if file not found or bad pid
# send the USR1 signal to runner.py
# open the status file for reading and check the size
# wait until it is non zero size, then read contents and copy to output, then quit.
#
# give error messages as necessary


import os, signal ,sys,time
if not(os.path.isfile('.runner.status')):
    print("File:'.runner.status' does not exist") 
try:
    fpid=open('runner.pid','r')
except:
    "error File:'.runner.pid' can not be opened"
    sys.exit()
pid=fpid.readline()
# print(pid)
start = time.time()
try:
    os.kill(int(pid), signal.SIGUSR1)
except:
    print("error bad pid")
    sys.exit()

while time.time() < start + 5:
    fstat=open('.runner.status', 'r')           #check done above
    lines =fstat.readlines()
    if len(lines)!=0:
        for line in lines:
            print(line)
        fstat.close()
        # time.sleep(6)     #check status timeout
        break

fstat=open('.runner.status', 'w')     
fstat.truncate(0)                 #truncate sometimes causes errors and doesn't print anything, instead overwrote the file by opening with 'w' in runner.py
fstat.close()

if time.time() >= start + 5:          #error if takes longer than 5 seconds
    print("status timeout") 
    sys.exit()
