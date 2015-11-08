#!/usr/bin/python
# -*- coding:utf-8 -*-
from PyQt4 import QtGui,QtCore,Qt
from SerialDev import SerialDev
from serial import Serial, serialutil

import pyqtgraph
from pyqtgraph.Qt import QtCore, QtGui
from CRCModules.CRC16 import CRC16
import numpy as np
import time,re,struct,os,sys
import mp3play
# import binascii
import ctypes
'''
UpMachine Project
上位机工程
'''

toHexList = {
    '0':'0000','1':'0001','2':'0010','3':'0011',
    '4':'0100','5':'0101','6':'0110','7':'0111',
    '8':'1000','9':'1001','A':'1010','B':'1011',
    'C':'1100','D':'1101','E':'1110','F':'1111',
    }

def toHex(argv):
    result = ''
    for i in argv:
        # result += toHexList[i.upper()]
        result += i.upper()
    return result
 
def HEX(argv):
    tmp = hex(argv)[2:]
    if len(tmp) == 1:
        tmp = '0'+tmp
    return tmp

def buffToHex(argv):
    '''显示十六进制'''
    result = ''
    hLen = len(argv)
    for i in xrange(hLen):
        hvol = ord(argv[i])
        hhex = '%02x'%hvol
        # result += hhex+' '
        # result += bin(int(hhex,16))[2:] + '\n'
        result += toHex(hhex) + '\n'
    return result

