from serial import Serial
import struct
import random
import time
import threading, multiprocessing
from queue import Queue
import sys
from matplotlib import pyplot as plt


def initSerialPort(portName: str, baudRate: int = 921600):
    ser = Serial()
    ser.baudrate = baudRate
    ser.port = portName
    ser.timeout = 0
    ser.set_buffer_size(rx_size=2147483647)
    ser.open()
    return ser

def receiveData(serial: Serial, parsingQueue: multiprocessing.Queue, stopped: threading.Event):
    while not stopped.is_set():
        recievedData = bytearray()
        recievedData = serial.read(serialPort.in_waiting)
        parsingQueue.put_nowait(recievedData)
      


    '''        if ((floatData > 0.0) and (floatData < 3.3)):
                dataUnitCount += 1
                storageQueue.put(floatData)
                if dataUnitCount >= 350:
                    displayQueue.put(floatData)
                    #print(displayQueue.qsize())
                    dataUnitCount = 0
             
        print((DEGUBSTARTREADTIME - DEBUGSTOPREADTIME)/1000)
    '''
def parseData(parsingQueue: multiprocessing.Queue, storageQueue: multiprocessing.Queue, displayQueue: multiprocessing.Queue, stopped: threading.Event ):
    data = bytearray()
    bytedData = bytearray(4)
    floatData = 0
    displayCount = 55000
    floatDataCount = 0
    while not stopped.is_set():
        while parsingQueue.qsize() >= 1:
            data = parsingQueue.get()
            byteCounter = 0
            while byteCounter <= len(data)-6 :
                syncByteCheck = data[byteCounter]

                while syncByteCheck == 255:    
                    bytedData[0] = data[byteCounter+1]
                    bytedData[1] = data[byteCounter+2]
                    bytedData[2] = data[byteCounter+3]
                    bytedData[3] = data[byteCounter+4]
                    floatData = struct.unpack('<f', bytedData)[0]
                    byteCounter += 4
                    floatDataCount += 1
                    storageQueue.put_nowait(floatData)
                    if floatDataCount >= displayCount:
                        displayQueue.put_nowait(floatData)
                        floatDataCount = 0
                    syncByteCheck = 0
                byteCounter += 1








def storeData(queue: multiprocessing.Queue, stopped: threading.Event):
    while not stopped.is_set():
        with open("output.txt", "a") as file:
            dataUnitsStored = 0
            while dataUnitsStored < 22000 and not stopped.is_set():
                if not queue.empty():
                    data = queue.get_nowait() # blocks the thread until item is available
                    file.write(str(data) + "\n")
                    dataUnitsStored += 1

def plotData(queue: multiprocessing.Queue):
    dataX = []
    dataY = []
    startTime = time.time_ns()
   
    while True:
        DEBUGTARTTIME = time.time_ns()
        newReading = queue.get()
        dataY.append(newReading)
        dataTime = time.time_ns()
        dataX.append((dataTime-startTime)/1000000000)
        
        plt.xlim(0, 200)
        plt.ylim(bottom=0, top=3.5)
        plt.xlabel("Time")
        plt.ylabel("Voltage")
        plt.plot(dataX, dataY)
        plt.pause(0.001)
        plt.cla()
        DEBUGSTOPtIME = time.time_ns()
        print(displayQueue.qsize())

        if (dataTime-startTime)/1000000000 >= 200:
            startTime = time.time_ns()
            dataX.clear()
            dataY.clear()
        

if __name__ == "__main__":
    storageQueue = multiprocessing.Queue()
    displayQueue = multiprocessing.Queue()
    parsingQueue = multiprocessing.Queue()

    stopped = threading.Event()
    with initSerialPort("COM3") as serialPort:
        storingData = threading.Thread(target=storeData, args=(storageQueue, stopped, ))
        receivingData = threading.Thread(target=receiveData, args=(serialPort, parsingQueue, stopped, ))
        parsingData = threading.Thread(target=parseData, args=(parsingQueue, storageQueue, displayQueue, stopped))

        ctrlcStop = False
        storingData.start()
        receivingData.start() 
        parsingData.start() 
        try:
            plotData(displayQueue)
        except KeyboardInterrupt: #Capture Ctrl-C
            print ("Captured Ctrl-C")
            stopped.set()
            plt.close()
            ctrlcStop = True
        
        if not ctrlcStop:
            stopped.set()
            storingData.join()
            receivingData.join()
            parsingData.join()
            plt.close()
    storageQueue.close()
    displayQueue.close()
    parsingQeue.close()




