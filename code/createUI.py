import sys
import math
import time
import wave
import pyaudio
import matplotlib.pyplot as plt
import numpy as np
import pyqtgraph as pg
from PyQt5.QtCore import Qt,QFile
from PyQt5.QtGui import QPixmap,QPainter
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog,QFileDialog,QGraphicsScene
from UI_MainWindow import *
from UI_modify import *
from UI_single_genarate import *
from UI_sweep_generate import *
from device import *
from test_torch import *


class modify_Window(QDialog, Ui_modify):
    AMorFM = "" 
    #信号参数依次为调制方式、基带信号类型、频率、振幅、相位、载波频率、调制指数
    _signal = QtCore.pyqtSignal(str,str,int,int,int,int,float)
    def __init__(self,modifyType):
        super(modify_Window,self).__init__()
        self.AMorFM = modifyType
        self.setupUi(self)
        self.retranslateUi(self)
        self.buttonBox.accepted.connect(self.slot)
    
    def slot(self):#向父窗口传递数据的槽
        signal_type = self.type.currentText()
        signal_freq = self.freq.value()
        signal_amp = self.amp.value()
        signal_offset = self.offset.value()
        carry_freq = self.carryfreq.value()
        modify_param = self.parameter.value()
        #发送信号
        self._signal.emit(self.AMorFM, signal_type, signal_freq, signal_amp, signal_offset, carry_freq, modify_param)
        #清除数据
        self.AMorFM = ""
        self.type.setCurrentIndex(0)
        self.freq.setValue(0)
        self.amp.setValue(0)
        self.offset.setValue(0)
        self.carryfreq.setValue(0)
        self.parameter.setValue(0.0)

class singlesignal_Window(QDialog, Ui_SingleSignal):
    #信号参数依次为信号类型、频率、振幅、相位
    _signal = QtCore.pyqtSignal(str, int, int, int)
    def __init__(self):
        super(singlesignal_Window,self).__init__()
        self.setupUi(self)
        self.retranslateUi(self)
        self.buttonBox.accepted.connect(self.slot)
        
    def slot(self):
        signal_type = self.type.currentText()
        signal_freq = self.freq.value()
        signal_amp = self.amp.value()
        signal_offset = self.offset.value()
        #发送信号
        self._signal.emit(signal_type, signal_freq, signal_amp, signal_offset)
        #清除数据
        self.type.setCurrentIndex(0)
        self.freq.setValue(0)
        self.amp.setValue(0)
        self.offset.setValue(0)

class sweep_Window(QDialog, Ui_sweep_window):
    _signal = QtCore.pyqtSignal(str, int, int, int, int)
    def __init__(self):
        super(sweep_Window,self).__init__()
        self.setupUi(self)
        self.retranslateUi(self)
        self.buttonBox.accepted.connect(self.slot)

    def slot(self):
        signal_type = self.type.currentText()
        signal_start = self.startfreq.value()
        signal_end = self.endfreq.value()
        signal_step = self.step.value()
        signal_time = self.time.value()
        #发送信号
        self._signal.emit(signal_type, signal_start, signal_end, signal_step, signal_time)
        #清除数据
        self.type.setCurrentIndex(0)
        self.startfreq.setValue(0)
        self.endfreq.setValue(0)
        self.step.setValue(0)
        self.time.setValue(0)