class MainWindow(QtGui.QMainWindow):
    def __init__(self,app,parent=None):
        super(MainWindow,self).__init__()
        self.setWindowTitle(u'UpMachine Project')
        # ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

        self.app = app
        self.getSetting()
        self.setWindowOpacity(1) # 初始透明度
        self.setWindowIcon(QtGui.QIcon('./icon.ico')) # 窗口图标
        self.isMaxShow = 0

        # 窗口样式表文件读取
        sshFile="./three.qss"
        with open(sshFile,"r") as fh:
            self.setStyleSheet(fh.read())
        #-----------------------------------------------------------------------------
        self.serial = SerialDev()
        # self.soundThread = SoundThread()
        # self.soundThread.run()
        # 左窗口-----------------------------------------------------------------------
        self.leftWidget = QtGui.QWidget()
        # self.leftWidget.setMaximumSize(200,700)
        self.leftWidget.setMaximumSize(200,4000)
        # self.leftWidget.resize(200,650)
        # self.leftWidget.setStyleSheet("""border:1px solid red""")
        # 使用QSS样式表设置背景颜色
        self.leftWidget.setStyleSheet("""
            .QWidget{
                background:rgb(143,143,143)
            }
            .QLabel{
                background:rgb(143,143,143)
            }
            """)
        # self.leftWidget.setStyleSheet(".QWidget{background:rgb(212,212,212)}")

        # self.leftWidget.testButton = QtGui.QPushButton(u'刷新串口',self.leftWidget)
        self.leftWidget.testButton = PushButton(u'刷新串口',self.leftWidget)

        self.leftWidget.testButton.clicked.connect(self.updateSerial)
        self.leftWidget.linkButton = PushButton(u'连接串口',self.leftWidget)
        self.leftWidget.linkButton.clicked.connect(self.connectSerial)
        
        self.leftWidget.stopUpdataVoltageDataButton  = PushButton(u'电压表暂停刷新',self.leftWidget)
        self.leftWidget.stopUpdataGalvanicDataButton = PushButton(u'电流表暂停刷新',self.leftWidget)        
        self.leftWidget.stopUpdataGalvanicDataButton.clicked.connect(self.stopUpdataGalvanicData)
        self.leftWidget.stopUpdataVoltageDataButton.clicked.connect(self.stopUpdataVoltageData)
        # 串口选择框
        self.comboBox = QtGui.QComboBox(self.leftWidget) 

        # 识别可用的串口
        # for i in self.serial.getPort(): 
        #     self.comboBox.addItem(i)
        
        # 波特率选择框        
        self.baudrateComboBox = QtGui.QComboBox()
        index = 0
        for i in (2400, 4800, 9600, 19200, 115200):
            self.baudrateComboBox.addItem(str(i))
            if str(i) == self.baudrate:
                self.baudrateComboBox.setCurrentIndex(index)
            index += 1        
        self.baudrateLabel = QtGui.QLabel(u' 波特率选择')
        # 数据位数选择框
        self.bytesizeComboBox = QtGui.QComboBox()
        index = 0
        for i in range(len(SerialDev.BYTESIZES)):
            self.bytesizeComboBox.addItem(str(SerialDev.BYTESIZES[i]))
            if SerialDev.BYTESIZES[i] == SerialDev.SETTING.EIGHTBITS:
                index = i
            if SerialDev.BYTESIZES[i] == self.bytesize:
                index = i
        self.bytesizeComboBox.setCurrentIndex(index)
        self.bytesizeComboBox.setEnabled(False)
        self.bytesizeLabel = QtGui.QLabel(u' 数据位选择')
        # 停止位选择框
        self.stopbitsComboBox = QtGui.QComboBox()
        for i in range(len(SerialDev.STOPBITS)):
            self.stopbitsComboBox.addItem(str(SerialDev.STOPBITS[i]))
            if SerialDev.STOPBITS[i] == SerialDev.SETTING.STOPBITS_ONE:
                index = i
            if SerialDev.STOPBITS[i] == self.stopbits:
                index = i
        self.stopbitsComboBox.setCurrentIndex(index)
        self.stopbitsComboBox.setEnabled(False)
        self.stopbitsLabel = QtGui.QLabel(u' 停止位选择')        

        # 左下角提示Label
        self.tipLabel = QtGui.QLabel(u'          ')
        self.statusLabel = QtGui.QLabel(u'          ')
        # self.tipLabel = QtGui.QLabel(u'Hello World')

        # 左边边框布局
        self.grid = QtGui.QGridLayout()
        self.verticalLayout = QtGui.QVBoxLayout(self.leftWidget)

        # 左上关于按钮
        self.aboutPushButton = labelBtn(u'about',self.leftWidget)
        self.aboutPushButton.setMaximumSize(200,101)
        self.aboutPushButton.resize(200,101)
        self.aboutPushButton.setPixmap(QtGui.QPixmap(r'./aboutNormal.png'))
        self.aboutPushButton.Entered.connect(self.buttonEnterFunc)
        self.aboutPushButton.Leaved.connect(self.buttonLeavedFunc)

        self.verticalLayout.addWidget(self.aboutPushButton,0) #列
        self.verticalLayout.addLayout(self.grid)

        # 输入框  ---------------------------------      
        # VoltageLayout_one  = QtGui.QHBoxLayout()
        # GalvanicLayout_one = QtGui.QHBoxLayout()
        
        # self.leftWidget.sendVoltageDataButton  = PushButton(u'电压指令',self.leftWidget)
        # self.leftWidget.sendGalvanicDataButton = PushButton(u'电流指令',self.leftWidget) 

        # self.leftWidget.sendVoltageDataLineEdit  = QtGui.QDoubleSpinBox(self.leftWidget)
        # self.leftWidget.sendGalvanicDataLineEdit = QtGui.QDoubleSpinBox(self.leftWidget)

        # self.leftWidget.sendVoltageDataLineEdit.setMinimumHeight(40)
        # self.leftWidget.sendVoltageDataLineEdit.setStyleSheet("""
        #     background:transparent;
        #     border: 0px solid red;
        #     font-size:40px;
        #     color:rgb(0,220,0);
        #     selection-color:rgb(0,220,0);
        #     selection-background-color: rgb(143,143,143);
        #     """)
        # self.leftWidget.sendVoltageDataLineEdit.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)

        # self.leftWidget.sendGalvanicDataLineEdit.setMinimumHeight(40)
        # self.leftWidget.sendGalvanicDataLineEdit.setStyleSheet("""
        #     background:transparent;
        #     border: 0px solid red;
        #     font-size:40px;
        #     color:rgb(0,220,0);
        #     selection-color:rgb(0,220,0);
        #     selection-background-color: rgb(143,143,143);
        #     """)
        # self.leftWidget.sendGalvanicDataLineEdit.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)

        # VoltageLayout_one.addWidget(self.leftWidget.sendVoltageDataLineEdit )
        # VoltageLayout_one.addWidget(self.leftWidget.sendVoltageDataButton )
        # GalvanicLayout_one.addWidget(self.leftWidget.sendGalvanicDataLineEdit)
        # GalvanicLayout_one.addWidget(self.leftWidget.sendGalvanicDataButton)

        # VoltageLayout_one.setContentsMargins(3,0,0,0)
        # GalvanicLayout_one.setContentsMargins(3,0,0,0)

        # self.verticalLayout.addLayout(VoltageLayout_one )
        # self.verticalLayout.addLayout(GalvanicLayout_one)
        # 输入框 Over ---------------------------------

        # 连接按钮
        self.verticalLayout.addWidget(self.leftWidget.linkButton)
        # 暂停按钮
        self.verticalLayout.addWidget(self.leftWidget.stopUpdataVoltageDataButton)
        self.verticalLayout.addWidget(self.leftWidget.stopUpdataGalvanicDataButton)            

        # 输入框  ---------------------------------      
        VoltageLayout_one  = QtGui.QHBoxLayout()
        GalvanicLayout_one = QtGui.QHBoxLayout()
        startStopLayout = QtGui.QHBoxLayout()
        
        self.leftWidget.sendVoltageDataButton  = PushButton(u'电压指令',self.leftWidget)
        self.leftWidget.sendGalvanicDataButton = PushButton(u'电流指令',self.leftWidget) 

        # 可调范围 0 ~ 500
        self.leftWidget.sendVoltageDataLineEdit  = QtGui.QDoubleSpinBox(self.leftWidget)    
        self.leftWidget.sendVoltageDataLineEdit.setRange(0,500)
        self.leftWidget.sendVoltageDataLineEdit.setDecimals(0) # 小数位数
        # 可调范围 0 ~ 20
        self.leftWidget.sendGalvanicDataLineEdit = QtGui.QDoubleSpinBox(self.leftWidget)
        self.leftWidget.sendGalvanicDataLineEdit.setRange(0,20)
        self.leftWidget.sendGalvanicDataLineEdit.setDecimals(0) # 小数位数

        self.leftWidget.sendVoltageDataLineEdit.setMinimumHeight(40)
        self.leftWidget.sendVoltageDataLineEdit.setStyleSheet("""
            background:transparent;
            border: 0px solid red;
            font-size:40px;
            color:rgb(0,220,0);
            selection-color:rgb(0,220,0);
            selection-background-color: rgb(143,143,143);
            """)
        self.leftWidget.sendVoltageDataLineEdit.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)

        self.leftWidget.sendGalvanicDataLineEdit.setMinimumHeight(40)
        self.leftWidget.sendGalvanicDataLineEdit.setStyleSheet("""
            background:transparent;
            border: 0px solid red;
            font-size:40px;
            color:rgb(0,220,0);
            selection-color:rgb(0,220,0);
            selection-background-color: rgb(143,143,143);
            """)
        self.leftWidget.sendGalvanicDataLineEdit.setButtonSymbols(QtGui.QAbstractSpinBox.NoButtons)

        VoltageLayout_one.addWidget(self.leftWidget.sendVoltageDataLineEdit )
        VoltageLayout_one.addWidget(self.leftWidget.sendVoltageDataButton )
        GalvanicLayout_one.addWidget(self.leftWidget.sendGalvanicDataLineEdit)
        GalvanicLayout_one.addWidget(self.leftWidget.sendGalvanicDataButton)

        VoltageLayout_one.setContentsMargins(3,0,0,0)
        GalvanicLayout_one.setContentsMargins(3,0,0,0)
        # startStopLayout.setContentsMargins(3,0,0,0)

        self.verticalLayout.addLayout(startStopLayout)
        self.verticalLayout.addLayout(VoltageLayout_one )
        self.verticalLayout.addLayout(GalvanicLayout_one)
        
        # 输入框 Over ---------------------------------
        # 启动暂停按钮
        self.startButton = PushButton(u'启动',self.leftWidget)
        self.stopButton = PushButton(u'暂停',self.leftWidget)
        self.startButton.clicked.connect(self.requestStartData)
        self.stopButton.clicked.connect(self.requestStopData)
        startStopLayout.addWidget(self.startButton)
        startStopLayout.addWidget(self.stopButton)
        # 启动暂停按钮 Over

        self.verticalLayout.addWidget(self.tipLabel)
        self.verticalLayout.addWidget(self.statusLabel)
        self.verticalLayout.setContentsMargins(3,2,3,3)

        # 窗口伸缩控件
        self.verticalLayout.addItem(QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))
        self.verticalLayout.addWidget(QtGui.QSizeGrip(self))

        self.leftWidget.setLayout(self.verticalLayout)

        self.grid.addWidget(self.leftWidget.testButton,0,1) # 行 列
        self.grid.addWidget(self.comboBox,0,0)
        self.grid.addWidget(self.baudrateComboBox,1,0)
        self.grid.addWidget(self.baudrateLabel,1,1)
        self.grid.addWidget(self.bytesizeComboBox,2,0)
        self.grid.addWidget(self.bytesizeLabel,2,1)
        self.grid.addWidget(self.stopbitsComboBox,3,0)
        self.grid.addWidget(self.stopbitsLabel,3,1)

        self.grid.setContentsMargins(5,10,5,5) # 显示边距

        # ----------------------------------------------------------------------------

        self.content_splitter = QtGui.QSplitter()
        self.content_splitter.setSizePolicy(QtGui.QSizePolicy.Expanding,QtGui.QSizePolicy.Expanding)
        self.content_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.content_splitter.setHandleWidth(1)
        self.content_splitter.setStyleSheet("QSplitter.handle{background:lightgray}")
        # self.content_splitter.setStyleSheet("""border:1px solid red""")

        # 容纳主部件的 widget
        self.contentWidget = QtGui.QMainWindow()
        self.content_splitter.addWidget(self.leftWidget)
        self.content_splitter.addWidget(self.contentWidget)
        # 主 Layout
        self.main_layout = QtGui.QVBoxLayout()
        # self.content_splitter.setStyleSheet("""border:1px solid red""")
        # self.main_layout.addWidget(self.titlebar)
        self.main_layout.addWidget(self.content_splitter)        
        self.main_layout.setSpacing(0) # 间距     # layout.addStretch() 弹簧
        self.main_layout.setContentsMargins(10,7,10,7)
        # 主窗口底层
        self.widget = QtGui.QWidget()
        self.setCentralWidget(self.widget)
        self.widget.setLayout(self.main_layout)
        
        # 窗口伸缩问题
        # self.main_layout.addWidget(QtGui.QSizeGrip(self));


        # 窗口属性
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.desktop = QtGui.QApplication.desktop()
        self.LeftButtonPreesed = 0
        self.resize(1000,650)
        self.center(1) # 居中显示

        # 表格界面
        self.PlotWidget = pyqtgraph.GraphicsWindow() # QtGui.QWidget()
        self.PlotWidget.setWindowOpacity(0)
        self.contentWidget.setCentralWidget(self.PlotWidget)
        
        # 黑色前景色
        # pyqtgraph.setConfigOption('foreground',(255,255,255))
        # useOpenGL
        # pyqtgraph.setConfigOption('useOpenGL',True)
        # 抗锯齿
        # pyqtgraph.setConfigOption('antialias',True)

        # http://www.pyqtgraph.org/documentation/functions.html#pyqtgraph.mkPen
        # 画笔 颜色 宽度 美化？
        # self.greenPen = pyqtgraph.mkPen((0,220,0), width=1.2,cosmetic=True,style=QtCore.Qt.SolidLine)
        self.greenPen = pyqtgraph.mkPen((0,220,0), width=1.2,cosmetic=False,style=QtCore.Qt.SolidLine)

        # 上层第一个电压图表
        # http://localhost:7464/pyqtgraph.graphicsItems.PlotItem.PlotItem.html
        self.upPlot = self.PlotWidget.addPlot()
        # self.upPlot.setLimits(xMax=350) # X轴显示最大值
        self.upPlot.showGrid(x=True, y=True) #网格
        
        self.data = np.random.normal(size=300)
        self.lastestData = 0
        
        # self.upCurve = self.upPlot.plot(self.data, pen=self.greenPen)
        self.upPlot.setLabel('bottom', text=u'时间', units='s',unitPrefix='test')
        self.upPlot.setLabel('left', text=u'电压', units='V')
        self.upPlot.setTitle(u'电压信号图')
        # self.upPlot.setRange(xRange=[0, 350])   #坐标默认显示的区间

        # 换行画图
        self.PlotWidget.nextRow()

        # 下层第二个电流图表
        self.downPlot = self.PlotWidget.addPlot()
        self.downPlot.showGrid(x=True, y=True)
        # antialias抗锯齿
        # self.downCurve = self.downPlot.plot(self.data, pen=self.greenPen)#antialias=True)
        self.downPlot.setLabel('bottom', text=u'时间', units='s')
        self.downPlot.setLabel('left', text=u'电流', units='A')
        self.downPlot.setTitle(u'电流信号图')
        self.downPlot.setRange(yRange=[0,30])

        # self.PlotWidget.setBackground((252,252,252))#QtGui.QBrush(QtGui.QColor(255,255,255,255)))

        # -------------------------------------------------------------------------------
        self.galvanicData = [] # 电流数据
        self.voltageData = []  # 电压数据
        self.lastestGalvanicData = 0 # 最新电流数据
        self.lastestVoltageData = 0  # 最新电压数据
        self.serialDataString = ""  # 所有的数据字符串
        self.serialDataCursor = 0 # 数据指针
        self.serialDataList = [] # 数据存储列表
        self.stopUpdateGalvanicDataFlag = 1 # 电流暂停标志
        self.stopUpdateVoltageDataFlag = 1 # 电压暂停标志        
        # 输出系统信息 ----------------------------------------------------------------------
        print pyqtgraph.systemInfo()

        # 窗口按钮 Grid 此布局利用QtDesign设计代码移入-----------------------------------
        self.gridLayout = QtGui.QGridLayout(self.PlotWidget)
        self.gridLayout.setMargin(0)  # 间距
        self.gridLayout.setSpacing(0) # 间距
        # 最大化按钮
        self.maxPushButton = labelBtn(u'max',self.PlotWidget)
        self.maxPushButton.setPixmap(QtGui.QPixmap(r'./maxNormal.png'))
        self.maxPushButton.Entered.connect(self.buttonEnterFunc)
        self.maxPushButton.Leaved.connect(self.buttonLeavedFunc)
        self.maxPushButton.Clicked.connect(self.maxFunc)
        self.gridLayout.addWidget(self.maxPushButton, 0, 2, 1, 1)
        # 关闭按钮
        self.closePushButton = labelBtn(u'close',self.PlotWidget)
        self.closePushButton.setPixmap(QtGui.QPixmap(r'./closeNormal.png'))
        self.closePushButton.Entered.connect(self.buttonEnterFunc)
        self.closePushButton.Leaved.connect(self.buttonLeavedFunc)
        self.closePushButton.Clicked.connect(self.closeFunc)
        self.gridLayout.addWidget(self.closePushButton, 0, 3, 1, 1)

        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding) # 两个弹簧控件
        self.gridLayout.addItem(spacerItem, 1, 3, 1, 1) # 行 列
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem2, 0, 0, 1, 1)
        # 最小化按钮
        self.minPushButton = labelBtn(u'min',self.PlotWidget)
        self.minPushButton.Entered.connect(self.buttonEnterFunc)
        self.minPushButton.Leaved.connect(self.buttonLeavedFunc)
        self.minPushButton.Clicked.connect(self.minFunc)
        self.minPushButton.setPixmap(QtGui.QPixmap(r'./minNormal.png'))
        self.gridLayout.addWidget(self.minPushButton, 0, 1, 1, 1)
        # 窗口按钮Over ------------------------------------------------------------------        
        # QtDesign设计的两个lable布局------------------------------------------------------------------------------- 

        self.gridLayout2 = QtGui.QGridLayout()

        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout2.addItem(spacerItem, 6, 1, 1, 1)
        self.label = QtGui.QLabel(u'     ',self.PlotWidget)
        self.gridLayout2.addWidget(self.label, 1, 0, 1, 1)
        spacerItem1 = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout2.addItem(spacerItem1, 2, 1, 1, 1)
        self.label_3 = QtGui.QLabel(self.PlotWidget)
        self.gridLayout2.addWidget(self.label_3, 0, 0, 1, 1)
        self.label_2 = QtGui.QLabel(u'     ',self.PlotWidget)
        self.gridLayout2.addWidget(self.label_2, 4, 0, 1, 1)
        self.label_4 = QtGui.QLabel(self.PlotWidget)
        self.gridLayout2.addWidget(self.label_4, 3, 0, 1, 1)
        spacerItem2 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout2.addItem(spacerItem2, 3, 1, 1, 1)

        self.gridLayout.addLayout(self.gridLayout2, 1, 0, 1, 1)

        self.label.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.label.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.label_2.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.label_2.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)        
        self.label_3.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.label_3.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.label_4.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.label_4.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        self.font = QtGui.QFont()
        self.font.setPixelSize(60)   #设置字号32,以像素为单位

        print self.font.family()
        QtGui.QFontDatabase.addApplicationFont("MiuiEx-Light.ttf");
        self.font.setFamily("MIUI EX")
        print self.font.family()
        for i in QtGui.QFontDatabase.families(QtGui.QFontDatabase()):
            # print i.toUtf8()
            pass

        # self.font.setFamily("SimSun") #设置字体
        # self.font.setWeight(1)     #设置字型,不加粗

        self.label.setStyleSheet("color:rgb(0,220,0)")
        self.label.setFont(self.font)
        self.label_2.setStyleSheet("color:rgb(0,220,0)")
        self.label_2.setFont(self.font)

        # --------------------------------------------------------------------------------
        # Connect Event 串口接收信号与槽连接-----------------------------------------------------------------
        self.connect(self.serial.qObj, QtCore.SIGNAL('SerialRecvData'), self.recvSerialData)
        '''电压指令'''
        self.leftWidget.sendVoltageDataButton.clicked.connect(self.requestVoltageData)
        '''电流指令'''
        self.leftWidget.sendGalvanicDataButton.clicked.connect(self.requestGalvanicData)        

        # Timer To ADD AblePort
        self.timer = QtCore.QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.timerTaskForSearchSeries)
        self.timer.start(0) # Start Now
        
        # self.setFocusProxy()
        self.setFocus()

    def timerTaskForSearchSeries(self):
        '''单时钟线程扫描串口'''
        self.serial.checkPort()
        index = 0
        for i in self.serial.getPort(): # 识别可用的串口
            self.comboBox.addItem(i)
            if i == self.port:
                self.comboBox.setCurrentIndex(index)
            index += 1
        # self.soundThread.stopPlay()
        # self.soundThread.selectPort.play()        

    def getSetting(self):
        '''获取应用设置'''
        self.settings = QtCore.QSettings("setting.ini", QtCore.QSettings.IniFormat)

        if self.settings.value('UpMachine/setting/geometry', None): # 窗口位置
            self.restoreGeometry(self.settings.value("UpMachine/setting/geometry").toByteArray());
        self.port = self.settings.value('UpMachine/setting/port', None).toString()         # 端口
        self.baudrate = self.settings.value('UpMachine/setting/baudrate', 9600).toString() # 波特率
        self.bytesize = self.settings.value('UpMachine/setting/bytesize', 8).toString()    # 数据位数
        self.stopbits = self.settings.value('UpMachine/setting/stopbits', 1).toString()    # 停止位        

    def saveSettings(self):
        '''保存应用设置'''
        self.settings.setValue('UpMachine/setting/geometry', self.saveGeometry()) # 窗口位置
        self.settings.setValue('UpMachine/setting/port', self.comboBox.currentText().toUtf8().data()) # 端口
        self.settings.setValue('UpMachine/setting/baudrate', int(self.baudrateComboBox.currentText().toUtf8().data()))   # 波特率
        self.settings.setValue('UpMachine/setting/bytesize', int(self.bytesizeComboBox.currentText().toUtf8().data()))   # 数据位数
        self.settings.setValue('UpMachine/setting/stopbits', float(self.stopbitsComboBox.currentText().toUtf8().data())) # 停止位

    def requestData(self):
        # data = ['AA','55','02','FE','01','00'] # AA 55 02 FE 01 00
        # for d in data:            
        #     self.serial.send(d)
        # self.serial.send((binascii.b2a_hex('AA5502FE0100')).decode('hex'))
        
        # For RS232
        # self.serial.send(('AA5502FE0100').decode('hex'))
        
        # For RS485
        self.serial.send(('0803000000018493').decode('hex')) # 查询数据
        time.sleep(0.1)
        self.serial.send(('0903000000018542').decode('hex')) # 查询数据

    def crcSum(self,dataTemp):
        temp = ""
        while dataTemp:
            temp += struct.pack('<H', int(dataTemp[:2],16))[0:1]
            dataTemp = dataTemp[2:]
        crc = ("{:10X}".format(CRC16(modbus_flag = True).calculate(temp)))[-4:] 
        crcL  = crc[-2:]
        crcH  = crc[-4:-2]
        return crcL + crcH

    def requestStartData(self):
        """发送启动数据"""
        data = "1203020000"
        data = data + self.crcSum(data)
        print data
        self.serial.send(data.decode('hex'))

    def requestStopData(self):
        """发送停机数据"""
        data = "1303020000"
        data = data + self.crcSum(data)
        print data
        self.serial.send(data.decode('hex'))

    def requestVoltageData(self):
        '''发送电压请求数据'''
        print self.leftWidget.sendVoltageDataLineEdit.value()
        data = "10030200"+HEX(int(self.leftWidget.sendVoltageDataLineEdit.value()))
        # data = "10030200"+HEX(self.leftWidget.sendVoltageDataLineEdit.value())
        data = data + self.crcSum(data)
        print data
        self.serial.send(data.decode('hex'))

    def requestGalvanicData(self):
        '''发送电流请求数据'''
        print self.leftWidget.sendGalvanicDataLineEdit.value()
        data = "11030200"+HEX(int(self.leftWidget.sendGalvanicDataLineEdit.value()))
        data = data + self.crcSum(data)
        print data
        self.serial.send(data.decode('hex'))

    def recvSerialData(self, data):        
        # codec = QtCore.QTextCodec.codecForName('GBK')
        # data = filter(self._filterChar, data)
        # data = buffToHex(data).replace('\n',' ')
        print data
        dataList = data.split(' ')
        
        # For RS485
        self.serialDataString += data.replace(" ","")
        self.analysis()        
        
        for i in self.serialDataList:
            num = int(i[6:10],16) # 500 = 0x01F4
            if i.startswith("08"):
                if num == 65535:
                    num = -1
                else:
                    if num > 500:
                        num = num - 65535                
                self.updataVoltageData(num)                
                print u"电压表",num
            elif i.startswith("08"):
                # 090302 03 43 1884
                num = num/100.0
                if num == 65535:
                    num = -1
                else:
                    if num > 500:
                        num = num - 65535
                self.updataGalvanicData(num)
                print u"电流表",num

            elif i.startswith("14"):
                '''
                状态数据 14 03 02 00 XX crcL crcH
                                     00 充电
                                     01 放电
                                     02 闲置
                                     03 待机
                                     04 错误
                '''
                if i[8:10] == "00":
                    self.statusLabel.setText("充电")
                elif i[8:10] == "01":
                    self.statusLabel.setText("放电")
                elif i[8:10] == "02":
                    self.statusLabel.setText("闲置")
                elif i[8:10] == "03":
                    self.statusLabel.setText("待机")
                elif i[8:10] == "04":
                    self.statusLabel.setText("错误")
            else:
                print '未知数据'

        self.serialDataList = []

        # For RS232
        # num = int(dataList[5]+dataList[4],16)
        # print num
        # self.updataGalvanicData(num)

        '''
        AA 55 04 F6 00 00 00 FA 
        AA 55 04 F6 1A 00 01 14
        int('001A',16) = 26
        双字节有符号型(SIGNED SHORT)型测量值，低位在前，在三位半表里其范围为 -1999~1999，
        在四位半表里其范围为 -19999~19999，具体值等于实际测量值乘以 10 的 N 次方，
        N 根据每个表头的情况而定，
        假设① 2V 四位半表，N = 4， 即返回值为 19990 时表示 19990 = 1.9990(V) *    ，
        ② 200mV 四位半表，N = 2，即 19990 = 199.90(mV) *    ，
        ③ 6V 四位半表，N = 3，即 6000 = 6.000(V) *    ，
        ④ 2V 三位半表，N = 3，即 1999 = 1.999(V) *    ；
        当测量为“OL”时返 回[00 80 = 0x8000 = -32768]
        '''

    def analysis(self):
        newData = self.serialDataString[self.serialDataCursor:]  
        # print newData
        regex = re.compile(r'\w{2}0302\w{8}')

        result = regex.search(newData)
        if result:            
            if self.dataTest(result.group()):
                self.serialDataCursor += len(result.group())
                print result.group()+" Right Data"
                self.serialDataList.append(result.group())
            else:
                self.serialDataCursor += 6 # 6=\w{2}+0302
                print result.group()+" Wrong Data"
                self.analysis()                
        else:
            print "Find Failed",newData
        
    def dataTest(self,data):
        dataTemp = data[:-4]
        temp = ""
        while dataTemp:
            temp += struct.pack('<H', int(dataTemp[:2],16))[0:1]
            dataTemp = dataTemp[2:]

        crc = ("{:10X}".format(CRC16(modbus_flag = True).calculate(temp)))[-4:] 
        crcL  = crc[-2:]
        crcH  = crc[-4:-2]

        if crcL+crcH == data[-4:]:
            return True
        else:
            return False

    def _filterChar(self, c): 
        '''Just for delete inexplicable newline'''
        return c != '\r'

    def stopUpdataGalvanicData(self):
        # 电流表暂停刷新
        if self.stopUpdateGalvanicDataFlag:
            self.stopUpdateGalvanicDataFlag = 0
            self.leftWidget.stopUpdataGalvanicDataButton.setText(u"电流表开始刷新")
        else:
            self.stopUpdateGalvanicDataFlag = 1
            self.leftWidget.stopUpdataGalvanicDataButton.setText(u"电流表暂停刷新")

    def stopUpdataVoltageData(self):
        # 电压表暂停刷新
        if self.stopUpdateVoltageDataFlag:
            self.stopUpdateVoltageDataFlag = 0
            self.leftWidget.stopUpdataVoltageDataButton.setText(u"电压表开始刷新")
        else:
            self.stopUpdateVoltageDataFlag = 1
            self.leftWidget.stopUpdataVoltageDataButton.setText(u"电压表暂停刷新")

    def updataGalvanicData(self,data):
        # self.galvanicData[self.lastestGalvanicData] = data        
        self.galvanicData.append(data)        
        if self.stopUpdateGalvanicDataFlag: # 电流暂停标志        
            self.label_2.setText(u'     '+str(data))
            self.lastestGalvanicData += 1
            self.downPlot.setRange(xRange=[self.lastestGalvanicData-30, self.lastestGalvanicData])
            self.downPlot.plot(pen=self.greenPen).setData(self.galvanicData[:self.lastestGalvanicData])

    def updataVoltageData(self,data):       
        self.voltageData.append(data)        
        if self.stopUpdateVoltageDataFlag: # 电压暂停标志
            self.label.setText(u'     '+str(data))
            self.lastestVoltageData += 1
            self.upPlot.setRange(xRange=[self.lastestVoltageData-30, self.lastestVoltageData])
            self.upPlot.plot(pen=self.greenPen).setData(self.voltageData[:self.lastestVoltageData])

    def update2(self,Data):
        '''模拟数据更新函数'''
        '''self.galvanicData
           self.voltageData '''
        self.data[self.lastestData] = Data # np.random.normal()

        self.lastestData += 1

        self.upPlot.setRange(xRange=[self.lastestData-30, self.lastestData])
        self.downPlot.setRange(xRange=[self.lastestData-30, self.lastestData])

        self.upPlot.plot(pen=self.greenPen).setData(self.data[:self.lastestData])
        self.downPlot.plot(pen=self.greenPen).setData(self.data[:self.lastestData])

        # self.upPlot.plot(pen=self.greenPen).setPos(self.lastestData-30,self.lastestData)

    def updateSerial(self):
        '''刷新可用的串口'''
        self.comboBox.clear()
        self.serial.checkPort()
        for i in self.serial.getPort():
            self.comboBox.addItem(i)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            self.LeftButtonPreesed = 1
            event.accept()

    def mouseReleaseEvent(self,event):
        self.LeftButtonPreesed = 0

    def mouseMoveEvent(self, event):
        if event.buttons() == QtCore.Qt.LeftButton:
            if self.LeftButtonPreesed:
                self.move(event.globalPos() - self.dragPosition)

    def paintEvent(self,event):
        '''窗口阴影'''
        p = QtGui.QPainter(self)
        if not self.isMaxShow:
            p.drawPixmap(0, 0, self.rect().width(), self.rect().height(), QtGui.QPixmap('main_shadow.png'))

    def keyPressEvent(self,event):
        # F11全屏切换
        if event.key()==QtCore.Qt.Key_F11:
            self.maxFunc("JustMaxName")
        if event.key()==QtCore.Qt.Key_F5:
            self.timerTaskForSearchSeries()
        if event.key()==QtCore.Qt.Key_Return:
            self.app.sendEvent(self.leftWidget.linkButton,QtCore.QEvent.KeyPress)
        if event.key()==QtCore.Qt.Key_Space:            
            self.stopUpdataGalvanicData()
            self.stopUpdataVoltageData()
            event.accept()

    def center(self,screenNum=0):
        '''多屏居中支持 居中显示在第screenNum个屏幕'''
        screen = self.desktop.availableGeometry(screenNum)
        size = self.geometry()
        self.normalGeometry2 = QtCore.QRect((screen.width()-size.width())/2+screen.left(),
                         (screen.height()-size.height())/2,
                         size.width(),size.height())
        self.setGeometry((screen.width()-size.width())/2+screen.left(),
                         (screen.height()-size.height())/2,
                         size.width(),size.height())

    def maxFunc(self,name):
        '''切换窗口模式'''
        if self.isMaxShow:
            self.main_layout.setContentsMargins(10,7,10,7)
            self.showNormal()           
            self.isMaxShow = 0
        else:
            self.main_layout.setContentsMargins(0,0,0,0)            
            self.showMaximized()
            self.isMaxShow = 1

    def minFunc(self,name):
        '''最小化函数'''
        self.PlotWidget.hide()
        # self.minPushButton.setPixmap(QtGui.QPixmap(r'./minNormal.png'))
        self.minAnimation = QtCore.QPropertyAnimation(self,"windowOpacity")
        self.minAnimation.finished.connect(self.showMinimized2)
        self.minAnimation.setDuration(200)
        self.minAnimation.setStartValue(1)
        self.minAnimation.setEndValue(0)        
        self.minAnimation.start()      

    def closeFunc(self,name):
        '''窗口关闭函数'''
        self.closeAnimation = QtCore.QPropertyAnimation(self,"windowOpacity")
        self.closeAnimation.setDuration(200)
        self.closeAnimation.setStartValue(1)
        self.closeAnimation.setEndValue(0)
        self.closeAnimation.finished.connect(self.exitFunc)
        self.closeAnimation.start()

    def buttonEnterFunc(self,name):
        '''按钮鼠标进入事件'''
        exec(str(('self.' + name + 'PushButton.setPixmap(QtGui.QPixmap(r"./' + name + '.png"))').toUtf8()))

    def buttonLeavedFunc(self,name):
        '''按钮鼠标离开事件'''
        exec(str(('self.' + name + 'PushButton.setPixmap(QtGui.QPixmap(r"./' + name + 'Normal.png"))').toUtf8()))

    def exitFunc(self):
        '''全部退出'''        
        # self.saveSettings()
        # self.disconnectSerial()
        
        # self.soundThread.stopPlay()
        # self.soundThread.seeYou.play() # 此句可能听不到
        self.close()
        # QtCore.QCoreApplication.instance().quit() 
        # sys.exit() # 用此法终止程序QSetting不会运行保存方法

    def showEvent(self,event):    
        self.PlotWidget.show()
        self.animation = QtCore.QPropertyAnimation(self,"windowOpacity")
        self.animation.setDuration(100)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

    def showMinimized2(self):
        self.setWindowOpacity(1)
        self.showMinimized()

    def closeEvent(self, event):
        '''窗口关闭事件'''
        self.saveSettings()
        self.disconnectSerial()        
        event.accept()

    def disconnectSerial(self):
        self.timer.stop()
        self.serial.turnOff()
        # self.soundThread.stopPlay()
        # self.soundThread.disconnect.play()
        self.tipLabel.setText('Disconnect Success')
        self.leftWidget.linkButton.setText(u'连接串口')
        self.statusLabel.setText("        ")
        self.leftWidget.linkButton.clicked.connect(self.connectSerial)
        try:
            self.leftWidget.linkButton.clicked.disconnect(self.disconnectSerial)
        except Exception, e:
            print e        

    def connectSerial(self):
        # self.serial.setting['port'] = self.portComboBox.currentText().toUtf8().data() # comboBox
        self.serial.setting['port']     = self.comboBox.currentText().toUtf8().data()
        self.serial.setting['baudrate'] = int(self.baudrateComboBox.currentText().toUtf8().data())
        self.serial.setting['bytesize'] = int(self.bytesizeComboBox.currentText().toUtf8().data())
        self.serial.setting['stopbits'] = float(self.stopbitsComboBox.currentText().toUtf8().data())
        # parity_name = self.parityComboBox.currentText().toUtf8().data()
        parity_name = serialutil.PARITY_NAMES
        for i in SerialDev.PARITY_NAMES:
            if parity_name == SerialDev.PARITY_NAMES[i]:
                self.serial.setting['parity'] = i
        is_connect, msg = self.serial.turnOn(self.serial.setting['port'], 
                                             self.serial.setting['baudrate'], 
                                             self.serial.setting['bytesize'], 
                                             self.serial.setting['stopbits'], 
                                             self.serial.setting['parity'])
        if is_connect:         
            print 'Connect Success'
            # self.soundThread.stopPlay()
            # self.soundThread.connectSuccess.play()   
            self.tipLabel.setText('Connect Success')
            self.leftWidget.linkButton.setText(u'断开串口')
            self.leftWidget.linkButton.clicked.disconnect(self.connectSerial)
            self.leftWidget.linkButton.clicked.connect(self.disconnectSerial)

            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.requestData)
            self.timer.start(1000)
            # self.done(settingSerialDialog.CONNECT)
        else:
            QtGui.QMessageBox.information(self,
                                          'Connect serial', 
                                          'Connect serial fail!\n%s' % (msg), 
                                           QtGui.QMessageBox.Ok, 
                                           QtGui.QMessageBox.Ok)

