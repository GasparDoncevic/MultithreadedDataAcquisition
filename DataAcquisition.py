from serial import Serial
import struct
import random
import time
import threading, multiprocessing
from queue import Queue
import sys
from matplotlib import pyplot as plt


""" def mockInitSerialPort(portName: str, baudRate: int = 921600):
    return Serial()

def mockReceiveData(mockSerial: Serial, storageQueue: multiprocessing.Queue, displayQueue: multiprocessing.Queue, stopped: threading.Event):
    while not stopped.is_set():
        time.sleep(0.000045)
        randValue = random.random() * 3.3
        storageQueue.put_nowait(randValue)
        displayQueue.put_nowait(randValue) """

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
        syncByte = serialPort.read(1)
        if(syncByte == b'\xff' ):
            bytedMeas = bytearray(4)
            bytedMeas = serialPort.read(4)
            floatData: float = struct.unpack('<f', bytedMeas)
            dataUnitCount += 1
            storageQueue.put_nowait(floatData)
            if dataUnitCount >= 367:
                displayQueue.put_nowait(floatData)
                dataUnitCount = 0

def storeData(queue: multiprocessing.Queue, stopped: threading.Event):
    while not stopped.is_set():
        with open("output.txt", "a") as file:
            dataUnitsStored = 0
            while dataUnitsStored < 22000:
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
        plt.plot(dataX, dataY)
        plt.pause(0.01)
        plt.xlim(0, 200)
        plt.ylim(bottom=0, top=3.5)
        plt.xlabel("Time")
        plt.ylabel("Voltage")
        plt.cla()
        

if __name__ == "__main__":
    storageQueue = multiprocessing.Queue()
    displayQueue = multiprocessing.Queue()

    stopped = threading.Event()
    with initSerialPort("COM5") as serialPort:
        storingData = threading.Thread(target=storeData, args=(storageQueue, stopped, ))
        receivingData = threading.Thread(target=receiveData, args=(serialPort, storageQueue, displayQueue, stopped, ))


        storingData.start()
        receivingData.start()  
        try:
            plotData(displayQueue)
        except KeyboardInterrupt: #Capture Ctrl-C
            print ("Captured Ctrl-C")
            stopped.set()
        stopped.set()
        storingData.join()
        receivingData.join()






