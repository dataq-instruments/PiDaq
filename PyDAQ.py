import serial
import time
import sys
import threading
import queue
import time
import socket
import struct
import csv
from datetime import datetime
from time import sleep
from random import random
from multiprocessing import Process
import math
CONST_SER_PORT = '/dev/ttyACM0'   #get the com port from device manger and enter it here
ip     = "127.0.0.1"  #local host
port   = 8008
input_str = "                                                                                  "
#serDataq = "                                                                                   "
line = "                                                                                       "
inputQueue = "exit"
bytestoread = 0
read_flg = False
write_flg = False
now_time = datetime.now()
# Create a datagram socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # socket.SOCK_DGRAM)
server_address = (ip, port)
#create file to store data to
f=open("dataq0.csv","w")
serDataq = serial.Serial(CONST_SER_PORT)
j = 0

#thread to read keyboard input
def read_kbd_input(inputQueue):
    while (True):
        input_str = input()
        inputQueue.put(input_str)
        sleep(.001)

def txdata():
    bytesToRead = 0
    lineCntr = 0
    fileCntr = 0
    inputStr = ""

    global j
    global f
    while(True):
        bytesToRead = serDataq.inWaiting()
        while (bytesToRead>100):
            inputStr = serDataq.readline()    
            print(inputStr)
            s.sendto(inputStr, server_address)

def main():
    now = ""
    i = 0
    serDataq.write(b"stop\r")        #stop in case device was left scanning
    serDataq.write(b"eol 1\r") 
    serDataq.write(b"encode 2\r")    #set up the device for ascii mode
    serDataq.write(b"slist 0 0\r")   #scan list exitposition 0 channel 0 thru channel 7
    serDataq.write(b"slist 1 1\r")
    serDataq.write(b"slist 2 2\r")
    serDataq.write(b"slist 3 3\r")
    serDataq.write(b"slist 4 4\r")
    serDataq.write(b"slist 5 5\r")
    serDataq.write(b"slist 6 6\r")
    serDataq.write(b"slist 7 7\r")
    serDataq.write(b"srate 6000\r") 	# samples/sec  = 60,000,000/(srate*dec*deca)
                                        #example 50 = 60,000,000/6000*200
    serDataq.write(b"dec 200\r")  
    serDataq.write(b"deca 1\r") 
    time.sleep(1)  
    serDataq.read_all()              #flush all command responses

    
    print("DI-1100 init")
    # Start DATAQ
    outputThread = threading.Thread(target=txdata, daemon=True)
    outputThread.start()
    sleep(2)
    serDataq.write(b"start\r")           #start scanning

    
    EXIT_COMMAND = "exit"
    inputQueue = queue.Queue()
    inputThread = threading.Thread(target=read_kbd_input, args=(inputQueue,), daemon=True)
    inputThread.start()
    while (True):
        if (inputQueue.qsize() > 0):
            input_str = inputQueue.get()
            if (input_str == EXIT_COMMAND):
                serDataq.write(b"stop\r")
                time.sleep(1)           
                serDataq.close()
                print('USB closed')
                stop_threads = True
                print('Threads killed')
                f.close()
                print('File closed')
                print("Exiting!")
                sleep(.01)
                sys.exit()
                break
            else:
                serDataq.write(bytes(input_str+'\r', 'utf-8'))
                print(input_str)
        sleep(.001)
if (__name__ == '__main__'): 
    main()
 

# Note: (1) is considered as int, whereas (1,) is considered as a tuple in python. So, in case 
# of a single argument an extra comma must be placed to project it as a tuple