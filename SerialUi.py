# -*- coding: utf-8 -*-

import sys
from PyQt4 import QtCore, QtGui
from SerialDev import SerialDev
            
class settingSerialDialog(QtGui.QDialog):
    CONNECT = 2     # Dialog self return 0 or 1
    
    def __init__(self, serial, parent=None):
        super(settingSerialDialog, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.Dialog)
        self.setWindowTitle('Setting of serial')
        
        self.serial = serial 
        self.port = self.serial.getPort()           
        self.__initSetUpUi()
        self.__initSetUpSignal()

    def __initSetUpUi(self):
        portLabal = QtGui.QLabel('port')
        self.portComboBox = QtGui.QComboBox()
        portLabal.setBuddy(self.portComboBox)
        baudrateLabal = QtGui.QLabel('baudrate')
        self.baudrateComboBox = QtGui.QComboBox()
        baudrateLabal.setBuddy(self.baudrateComboBox)
        bytesizeLabal = QtGui.QLabel('bytesize')
        self.bytesizeComboBox = QtGui.QComboBox()
        bytesizeLabal.setBuddy(self.bytesizeComboBox)
        stopbitsLabal = QtGui.QLabel('stopbits')
        self.stopbitsComboBox = QtGui.QComboBox()
        stopbitsLabal.setBuddy(self.stopbitsComboBox)
        parityLabal = QtGui.QLabel('parity')
        self.parityComboBox = QtGui.QComboBox()
        parityLabal.setBuddy(self.parityComboBox)
        self.connectButton = QtGui.QPushButton('connect')
        self.closeButton = QtGui.QPushButton('cancel')
        
        for i in self.port:
            self.portComboBox.addItem(i)
        self.portComboBox.setCurrentIndex(0)        
        index = 0
        for i in range(len(SerialDev.BAUDRATES)):
            self.baudrateComboBox.addItem(str(SerialDev.BAUDRATES[i]))
            if SerialDev.BAUDRATES[i] == 115200:
                index = i
        self.baudrateComboBox.setCurrentIndex(index)
        index = 0
        for i in range(len(SerialDev.BYTESIZES)):
            self.bytesizeComboBox.addItem(str(SerialDev.BYTESIZES[i]))
            if SerialDev.BYTESIZES[i] == SerialDev.SETTING.EIGHTBITS:
                index = i
        self.bytesizeComboBox.setCurrentIndex(index)
        index = 0
        for i in range(len(SerialDev.STOPBITS)):
            self.stopbitsComboBox.addItem(str(SerialDev.STOPBITS[i]))
            if SerialDev.STOPBITS[i] == SerialDev.SETTING.STOPBITS_ONE:
                index = i
        self.stopbitsComboBox.setCurrentIndex(index)   
        index, j = 0, 0    
        for i in SerialDev.PARITY_NAMES:
            self.parityComboBox.addItem(SerialDev.PARITY_NAMES[i])
            if SerialDev.PARITY_NAMES[i] == SerialDev.PARITY_NAMES[SerialDev.SETTING.PARITY_NONE]:
                index = j
            j += 1
        self.parityComboBox.setCurrentIndex(index)
          
        mainLayout = QtGui.QGridLayout()
        mainLayout.addWidget(portLabal, 0, 0, QtCore.Qt.AlignRight)    
        mainLayout.addWidget(self.portComboBox, 0, 1, QtCore.Qt.AlignLeft)
        mainLayout.addWidget(baudrateLabal, 1, 0, QtCore.Qt.AlignRight)    
        mainLayout.addWidget(self.baudrateComboBox, 1, 1, QtCore.Qt.AlignLeft)        
        mainLayout.addWidget(bytesizeLabal, 2, 0, QtCore.Qt.AlignRight)    
        mainLayout.addWidget(self.bytesizeComboBox, 2, 1, QtCore.Qt.AlignLeft)
        mainLayout.addWidget(stopbitsLabal, 3, 0, QtCore.Qt.AlignRight)    
        mainLayout.addWidget(self.stopbitsComboBox, 3, 1, QtCore.Qt.AlignLeft)
        mainLayout.addWidget(parityLabal, 4, 0, QtCore.Qt.AlignRight)    
        mainLayout.addWidget(self.parityComboBox, 4, 1, QtCore.Qt.AlignLeft)  
        mainLayout.addWidget(self.connectButton, 5, 0, QtCore.Qt.AlignLeft)
        mainLayout.addWidget(self.closeButton, 5, 1, QtCore.Qt.AlignLeft)          
        self.setLayout(mainLayout)
    
    def __initSetUpSignal(self):
        self.closeButton.clicked.connect(self.reject)
        self.connectButton.clicked.connect(self.connectSerial)
        
    def connectSerial(self):
        self.serial.setting['port'] = self.portComboBox.currentText().toUtf8().data()
        self.serial.setting['baudrate'] = int(self.baudrateComboBox.currentText().toUtf8().data())
        self.serial.setting['bytesize'] = int(self.bytesizeComboBox.currentText().toUtf8().data())
        self.serial.setting['stopbits'] = float(self.stopbitsComboBox.currentText().toUtf8().data())
        parity_name = self.parityComboBox.currentText().toUtf8().data()
        for i in SerialDev.PARITY_NAMES:
            if parity_name == SerialDev.PARITY_NAMES[i]:
                self.serial.setting['parity'] = i
        is_connect, msg = self.serial.turnOn(self.serial.setting['port'], 
                                             self.serial.setting['baudrate'], 
                                             self.serial.setting['bytesize'], 
                                             self.serial.setting['stopbits'], 
                                             self.serial.setting['parity'])
        if is_connect:
            self.done(settingSerialDialog.CONNECT)
        else:
            QtGui.QMessageBox.information(self,
                                          'Connect serial', 
                                          'Connect serial fail!\n%s' % (msg), 
                                           QtGui.QMessageBox.Ok, 
                                           QtGui.QMessageBox.Ok)
    
