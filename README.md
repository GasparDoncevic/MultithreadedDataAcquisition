# dataAcquisitionAndPlottingMultithreading
A python script used for reading data from a virtual COM port, store the data to a .txt file and plot selected data using the matplotlib library.

The data recieved is in the form of a 4 byte float, which is sent at a baud rate of 921600.
In order to allow larger quantities of data to be recieved, multithreading was implemented, which is sufficient for lower sample rates.
The ammount of plotted data each second can be adjusted.

Overstressing this code with too much data on the reciever buffer of the virtual COM port will lead to delays in plotting and unpacking data, and possibly loss of data.

Future plans:
  -implementing multiprocessing, which will allow for greater processing power to be distributed to each logical task the script performs 
