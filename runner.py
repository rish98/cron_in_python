#!/usr/bin/env python3
# -*- coding: ascii -*-

import sys, os, time, datetime, signal

"""
The configuration file for runner.py will contain one line for each program that is to be run.   Each line has the following parts: 

timespec program-path parameters

where program-path is a full path name of a program to run and the specified time(s), parameters are the parameters for the program,
timespec is the specification of the time that the program should be run.

The timespec has the following format:

[every|on day[,day...]] at HHMM[,HHMM] run

Square brackets mean the term is optional, vertical bar means alternative, three dots means repeated.

Examples:

every Tuesday at 1100 run /bin/echo hello
	every tuesday at 11am run "echo hello"
on Tuesday at 1100 run /bin/echo hello
	on the next tuesday only, at 11am run "echo hello"
every Monday,Wednesday,Friday at 0900,1200,1500 run /home/bob/myscript.sh
	every monday, wednesday and friday at 9am, noon and 3pm run myscript.sh
at 0900,1200 run /home/bob/myprog
	runs /home/bob/myprog once  at 9am and noon


"""

#
# open the configuration file and read the lines, 
#    check for errors
#    build a list of "run" records that specifies a time and program to run
#

#
# define up the function to catch the USR1 signal and print run records
#

#
# sort run records by time
# take the next record off the list and wait for the time, then run the program
# add a record to the "result" list
# if this was an "every" record", add an adjusted record to the "run" list 
#
# repeat until no more to records on the "run" list, then append(temp[i])
import sys, os, time, datetime, signal

"""
The configuration file for runner.py will contain one line for each program that is to be run.   Each line has the following parts: 

timespec program-path parameters

where program-path is a full path name of a program to run and the specified time(s), parameters are the parameters for the program,
timespec is the specification of the time that the program should be run.

The timespec has the following format:

[every|on day[,day...]] at HHMM[,HHMM] run

Square brackets mean the term is optional, vertical bar means alternative, three dots means repeated.

Examples:

every Tuesday at 1100 run /bin/echo hello
	every tuesday at 11am run "echo hello"
on Tuesday at 1100 run /bin/echo hello
	on the next tuesday only, at 11am run "echo hello"
every Monday,Wednesday,Friday at 0900,1200,1500 run /home/bob/myscript.sh
	every monday, wednesday and friday at 9am, noon and 3pm run myscript.sh
at 0900,1200 run /home/bob/myprog
	runs /home/bob/myprog once  at 9am and noon


"""

#
# open the configuration file and read the lines, 
#    check for errors
#    build a list of "run" records that specifies a time and program to run
#

#
# define up the function to catch the USR1 signal and print run records
#

#
# sort run records by time
# take the next record off the list and wait for the time, then run the program
# add a record to the "result" list
# if this was an "every" record", add an adjusted record to the "run" list 
#
# repeat until no more to records on the "run" list, then exit
#
import os
import sys
import re
import datetime
import time
import signal

operation={}            #format of an operation...
global operationList    #...{prog:   ,progPath:   ,timeSpec:{when:   ,day;   },dT:[   ],repeat:   ,done:   }
operationList=[]        #list of all operations
timeSpec={}
global currDT
# currDT = datetime.datetime(2020, 10, 22,12,0,0)           #made currDT a global variable which i updated in the program for testing
currDT=datetime.datetime.now()
global statList
statList=[]         #list to store all the records of the status file before it is written to it

#https://stackoverflow.com/questions/6558535/find-the-date-for-the-first-monday-after-a-given-a-date [used site for idea to get next weekday]


def receive_signal(signum, stack):
    start = time.time()
    # print("stat request")
    fstat=open('.runner.status', 'w')
    for line in statList:
        fstat.write(str(line))
    fstat.close()
    statList.clear()     #clear statList
    if time.time() >= start + 5:          #error if takes longer than 5 seconds
        print("status timeout")

signal.signal(signal.SIGUSR1, receive_signal)

def findEnd_date(currDT, dayOfWeek):
    weekDaysList = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    offset = weekDaysList.index(dayOfWeek) - currDT.weekday()
    if offset < 0: # Target day already happened this week
        offset += 7
    return currDT.date() + datetime.timedelta(offset)

def findClosest():
    record= 1000000          #604800 seconds in a week
    recordHolder=[0,0,0]          #assume first operation is the closest operation
    # currDT=datetime.datetime.now()
    DThist=[]       #list of all datetimes to check repeats 
    for i in range(len(operationList)):
        operationList[i]["dT"]=[]
        for j in range(len(operationList[i]['timeSpec']['day'])):
            for k in range(len(operationList[i]['timeSpec']['when'])):          #find differnce between cureent time and all run times

                endDT = findEnd_date(currDT,operationList[i]['timeSpec']['day'][j]) 
                endDT_t=datetime.datetime.strptime(str(operationList[i]['timeSpec']['when'][k]),'%H%M')
                endDT=datetime.datetime.combine(endDT,endDT_t.time())
                operationList[i]["dT"].append(endDT)       #store dt for future use
                operationList[i]["dT"].sort()
                diff=endDT-currDT
                diffSec=diff.total_seconds()

                if diffSec<record and diffSec>0:
                    record=diffSec
                    recordHolder=[i,j,k]            #operationList => index=i  ,  ['timeSpec']['day'] => index=j  ,  ['timeSpec']['when'] => index=k
                # print(DThist)
                if endDT in DThist:                     #check all datetimes to see if any repeated 
                    print("datetime:",endDT,"repeated")
                    sys.exit()
                else:
                    DThist.append(endDT)
    return(recordHolder,record)




