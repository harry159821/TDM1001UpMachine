#-*- coding: UTF-8 -*-

import sys
from time import sleep
from serial import Serial, serialutil
from PyQt4 import QtCore

class SerialDev(QtCore.QThread):
    BAUDRATES = (50, 75, 110, 134, 150, 200, 300, 600, 1200, 1800, 2400, 4800,
                 9600, 19200, 38400, 57600, 115200, 230400, 460800, 500000,
                 576000, 921600, 1000000, 1152000, 1500000, 2000000, 2500000,
                 3000000, 3500000, 4000000)
    SETTING = serialutil
    BYTESIZES = (SETTING.FIVEBITS, SETTING.SIXBITS, SETTING.SEVENBITS, SETTING.EIGHTBITS)
    STOPBITS = (SETTING.STOPBITS_ONE, SETTING.STOPBITS_ONE_POINT_FIVE, SETTING.STOPBITS_TWO)
    PARITYS = (SETTING.PARITY_NONE, SETTING.PARITY_EVEN, SETTING.PARITY_ODD, SETTING.PARITY_MARK, SETTING.PARITY_SPACE)
    PARITY_NAMES = SETTING.PARITY_NAMES
    
    def __init__(self, parent = None):
        '''write is a function that printf the data of serial.'''
        super(SerialDev, self).__init__(parent)
        self.setting = {'port'      : 'COM1',
                        'baudrate'  : 115200,
                        'bytesize'  : 8,
                        'stopbits'   : 1,
                        'parity'    : 'N',
                        'timeout'   : 300
                        }
        self.__serial = None        
        self.__isOpen = False
        self.__isRun = False
        self.__com = []
        # self.__checkPort() # 把占时间的串口搜索任务放在QTimer拟线程里面运行
        self.___even_data = ''

        
        self.qObj = QtCore.QObject()
        
    def __del__(self):
#         print 'SerialDev, del'
        self.__closeCom()

    def checkPort(self):
        self.__com = []
        for i in range(20):
            port_str = 'COM%d' % i
            self.setting['port'] = port_str
            is_open, msg = self.__openCom()
            if is_open:
                self.__serial.close()
                self.__com.append(port_str)
            else:
                try:
                    index = msg.index(']')
                    if int(msg[index-1]) == 5:             
                        self.__com.append(port_str)
                except Exception, e:
                    pass
        self.setting['port'] = self.__com[0]
        return self.__com 

    def __checkPort(self):
        for i in range(10):
            port_str = 'COM%d' % i
            self.setting['port'] = port_str
            is_open, msg = self.__openCom()
            if is_open:
                self.__serial.close()
                self.__com.append(port_str)
            else:
                try:
                    index = msg.index(']')
                    if int(msg[index-1]) == 5:             
                        self.__com.append(port_str)
                except Exception, e:
                    pass
        self.setting['port'] = self.__com[0]
        return self.__com 

    def checkPort(self):
        for i in range(10):
            port_str = 'COM%d' % i
            self.setting['port'] = port_str
            is_open, msg = self.__openCom()
            if is_open:
                self.__serial.close()
                self.__com.append(port_str)
            else:
                try:
                    index = msg.index(']')
                    if int(msg[index-1]) == 5:             
                        self.__com.append(port_str)
                except Exception, e:
                    pass
        try:
            self.setting['port'] = self.__com[0]
        except Exception, e:
            pass
        return self.__com

    def getPort(self):
        '''get exist COM'''
        return self.__com
    
    def getOpen(self):
        '''get serial status,
        False is not opened,
        True is opened'''
        return self.__isOpen
    
    def turnOn(self, 
               port,
               baudrate=9600, 
               bytesize=SETTING.EIGHTBITS,
               stopbits=SETTING.STOPBITS_ONE,
               parity=SETTING.PARITY_NONE
               ):
        self.setting['port'] = port
        self.setting['baudrate'] = baudrate
        self.setting['bytesize'] = bytesize
        self.setting['parity'] = parity
        self.setting['stopbits'] = stopbits
        
        is_open, msg = self.__openCom()
#         print is_open, msg
        if is_open:
            self.start()
        return is_open, msg
            
    def turnOff(self):
        self.__isRun = False
        self.terminate()
        while self.isRunning():
            sleep(0.1)
        self.__closeCom()
#         print 'turnOff'
    
    def __openCom(self):
        try:
            self.__serial = Serial(self.setting['port'], self.setting['baudrate'], self.setting['bytesize'],
                                 self.setting['parity'], self.setting['stopbits'], self.setting['timeout'])
            self.__isOpen = True
            self.__serial.flushInput()
            self.__serial.flushOutput()
            return True, 'success'
        except Exception, msg:
            self.__isOpen = False
            return False, msg.message.decode('gbk')
       
    def __closeCom(self):
        if self.__isOpen:
            self.__isOpen = False
            self.__serial.close()
            
    def send(self, data):
        '''send data to opend COM'''
        if self.__isOpen:
            return self.__serial.write(data)
        else:
            return False
        
    def __recv(self):
        count = 0
        data = ''
        while True:
            sleep(0.01)
            if count != 0:
                count += 1
#                 print count
            n = self.__serial.inWaiting()
            if n > 0:
                data += self.__serial.read(n)
                try:        #Avoid characters be truncated
                    count += 1                
                    data = buffToHex(data)
                    print data
                    udata = data.decode('utf-8')   # 此处导致正数出现问题                 
                    self.qObj.emit(QtCore.SIGNAL('SerialRecvData'), udata)
                    break
                except Exception,e:
                    print e
                    continue
            if count > 50:        #received messy code need
                self.qObj.emit(QtCore.SIGNAL('SerialRecvData'), data)
                break  
              
    def run(self): 
        self.__isRun = True
        while self.__isRun and self.__isOpen:
            self.__recv()
                
def toHex(argv):
    result = ''
    for i in argv:
        # result += toHexList[i.upper()]
        result += i.upper()
    return result
        
def buffToHex(argv):
    '''显示十六进制'''
    result = ''
    hLen = len(argv)
    for i in xrange(hLen):
        hvol = ord(argv[i])
        hhex = '%02x'%hvol
        # result += hhex+' '
        # result += bin(int(hhex,16))[2:] + '\n'
        result += toHex(hhex) + ' '
    return result

if __name__ == '__main__':
    sd = SerialDev()
    port = sd.getPort()    
    print port[0]
    print sd.turnOn(port[0], 115200, sd.SETTING.EIGHTBITS, sd.SETTING.STOPBITS_ONE, sd.SETTING.PARITY_NONE)
    sleep(10)
    print 'off'
    sd.turnOff()
    
    