import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap,QPainter
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog

from UI_MainWindow import *
from UI_modify import *
from UI_single_genarate import *
from UI_sweep_generate import *
from device import *

class modify_Window(QDialog, Ui_modify):
    AMorFM = "" 
    def __init__(self,modifyType):
        super(modify_Window,self).__init__()
        self.AMorFM = modifyType
        self.setupUi(self)

class singlesignal_Window(QDialog, Ui_SingleSignal):
    def __init__(self):
        super(singlesignal_Window,self).__init__()
        self.setupUi(self)

class sweep_Window(QDialog, Ui_sweep_window):
    def __init__(self):
        super(sweep_Window,self).__init__()
        self.setupUi(self)

class Main_Window(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super(Main_Window,self).__init__()
        self.setupUi(self)
        #以下为点击菜单栏弹出子窗口
        self.action_AM.triggered.connect(self.drawAM)
        self.action_FM.triggered.connect(self.drawFM)
        self.action_single.triggered.connect(self.drawSingle)
        self.action_sweep.triggered.connect(self.drawSweep)
        #以下为更新输入输出设备列表
        self.update_device_info()
        #以下为
    def drawAM(self):#弹出AM调制子窗口
        modify = modify_Window("AM")
        modify.setWindowTitle("AM调制")
        print("type is ",modify.AMorFM)
        modify.exec()

    def drawFM(self):#弹出FM调制子窗口
        modify = modify_Window("FM")
        modify.setWindowTitle("FM调制")
        print("type is ",modify.AMorFM)
        modify.exec()

    def drawSingle(self):#弹出单频信号生成子窗口
        singleSignal = singlesignal_Window()
        singleSignal.exec()
    
    def drawSweep(self):#弹出扫频信号生成子窗口
        sweep = sweep_Window()
        sweep.exec()

    def update_device_info(self):#更新输入与输出的设备列表
        input_device,output_device = get_device_info()
        for i in range(len(input_device)):
            self.input_device.insertItem(i,input_device[i]['name'])
        for i in range(len(output_device)):
            self.output_device.insertItem(i,output_device[i]['name'])


if __name__== '__main__':
    app = QApplication(sys.argv)
    main = Main_Window()
    main.show()
    #modify = modify_Window()
    #modify.show()
    sys.exit(app.exec_())