class SerialTextEdit(QtGui.QTextBrowser):
    def __init__(self, serial, status_tip, parent = None):
        super(SerialTextEdit, self).__init__(parent)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setUndoRedoEnabled(False)
        self.setReadOnly(False)
        self.setUndoRedoEnabled(False)
        self.setLineWidth(5)
        
        self.setCursorWidth(9)
        font = QtGui.QFont()
        font.setPointSize(9)
        self.setFont(font)
        
        self.serial = serial
        self.__statusTip = status_tip
        self._clicked = False
        self._clickSaveData = ''
        self._onPrintData = False
        
    def mousePressEvent(self, e):
        if e.button() & (QtCore.Qt.RightButton | QtCore.Qt.MiddleButton):
            self.tc = self.textCursor()
            self.copy()
        super(SerialTextEdit, self).mousePressEvent(e)
        self._clicked = True
        self.__statusTip(SerialUi.TIP_MSG['Operate/StopReceive'])    
    
    def mouseReleaseEvent(self, envent):
        self._clicked = False
        self.tc = self.textCursor()
        select_str = self.tc.selectedText()
        status_copy = False
        omit = ''
        if select_str != '':
            self.copy()
            
            status_copy = True
            if len(select_str) > 10:
                select_str = select_str[0:10]
                omit = '...'
            status_msg = '''"%s%s" %s'''% (select_str, omit, SerialUi.TIP_MSG['Operate/CopyData'])
            self.__statusTip(status_msg)
        
        if not status_copy:
            self.__statusTip(SerialUi.TIP_MSG['Operate/RecoverReceive'])
        
        if self._clickSaveData != '' and not self._onPrintData:
            recvData = self._clickSaveData[0:]
            self._clickSaveData = ''
            self._onPrintData = True
            self._setEndCursor()
            self._insertText(recvData) 
            self.vsb = self.verticalScrollBar()
            self.vsb.setSliderPosition(self.vsb.maximum())   
            self._onPrintData = False
            
            
                                          
    def keyPressEvent(self, e):
        if e.modifiers() == QtCore.Qt.ControlModifier and e.key() == QtCore.Qt.Key_C:
            super(SerialTextEdit, self).keyPressEvent(e)
        if self.serial.getOpen():
            self.serial.send(e.text())
            status_msg = "'%s' %s" % (e.text(), SerialUi.TIP_MSG['Operate/SendData'])
            self.__statusTip(status_msg)
        else:
            QtGui.QMessageBox.information(self,
                              'error', 
                              'Send data to serial error! \nSerial is not be connect.', 
                               QtGui.QMessageBox.Ok, 
                               QtGui.QMessageBox.Ok)

    def contextMenuEvent(self, e):
        '''Delete right key menu'''
        pass
    
    def _filterChar(self, c): 
        '''Just for delete inexplicable newline'''
        return c != '\r'
    
    def _setEndCursor(self):
        self.tc = self.textCursor()
        if not self.tc.atEnd():
            self.tc.movePosition(self.tc.End)
            self.setTextCursor(self.tc)   
     
    def _insertText(self, data): 
        for c in data:   
            self.tc = self.textCursor()
            self.tc.clearSelection()
            self.tc.movePosition(self.tc.End)