class Main_Window(QMainWindow, Ui_MainWindow):
    #以下保存音频数据
    _nchannels = 1
    _sampwidth = 2
    _framerate = 0
    _CHUNK = 1024
    _FORMAT = pyaudio.paInt16
    _nframes = None
    _data_list = []#wave的列表格式
    _wave = b"" #byte格式
    _current_time = 0
    _time_axis = []
    _amp_axis = []
    #以下为按钮状态
    status_play = False
    status_stop = False
    status_end = False
    status_record = False
    def __init__(self):
        super(Main_Window,self).__init__()
        self.setupUi(self)
        #以下为点击菜单栏弹出子窗口
        self.modify = modify_Window("")
        self.action_AM.triggered.connect(self.drawAM)
        self.action_FM.triggered.connect(self.drawFM)
        self.singleSignal = singlesignal_Window()
        self.action_single.triggered.connect(self.drawSingle)
        self.sweep = sweep_Window()
        self.action_sweep.triggered.connect(self.drawSweep)
        self.action_exit.triggered.connect(self.close)
        #以下为更新输入输出设备列表
        self.update_device_info()
        #以下为文件菜单的处理
        self.action_open.triggered.connect(self.open_file)
        self.action_new.triggered.connect(self.new_file)
        self.action_save.triggered.connect(self.save_file)
        self.action_close.triggered.connect(self.close_file)
        self.action_freq.triggered.connect(self.frequency_analyze)
        self.button_record.clicked.connect(self.record)
        self.button_stop.clicked.connect(self.stop)
        self.button_end.clicked.connect(self.end)
        #以下实现信号可视化
        self.plot_Coordinate_system()
        
    def drawAM(self, modify):#弹出AM调制子窗口
        self.modify.AMorFM = "AM"     
        self.modify.setWindowTitle("AM调制")
        print("type is ",self.modify.AMorFM)
        self.modify.show()
        self.modify._signal.connect(self.get_modify_data)#接受调制信号子窗口回传的数据

    def drawFM(self):#弹出FM调制子窗口
        self.modify.AMorFM = "FM"     
        self.modify.setWindowTitle("FM调制")
        print("type is ",self.modify.AMorFM)
        self.modify.show()
        self.modify._signal.connect(self.get_modify_data)#接受调制信号子窗口回传的数据

    def drawSingle(self):#弹出单频信号生成子窗口
        self.singleSignal.show()
        self.singleSignal._signal.connect(self.get_single_data)#接受调制信号子窗口回传的数据
    
    def drawSweep(self):#弹出扫频信号生成子窗口
        self.sweep.show()
        self.sweep._signal.connect(self.get_sweep_data)

    def update_device_info(self):#更新输入与输出的设备列表
        input_device,output_device = get_device_info()
        for i in range(len(input_device)):
            if input_device[i]["maxInputChannels"]>0:
                self.input_device.insertItem(i,input_device[i]['name'])
        for i in range(len(output_device)):
            if output_device[i]["maxOutputChannels"]>0:
                self.output_device.insertItem(i,output_device[i]['name'])

    def get_modify_data(self, AMorFM, signal_type, signal_freq, signal_amp, signal_offset, carry_freq, modify_param):#接收调制信号子窗口回传的数据
        print("接收到调制信号数据：调制类型{0}，基带信号类型：{1}，频率{2}，振幅{3}，相位{4}，载波频率{5}，调制参数{6}".format(AMorFM, signal_type, signal_freq, signal_amp, signal_offset, carry_freq, modify_param))
        self.modify.disconnect()

    def get_single_data(self, signal_type, signal_freq, signal_amp, signal_offset):#接收调制信号子窗口回传的数据
        print("接收到单频信号数据：信号类型：{0}，频率{1}，振幅{2}，相位{3}".format(signal_type, signal_freq, signal_amp, signal_offset))
        self.singleSignal.disconnect()

    def get_sweep_data(self, signal_type, signal_start, signal_end, signal_step, signal_time):
        print("接收到扫频信号数据：扫频类型{0}，起始频率{1}，终止频率{2}，步长{3}，扫频时间{4}".format(signal_type, signal_start, signal_end, signal_step, signal_time))
        self.sweep.disconnect()

    def open_file(self):
        fname, ftype = QFileDialog.getOpenFileName(self, "打开音频文件", "./", "All Files(*);;Wav(*.wav)")
        if fname:
            self._time_axis,self._amp_axis,self._framerate = calculate_axis(fname)
            self.plot_waveform()
            #以下清除已有的频率图
            self.plot2.setData([],[],pen='b', clear=True)
        else:
            print("open file Error!")

    def new_file(self):
        print("创建新文件")

    def save_file(self):
        print("保存文件")
    
    def close_file(self):
        print("关闭文件")

    def mouse_located1(self, evt):
        #print("鼠标移动")
        if self.p1.vb.mapSceneToView(evt):
            point =self.p1.vb.mapSceneToView(evt)
            xyrange = self.p1.viewRange()
            xmin = xyrange[0][0]
            xmax = xyrange[0][1]
            ymin = xyrange[1][0]
            ymax = xyrange[1][1]
            if xmin<=point.x()<=xmax and ymin<=point.y()<ymax:#只有在坐标系范围内才显示
                self.locate.setText("X=%0.2f Y=%0.2f"%(point.x(),point.y()))

    def mouse_located2(self, evt):
        #print("鼠标移动")
        if self.p2.vb.mapSceneToView(evt):
            point =self.p2.vb.mapSceneToView(evt)
            xyrange = self.p2.viewRange()
            xmin = xyrange[0][0]
            xmax = xyrange[0][1]
            ymin = xyrange[1][0]
            ymax = xyrange[1][1]
            if xmin<=point.x()<=xmax and ymin<=point.y()<ymax:#只有在坐标系范围内才显示
                self.locate.setText("X=%0.2f Y=%0.2f"%(point.x(),point.y()))

    def frequency_analyze(self):
        self.plot_fft()

    def callback_record(self, in_data, frame_count, time_info, status):
        #print("in_data={}\nframe_count={}\ntime_info={}\nstatus={}".format(in_data, frame_count, time_info, status))
        if self.status_record:
            print("standard time: ",time.time()-self.t0)
            print("current time: ",self._current_time)
            print("record samples:",len(self._amp_axis))
            y = decode_wavedata(in_data,self._sampwidth,self._nchannels).tolist()
            #print("amp = ",self._amp_axis,type(self._amp_axis))
            #print("y[0] = ",y[0],type(y[0]))
            self._current_time = time.time()-self.t0
            self._amp_axis = self._amp_axis + y[0]
            #self._time_axis = np.linspace(0, len(self._amp_axis)-1, len(self._amp_axis)) / self._framerate
            self._time_axis = np.linspace(0, self._current_time, len(self._amp_axis))
            self.plot1.setData(self._time_axis, self._amp_axis, pen='b', clear=True)
            self._data_list.append(in_data)
            self.L1.setValue(self._current_time)
            #self._current_time += (len(y[0])-1)/self._framerate
        return b"", pyaudio.paContinue

    def record(self):
        self.status_record = True
        self.audio = pyaudio.PyAudio()
        #以下为获取输入设备的信息
        index = self.input_device.currentIndex()
        print("input device index:",index)
        device_info = self.audio.get_device_info_by_index(index)
        print(device_info)
        self._nchannels = device_info["maxInputChannels"]#声轨数
        self._framerate = int(device_info["defaultSampleRate"])#采样率
        #以下为清空缓存
        self._wave = b''
        self._data_list = []
        self._current_time = 0
        self._time_axis = []
        self._amp_axis = []
        #以下为开始录制
        #print(type(self._nchannels),type(self._framerate))
        self.stream = self.audio.open(format=self._FORMAT,
                    channels=self._nchannels,
                    frames_per_buffer=1024,
                    rate=self._framerate,
                    input_device_index=device_info["index"],
                    input=True,
                    stream_callback=self.callback_record)
        self.t0 = time.time()
        self.stream.start_stream()

    def stop(self):
        if self.status_record:#如果是在录制
            self.stream.stop_stream()
            print("暂停录制")
        else:
            pass

    def end(self):
        self.stream.stop_stream()
        self.stream.close()
        self.audio.terminate()
        print("结束录制")

    def plot_Coordinate_system(self):#只做框架（不画曲线图）
        pg.setConfigOptions(antialias=True, background='#ffffff', foreground="#000000")  # pg全局变量设置函数，antialias=True开启曲线抗锯齿
        win1 = pg.GraphicsLayoutWidget()  # 创建pg layout，可实现数据界面布局自动管理
        win2 = pg.GraphicsLayoutWidget()  # 创建pg layout，可实现数据界面布局自动管理
        self.graph_time.addWidget(win1)
        self.graph_time.addWidget(win2)
        #以下为坐标系的建立
        self.p1 = win1.addPlot(title="Time domain")  # 添加绘图窗口,PlotItem类
        self.p2 = win2.addPlot(title="Freq domain")  # 添加绘图窗口,PlotItem类
        self.p1.setMenuEnabled(enableViewBoxMenu=False)
        self.p2.setMenuEnabled(enableViewBoxMenu=False)
        self.p1.setLabel('left', text='Amp', color='#000000')  # y轴设置函数
        self.p2.setLabel('left', text='db', color='#000000')  # y轴设置函数
        self.p1.showGrid(x=True, y=True)  # 栅格设置函数
        self.p2.showGrid(x=True, y=True)  # 栅格设置函数
        self.p1.setLogMode(x=False, y=False)  # False代表线性坐标轴，True代表对数坐标轴
        self.p2.setLogMode(x=False, y=False)  # False代表线性坐标轴，True代表对数坐标轴
        self.p1.setLabel('bottom', text='time', units='s')  # x轴设置函数
        self.p2.setLabel('bottom', text='freq', units='hz')  # x轴设置函数
        self.p1.setLimits(xMin=0,yMin=-1.1,yMax=1.1)
        self.p2.setLimits(xMin=0)
        self.p1.setYRange(-1.1,1.1)
        #以下为显示光标位置
        self.setMouseTracking(True)
        #pg.SignalProxy(self.p1.scene().sigMouseMoved,rateLimit=60,slot=self.mouse_located1)
        self.p1.scene().sigMouseMoved.connect(self.mouse_located1)
        self.p2.scene().sigMouseMoved.connect(self.mouse_located2)
        #以下为创建plot
        self.plot1 = self.p1.plot()
        self.plot2 = self.p2.plot()
        #以下为创建定位线
        self.L1 = self.p1.addLine(movable=True, pen='g', angle=90, pos=0)
        self.L1.addMarker(marker='v', position=1)
    
    def plot_waveform(self):#画时域图
        self.plot1.setData(self._time_axis, self._amp_axis, pen='b', clear=True)
        self.p1.setLimits(xMax=self._time_axis[-1])
        self.L1.setValue(0)
        self.L1.setBounds([0,self._time_axis[-1]])
        #print(self.L1.bounds())
        

    def plot_fft(self):
        n=len(self._time_axis)# 信号长度
        #方法一
        freq = np.fft.fftfreq(n, d=1/self._framerate) #x轴
        fft_y = np.fft.fft(self._amp_axis) #y轴
        abs_y = np.abs(fft_y)
        amplitude_y = np.abs(abs_y[1:int(n/2)])/n
        self.plot2.setData(freq[1:int(n/2)],  amplitude_y, pen='b', clear=True)
        self.p2.setLimits(yMin=0,yMax=1.1,xMin=0,xMax=np.max(freq))
        #方法二
        # x = np.arange(n)             # 频率个数
        # half_x = x[range(int(n/2))]  #取一半区间
        # fft_y = np.fft.fft(self._amp_axis)
        # abs_y=np.abs(fft_y)                # 取复数的绝对值，即复数的模(双边频谱)
        # angle_y=np.angle(fft_y)            #取复数的角度
        # normalization_y=abs_y/n           #归一化处理（双边频谱）                              
        # normalization_half_y = normalization_y[range(int(n/2))]      #由于对称性，只取一半区间（单边频谱）
        # self.p2.setLimits(yMin=0,yMax=1.1,xMin=0,xMax=np.max(half_x))
        # self.plot2.setData(half_x,  normalization_half_y, pen='b', clear=True)
        
        


if __name__== '__main__':
    app = QApplication(sys.argv)
    main = Main_Window() 
    main.show()
    sys.exit(app.exec_())