def splitLine(line):
    operation={}
    timeSpec={}

    #search between at and run
    try:
        whenStr=re.search('at\s(.*)\srun', line)
        whenArray=(whenStr.group(1).split(','))
    except:
        print("bad configuration file line:",line)
        sys.exit()

    for i in range(len(whenArray)-1,-1,-1):         #check time is valid
        if   (0<=int(whenArray[i][0:2])<=23) and (0<=int(whenArray[i][-2:])<=59) and (len(whenArray[i])==4 and whenArray[i].isnumeric()):#if first 2 numbers are between 0-23 and last 2 numbers between 0-59
            whenArray[i]=str(whenArray[i])
        else:
            print("invalid line ",line)
            sys.exit()
    whenArray.sort()
    timeSpec['when']=whenArray

    #search from run to end of string
    try:
        runStr=re.search('run\s(.*)', line)         #runStr has program path and parameters
    except re.error:
        print("bad configuration file line:",line)
    runArray=(runStr.group(1).split(' ',1))         #maxsplit =1 to take only program path
    operation['progPath']=runArray[0]


    if len(runArray)>1:
        operation['parameters']=runArray[1]         #if the previous array had more than one item it also had parameters...
    else:
        operation['parameters']=''                  #...if it didnt set parameters to none

    #if line starts with every 
    if line.startswith("every"):
        try:
            dayStr=re.search('every\s(.*)\sat', line)
        except re.error:
            print("bad configuration file line:",line)
        dayArray=(dayStr.group(1).split(','))
        timeSpec['day']=sortDays(dayArray)
        operation['timeSpec']=timeSpec
        operation['repeat']=True
        operationList.append(operation)

#if line starts with on 
    elif line.startswith("on"):
        try:
            dayStr=re.search('on\s(.*)\sat', line)
        except re.error:
            print("bad configuration file line:",line)
        dayArray=(dayStr.group(1).split(','))
        timeSpec['day']=sortDays(dayArray)
        operation['timeSpec']=timeSpec
        operation['repeat']=False
        operationList.append(operation)


#if it starts with "at" ,create separate operations for each time as may occur on different days
    elif line.startswith("at"):         
        temp=timeSpec["when"]       #store "when" in a temporary variable so each element is in a separate operation
        for i in range (len(temp)):
            operation={}
            timeSpec={}
            timeSpec["day"]=[]
            timeSpec["when"]=[]
            operation['progPath']=runArray[0]
            if len(runArray)>1:
                operation['parameters']=runArray[1]
            else:
                operation['parameters']=''
            operation['timeSpec']=timeSpec
            operation['repeat']=False           #(above) all common items in operation 
            
            if int(temp[i])>int(currDT.time().strftime('%H%M')):          #if line start with "at" take current day...
                timeSpec["when"].append(temp[i])
                timeSpec["day"].append(currDT.strftime('%A'))
                
                operationList.append(operation)
            else:
                timeSpec["when"].append(temp[i])
                timeSpec["day"].append((currDT+datetime.timedelta(1)).strftime('%A'))           #...or next day if time passed
                
                operationList.append(operation)

    errorChecks()
    for i in range(len(operationList)):         #create a done array wih the same length as "dT"
        operationList[i]["done"]=[1]*( len (operationList[i]["timeSpec"]["when"]) * len (operationList[i]["timeSpec"]["day"]) )
        #done is an list of boolean values that correspond to its index in dT(datetime) it shows if a run has run or not if it is an 'every' program it always remains 1 
            
def errorChecks():
    fconfig =open('.runner.conf', 'r')
    lines=fconfig.readlines()
    for line in lines:
        errFlag=0
        if not(line.startswith('every ') or line.startswith('on ') or line.startswith('at ') or ('at ' in line)):
            errFlag=1
        elif line.startswith('every ') and ("on "in line):          #checks if it is a 'every' program 'on' is not there in the line...
            errFlag=1       
        elif line.startswith('on ') and ("every "in line):          #may give false positive if program name ends in 'on'  
            errFlag=1
        elif line.startswith('at ') and ("every "in line or "on "in line):          #may give false positive if program name ends in 'every' or 'on'...
            errFlag=1                                                               #... so searched for 'every ' (with a space) to reduce that error
        if errFlag:
            print("bad configuration file line:",line)#if any of the checks raise a flag then show an error
            sys.exit()
    
    fconfig.close()             #checks for repeats
    for i in range (len(operationList)):
        if operationList.count(operationList[i])>1 :
            print("line",operationList[i],"repeated")           #check any full line repeated
            sys.exit()
        for j in range (len(operationList[i]['timeSpec']['when'])):
            if operationList[i]['timeSpec']['when'].count(operationList[i]['timeSpec']['when'][j])>1 :#check same time in a line 
                print("time",operationList[i]['timeSpec']['when'][j],"repeated")
                sys.exit()
        for k in range(len(operationList[i]['timeSpec']['day'])) :
            if operationList[i]['timeSpec']['day'].count(operationList[i]['timeSpec']['day'][k])>1:#check same day in a line 
                print("day",operationList[i]['timeSpec']['day'][k],"repeated")
                sys.exit()
    