#             if c != '\r':
            self.tc.insertText(c)        

    def printSerialData(self, data):
#         codec = QtCore.QTextCodec.codecForName('GBK')
        data = filter(self._filterChar, data)
        if self._clicked:
            self._clickSaveData += data
        else:
            self._setEndCursor()
            self._insertText(data)
            for c in data:
                if c == '\n':
                    self.vsb = self.verticalScrollBar()
                    self.vsb.setSliderPosition(self.vsb.maximum())   

def statusPicButton(msg):
    pass

class PicButton(QtGui.QPushButton):
    def __init__(self, icon, status_tip=statusPicButton, status_msg='', parent = None):
        super(PicButton, self).__init__(parent)
#         self.setStyleSheet('QPushButton{background-color:#da00cd;}')
        self.icon = icon
#         self.setIcon(icon)
        self.statusTip = status_tip
        self.statusMsg = status_msg
        self.setMouseTracking(True)
#         self.buttonPicture = QtGui.QPixmap()
        self.setFlat(True) 
        
    def setButtonPicture(self, pic):
        print 'setButtonPicture'
        pass
    
    def setPressPicture(self, pic):
        print 'setPressPicture'
        pass
    
    def setReleasePicture(self, pic):
        print 'setReleasePicture'
        pass
    
    def setButtonGeometry(self, pic):
        print 'setButtonGeometry'
        pass

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
#         pen = QtGui.QPen()
#         painter.setPen(pen)
#         self.brush.setStyle(QtCore.Qt.SolidPattern)
        brush = QtGui.QBrush(QtCore.Qt.darkGray, QtCore.Qt.SolidPattern)
#         brush.setColor(QtCore.Qt.darkGray)
        painter.setBrush(brush)
        painter.fillRect(self.rect(), QtCore.Qt.SolidPattern)
        image = QtGui.QImage()
        image.load(self.icon)
        painter.drawImage(self.rect(), image)
#         self.setIcon(self.icon)
        print 'paintEvent'
        pass
        
    def mouseDoubleClickEvent(self, event):
        print 'mouseDoubleClickEvent'
        pass
    
    def mousePressEvent(self, event):
        print 'mousePressEvent'
        pass
    
    def mouseMoveEvent(self, event):
        self.statusTip(self.statusMsg)
        print 'mouseMoveEvent'
        pass
    
    def mouseReleaseEvent (self, event):
        print 'mouseReleaseEvent'
        self.clicked.emit(True)
        pass
    
#         self.setButton.setFlat(True)
#         self.setButton.setIcon(QtGui.QIcon('./images/icon.ico'))
#         self.setButton.setIconSize(QtCore.QSize(48, 48))
#         self.setButton.setWindowOpacity(0.1)
      
class SerialUi(QtGui.QMainWindow):
    TIP_MSG = {'Ready': 'Ready',
               'Operate/Select': 'Select context',
               'Operate/CopyData': 'has been copied',
               'Operate/StopReceive': 'Stop receive data', 
               'Operate/RecoverReceive': 'Recover receive data', 
               'Operate/SendData': 'has been sent to serial', 
               'Button/Set': 'Set the serial',
               'Button/Connect/Yes': 'Serial has connected',
               'Button/Connect/No': 'Serial is not connect',
               'Button/Clear': 'Clear context',
               'Button/Status/On': 'Display status bar',
               'Button/Status/Off': 'Not Displayed status bar'
               }  
    
    def __init__(self, parent = None):
        super(SerialUi, self).__init__(parent)

        self.__defineVar()
        self.__initSetUpUi()
        self.__initSetUpSignal()
        self.__initLaunch()
         
        self.serialSetting = self.serial.setting
        
    def __defineVar(self):
        self.serial = SerialDev()

    def __setWindowAttribute(self):
        if self.__isLanuch:
            self.setMinimumSize(200, 50)
            self.setWindowTitle('OwonUtil serial')
            self.setGeometry(self.__geometry)
            self.setWindowIcon(QtGui.QIcon('./images/icon.ico'))