class PushButton(QtGui.QPushButton):
    def __init__(self,text,parent=None):
        super(PushButton,self).__init__()
        self.text = text
        self.setText(self.text)

    def keyPressEvent(self,event):        
        event.ignore()

# 图标按钮类重写类
class labelBtn(QtGui.QLabel):
    Clicked = QtCore.pyqtSignal(str)
    Entered = QtCore.pyqtSignal(str)
    Leaved = QtCore.pyqtSignal(str)
    Moved = QtCore.pyqtSignal(str,int,int)

    def __init__(self,name,timeoutset=None,parent=None):
        super(labelBtn,self).__init__()
        self.setMouseTracking(True)
        self.name = name
            
    def mouseReleaseEvent(self,event):
        self.Clicked.emit(self.name)
        
    def mouseMoveEvent(self,event):
        self.Moved.emit(self.name,event.globalPos().x(),event.globalPos().y())
        
    def enterEvent(self,event):
        self.Entered.emit(self.name)
   
    def leaveEvent(self,event):
        self.Leaved.emit(self.name)

# 输入框类重写类
class LineEdit(QtGui.QLineEdit):
    def __init__(self):
        super(LineEdit,self).__init__()

    def keyPressEvent(self,event):
        print event.key()

class SoundThread(QtCore.QThread):
    def __init__(self, parent = None):
        '''write is a function that printf the data of serial.'''
        super(SoundThread, self).__init__(parent)

        self.selectPort     = None
        self.connectSuccess = None
        self.disconnect     = None
        self.seeYou         = None

    def stopPlay(self):
        for music in [self.selectPort,self.connectSuccess,self.disconnect,self.seeYou]:
            if music:
                try:
                    music.stop()
                except Exception, e:
                    print e                

    def run(self):
        self.selectPort  = mp3play.load("selcetPort.mp3")
        self.connectSuccess = mp3play.load("connectSuccess.mp3")
        self.disconnect  = mp3play.load("disconnect.mp3")
        self.seeYou      = mp3play.load("seeYou.mp3")
        
if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    testWidget = MainWindow(app)
    testWidget.setWindowOpacity(0)
    testWidget.show()
    sys.exit(app.exec_())