def sortDays(dayArray):
    daysWeek=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    for i in range(len(dayArray)-1,-1,-1):
        if dayArray[i] not in daysWeek:                 #(part of error checks )
            print("invalid day "+dayArray[i])           #check for any invalid days
            sys.exit()
    dayArray.sort(key=daysWeek.index)
    return dayArray    
    

def runProg(recordHolder):
    pid = os.fork()
    if pid==0:              #child runs the exec
        dTindex=recordHolder[2]+len(operationList[(recordHolder[0])]["timeSpec"]['when'])*recordHolder[1]
        #exec the program
        try:
            cronArgv=operationList[(recordHolder[0])]['parameters'].split(' ')
            cronArgv.insert(0,"cronProg")
            os.execvp(operationList[(recordHolder[0])]['progPath'],cronArgv)
        except:
            sys.exit(1)

    elif pid == -1:     #error when forking
        print (" fork failed")

    else:           #parent continues with updating the status file 
        wval = os.wait()
        dTindex=recordHolder[2]+len(operationList[int(recordHolder[0])]["timeSpec"]['when'])*recordHolder[1]
        # print (" exit status:", wval[1]>>8)

        if(wval[1]>>8 != 0):
            try:
                statList.append("error {} {} {}\n".format((operationList[(recordHolder[0])]['dT'][dTindex]).ctime(),operationList[(recordHolder[0])]['progPath'],operationList[(recordHolder[0])]['parameters']))
            except:
                pass

        else:
            statList.append("ran {} {} {}\n".format((operationList[(recordHolder[0])]['dT'][dTindex]).ctime(),operationList[(recordHolder[0])]['progPath'],operationList[(recordHolder[0])]['parameters']))
            try:            #if last element in list get index error 
                statList.append("will run {} {} {}\n".format((operationList[(recordHolder[0])]['dT'][dTindex+1]).ctime(),operationList[(recordHolder[0])]['progPath'],operationList[(recordHolder[0])]['parameters']))
            except:
                pass
        

    
    if operationList[(recordHolder[0])]["repeat"] == False:         #only change done to 0 ,if it is an 'on' operation (repeat is false)
        operationList[recordHolder[0]]['done'][dTindex]=0 

    if sum(operationList[recordHolder[0]]['done'])==0:              #if every element in the done array is 0 ,sum(done)==0...
        operationList.remove(operationList[recordHolder[0]])        #...remove that operation


# ****************************************************************************************************************************************


# ****************************************************************************************************************************************

# splitLine('every Monday,Wednesday,Friday at 0900,1200,1500 run /home/bob/myscript.sh gf ssk jd')
# splitLine('every Tuesday at 1100 run /bin/echo hello')

try:
    fpid=open('runner.pid','w')         #runner.pid file check
except:
    print("error File: runner.pid can not be created")
    sys.exit()
fpid.write(str(os.getpid()))
fpid.close()

try: 
    if not(os.path.isfile('.runner.status')):            #.runner.status file check
        fstat=open('.runner.status', 'w')
        fstat.close()
except:
    print("error File: .runner.status can not be created")

try:
    fconfig =open('.runner.conf', 'r')
except:
    print("configuration file not found")
    sys.exit()

if os.path.getsize('.runner.conf')==0 or os.path.getsize('.runner.conf')==1:     # on ed if the cursor is on a line of a file it counts that line as some data...
    print("configuration file empty")                                            #...or if you add data then delete it it still counts as some infomation
    sys.exit()
else:
    lines=fconfig.readlines()
    for line in lines:
        if  line!='':           #check line is not blank
            splitLine(line)

# recordHolder,record=findClosest()
# print(operationList[(recordHolder[0])]['progPath'],record)

# for i in operationList:
#     print(i)

while len(operationList)>0:
    # print(currDT.ctime())
    currDT = datetime.datetime.now()
    recordHolder,record=findClosest()           #returns array to recordHolder and time in seconds to next operation to record 
    # currDT += datetime.timedelta(seconds=record)          #change currDT to the execution time of the next program so I dont wait for that amount of time
    # time.sleep(2.5)
    time.sleep(record)
    runProg(recordHolder)

print("nothing left to run")
sys.exit()

#yayy!