#         self.setWindowOpacity(1)
#         self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
#         self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        pass

        
    def __initSetUpUi(self):
#         self.setButton = PicButton('./images/icon.ico')
        self.setButton = QtGui.QPushButton('set')
        self.connectButton = QtGui.QPushButton('connect')
        self.clearButton = QtGui.QPushButton('clear')
#         self.fontButton = QtGui.QPushButton('font')
        self.opacityCheckBox = QtGui.QCheckBox('opacity')
        self.opacitySlider = QtGui.QSlider(QtCore.Qt.Horizontal)
        self.opacitySlider.setFixedWidth(50)
        self.opacitySlider.setRange(10, 100)
        self.stickCheckBox = QtGui.QCheckBox('stick')
        iconSpacerItem = QtGui.QSpacerItem(0, 0, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.textEdit = SerialTextEdit(self.serial, self.statusTipText)
        
        self.statusBar = QtGui.QStatusBar()
        self.statusBarTipLabel = QtGui.QLabel()
        self.statusBarTipLabel.setFixedWidth(230)
        self.statusBarSerialLabel = QtGui.QLabel()
        self.statusBar.addWidget(self.statusBarTipLabel, QtCore.Qt.AlignLeft)
        self.statusBar.addWidget(self.statusBarSerialLabel, QtCore.Qt.AlignRight)
        
        iconButtonLayout = QtGui.QHBoxLayout()
        iconButtonLayout.setSpacing(1)
        iconButtonLayout.addWidget(self.setButton)
        iconButtonLayout.addWidget(self.connectButton)
        iconButtonLayout.addWidget(self.clearButton)
#         iconButtonLayout.addWidget(self.fontButton)
        iconButtonLayout.addItem(iconSpacerItem)
        iconButtonLayout.addWidget(self.stickCheckBox)       
        iconButtonLayout.addWidget(self.opacityCheckBox)
        iconButtonLayout.addWidget(self.opacitySlider)
        
        mainLayout = QtGui.QGridLayout()
        mainLayout.addLayout(iconButtonLayout, 0, 0)
        mainLayout.addWidget(self.textEdit)
        mainLayout.addWidget(self.statusBar)
        mainLayout.setMargin(1)
        mainLayout.setSpacing(1)
        
        centralWidget = QtGui.QWidget()        
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)
#         self.setLayout(mainLayout)

    def __initSetUpSignal(self):
        self.setButton.clicked.connect(self.settingDialog)
        self.connectButton.clicked.connect(self.changeConnect)
        self.clearButton.clicked.connect(self.clearText)
        self.stickCheckBox.toggled.connect(self.__changeStick)
        self.opacityCheckBox.toggled.connect(self.__changeOpacity)
        self.opacitySlider.valueChanged.connect(self.__changeOpacity)
        self.connect(self.serial.qObj, QtCore.SIGNAL('SerialRecvData'), 
                     self.textEdit.printSerialData)
        
    def __initLaunch(self):
        self.__isLanuch = True
        
        self.statusTipText(SerialUi.TIP_MSG['Ready'])
        
        self.__settings = QtCore.QSettings("setting.ini", QtCore.QSettings.IniFormat)
        self.__geometry = self.__settings.value('OwonUtil/Serial/__geometry', 
                                            QtCore.QRect(950, 200, 400, 250)).toRect()
        self.__setWindowAttribute()
        
        self.__enableOpacity = self.__settings.value('OwonUtil/Serial/__enableOpacity', 
                                                     True).toBool()
        self.__opacity, b = self.__settings.value('OwonUtil/Serial/__opacity', 
                                                  0.7).toFloat()
        self.__changeOpacity()
        
        self.__enableStick = self.__settings.value('OwonUtil/Serial/__enableStick', 
                                                   True).toBool()
        self.__changeStick()
        
        self.__serialConnected = self.__settings.value('OwonUtil/Serial/__serialConnected',
                                                        True).toBool()
        self.changeConnect(self.__serialConnected)
        
        self.__isLanuch = False        
                
    def settingDialog(self):
        settingDialog = settingSerialDialog(self.serial, parent=self)
        if settingDialog.exec_() == settingDialog.CONNECT:
            self.__serialConnected = True
        self.updataConnect()    
        self.textEdit.setFocus()
    
    def updataConnect(self):
        if self.__serialConnected:
            self.connectButton.setText('disconnect')
            msg = 'serial: %s' % self.serial.setting['port']
        else:
            self.connectButton.setText('connect')
            msg = 'serial: disconnect'
        self.statusBarSerialLabel.setText(msg)
        self.textEdit.setFocus()
        
    def changeConnect(self, lanuch_set=False): 
        if not self.__serialConnected or lanuch_set:
            is_connect, msg = self.serial.turnOn(self.serial.setting['port'], 
                                                 self.serial.setting['baudrate'], 
                                                 self.serial.setting['bytesize'], 
                                                 self.serial.setting['stopbits'], 
                                                 self.serial.setting['parity'])
            if is_connect:
                self.__serialConnected = True
            else:
                QtGui.QMessageBox.about(self, 'Connect serial','Connect serial fail!\n%s' % (msg))
        else:
            self.__serialConnected = False
            self.serial.turnOff()
        self.updataConnect()    
        
    def disconnectSerial(self):
        self.serial.turnOff()
        
    def clearText(self):
        self.textEdit.clear()
        self.textEdit.setFocus()
    
    def statusTipText(self, msg):
        self.statusBarTipLabel.setText(msg)
        
    def __changeStick(self):
        if self.__isLanuch:
            if self.__enableStick:
                self.stickCheckBox.setCheckState(QtCore.Qt.Checked)
            else:
                self.stickCheckBox.setCheckState(QtCore.Qt.Unchecked)
                
        if not self.__isLanuch:
            self.hide()
        x, y= self.x(), self.y()
        if self.stickCheckBox.isChecked():
            self.__enableStick = True
            self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        else:
            self.__enableStick = False
            self.setWindowFlags(QtCore.Qt.Widget)
        self.move(x, y)
        self.__setWindowAttribute()
        if not self.__isLanuch:
            self.show()   
        
    def __changeOpacity(self):
        if self.__isLanuch:
            self.opacitySlider.setValue(int(self.__opacity*100))
            if self.__enableOpacity:
                self.opacityCheckBox.setCheckState(QtCore.Qt.Checked)
            else:
                self.opacityCheckBox.setCheckState(QtCore.Qt.Unchecked)
        if self.opacityCheckBox.isChecked():
            self.__enableOpacity = True            
            self.opacitySlider.setEnabled(True)
            self.__opacity = float(self.opacitySlider.value()) / 100
            self.setWindowOpacity(self.__opacity)
        else:
            self.__enableOpacity = False
            self.opacitySlider.setEnabled(False)
            self.setWindowOpacity(1.0)
         
    def __saveSettings(self):
        self.__settings.setValue('OwonUtil/Serial/__geometry', 
                                 self.geometry())
        self.__settings.setValue('OwonUtil/Serial/__enableOpacity', 
                                 self.__enableOpacity)
        self.__settings.setValue('OwonUtil/Serial/__opacity',
                                 self.__opacity)
        self.__settings.setValue('OwonUtil/Serial/__enableStick',
                                 self.__enableStick)
        self.__settings.setValue('OwonUtil/Serial/__serialConnected',
                                 self.__serialConnected)
        
    def closeEvent(self, e):
        self.__saveSettings()
        self.disconnectSerial()
        e.accept()

def main():
#     set = QtCore.QSettings("setting.ini", QtCore.QSettings.IniFormat)
#     s = QtCore.QString('yes')
#     set.setValue("animal/snake", QtCore.QByteArray('你好').toBase64())
#     v = set.value("animal/snake", '1024')
#     print QtCore.QByteArray.fromBase64(v.toByteArray())
    app = QtGui.QApplication(sys.argv)
    gui = SerialUi()
    gui.show()
    sys.exit(app.exec_())            
            
if __name__ == '__main__':
    main()
