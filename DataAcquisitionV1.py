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

def receiveData(mockSerial: Serial, storageQueue: multiprocessing.Queue, displayQueue: multiprocessing.Queue, stopped: threading.Event):
    dataUnitCount = 0
    while not stopped.is_set():
        DEGUBSTARTREADTIME = 0
        DEBUGSTOPREADTIME = 0
        syncByte = serialPort.read(1)
        if(syncByte == b'\xff' ):
            DEGUBSTARTREADTIME = time.time_ns()
            bytedMeas = bytearray(4)
            bytedMeas = serialPort.read(4)
            floatData = struct.unpack('<f', bytedMeas)[0]
            DEBUGSTOPREADTIME = time.time_ns()  
            if ((floatData > 0.0) and (floatData < 3.3)):
                dataUnitCount += 1
                storageQueue.put(floatData)
                if dataUnitCount >= 350:
                    displayQueue.put(floatData)
                    #print(displayQueue.qsize())
                    dataUnitCount = 0
             
        print((DEGUBSTARTREADTIME - DEBUGSTOPREADTIME)/1000)

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
        newReading = queue.get()
        dataY.append(newReading)
        dataTime = time.time_ns()
        dataX.append((dataTime-startTime)/1000000000)
        
        plt.xlim(0, 200)
        plt.ylim(bottom=0, top=3.5)
        plt.xlabel("Time")
        plt.ylabel("Voltage")
        plt.plot(dataX, dataY)
        plt.pause(0.01)
        plt.cla()

        if (dataTime-startTime)/1000000000 >= 200:
            startTime = time.time_ns()
            dataX.clear()
            dataY.clear()
        

if __name__ == "__main__":
    storageQueue = multiprocessing.Queue()
    displayQueue = multiprocessing.Queue()

    stopped = threading.Event()
    with initSerialPort("COM3") as serialPort:
        storingData = threading.Thread(target=storeData, args=(storageQueue, stopped, ))
        receivingData = threading.Thread(target=receiveData, args=(serialPort, storageQueue, displayQueue, stopped, ))

        ctrlcStop = False
        storingData.start()
        receivingData.start()  
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
            plt.close()
    storageQueue.close()
    displayQueue.close()




