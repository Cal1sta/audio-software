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
from PyQt5.QtWidgets import QApplication,QMainWindow,QDialog,QFileDialog,QGraphicsScene,QMessageBox
from scipy.fft import fft, fftfreq
from UI_MainWindow import *
from UI_modify import *
from UI_sin_generate import *
from UI_square_generate import *
from UI_sweep_generate import *
from UI_pulse_generate import *
from device import *
from test_torch import *
from signal_create import *
import threading


class modify_Window(QDialog, Ui_modify):
    AMorFM = "" 
    #信号参数依次为:调制方式、基带信号类型、频率、振幅、相位或占空比、载波频率、调制指数、持续时间
    _signal = QtCore.pyqtSignal(str,str,int,int,int,int,float,float)
    def __init__(self,modifyType):
        super(modify_Window,self).__init__()
        self.AMorFM = modifyType
        self.setupUi(self)
        self.retranslateUi(self)
        self.buttonBox.accepted.connect(self.slot)
        self.type.currentIndexChanged.connect(self.update)
    
    def slot(self):#向父窗口传递数据的槽
        signal_type = self.type.currentText()
        signal_freq = self.freq.value()
        signal_samplerate = self.samplerate.value()
        signal_offset_or_ratio = self.offset_or_ratio.value()
        carry_freq = self.carryfreq.value()
        modify_param = self.parameter.value()
        duration = self.duration.value()
        #发送信号
        self._signal.emit(self.AMorFM, signal_type, signal_freq, signal_samplerate, signal_offset_or_ratio, carry_freq, modify_param, duration)
        #清除数据
        self.AMorFM = ""
        self.type.setCurrentIndex(0)
        self.freq.setValue(0)
        self.samplerate.setValue(0)
        self.offset_or_ratio.setValue(0)
        self.carryfreq.setValue(0)
        self.parameter.setValue(0.0)
        self.duration.setValue(0.0)

    def update(self):
        print("update")
        if self.type.currentText() == "正弦波":
            self.label_offset_or_ratio.setText("相位(°)：")
            self.offset_or_ratio.setMaximum(360)
            print("正弦")
        elif self.type.currentText() == "矩形波":
            self.label_offset_or_ratio.setText("占空比(%)：")
            self.offset_or_ratio.setMaximum(100)
            print("矩形")

class sinsignal_Window(QDialog, Ui_SinSignal):
    #信号参数依次为频率、相位、持续时间、采样率
    _signal = QtCore.pyqtSignal(int, int, float, int)
    def __init__(self):
        super(sinsignal_Window,self).__init__()
        self.setupUi(self)
        self.retranslateUi(self)
        self.buttonBox.accepted.connect(self.slot)
        
    def slot(self):
        signal_freq = self.freq.value()
        signal_offset = self.offset.value()
        signal_duration = self.duration.value()
        signal_samplerate = self.samplerate.value()
        #发送信号
        self._signal.emit(signal_freq, signal_offset, signal_duration, signal_samplerate)
        #清除数据
        self.freq.setValue(0)
        self.offset.setValue(0)
        self.duration.setValue(0.0)
        self.samplerate.setValue(1)

class squaresignal_Window(QDialog, Ui_SquareSignal):
    #信号参数依次为频率、占空比、持续时间、采样率
    _signal = QtCore.pyqtSignal(int, int, float, int)
    def __init__(self):
        super(squaresignal_Window,self).__init__()
        self.setupUi(self)
        self.retranslateUi(self)
        self.buttonBox.accepted.connect(self.slot)
        
    def slot(self):
        signal_freq = self.freq.value()
        signal_ratio = self.ratio.value()
        signal_duration = self.duration.value()
        signal_samplerate = self.samplerate.value()
        #发送信号
        self._signal.emit(signal_freq, signal_ratio, signal_duration, signal_samplerate)
        #清除数据
        self.freq.setValue(0)
        self.ratio.setValue(0)
        self.duration.setValue(0.0)
        self.samplerate.setValue(1)

class pulsesignal_Window(QDialog, Ui_PulseSignal):
    #信号参数依次为频率、占空比、持续时间、采样率
    _signal = QtCore.pyqtSignal(int, float, int)
    def __init__(self):
        super(pulsesignal_Window,self).__init__()
        self.setupUi(self)
        self.retranslateUi(self)
        self.buttonBox.accepted.connect(self.slot)
        
    def slot(self):
        signal_freq = self.freq.value()
        signal_duration = self.duration.value()
        signal_samplerate = self.samplerate.value()
        #发送信号
        self._signal.emit(signal_freq, signal_duration, signal_samplerate)
        #清除数据
        self.freq.setValue(0)
        self.duration.setValue(0.0)
        self.samplerate.setValue(1)

class sweep_Window(QDialog, Ui_sweep_window):
    _signal = QtCore.pyqtSignal(str, int, int, float, int)
    def __init__(self):
        super(sweep_Window,self).__init__()
        self.setupUi(self)
        self.retranslateUi(self)
        self.buttonBox.accepted.connect(self.slot)

    def slot(self):
        signal_type = self.type.currentText()
        signal_start = self.startfreq.value()
        signal_end = self.endfreq.value()
        signal_duration = self.duration.value()
        signal_samplerate = self.samplerate.value()
        #发送信号
        self._signal.emit(signal_type, signal_start, signal_end, signal_duration, signal_samplerate)
        #清除数据
        self.type.setCurrentIndex(0)
        self.startfreq.setValue(0)
        self.endfreq.setValue(0)
        self.duration.setValue(0.0)
        self.samplerate.setValue(0)

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
    _time_axis = []#时域图x轴 list
    _amp_axis = []#时域图y轴 list
    _freq_axis = np.array([0])
    _amp_freq_axis = np.array([0])
    _filename = ''
    _drawsample = 10000#绘制图像时的坐标数量
    showmaxx = 1
    showminx = 0
    #以下运行状态
    status_play = False
    status_stop = False
    status_end = False
    status_record = False
    status_saved = False
    status_generated = False
    status_open = False
    def __init__(self):
        super(Main_Window,self).__init__()
        self.setupUi(self)
        #以下为点击菜单栏弹出子窗口
        self.modify = modify_Window("")
        self.action_AM.triggered.connect(self.drawAM)
        self.action_FM.triggered.connect(self.drawFM)
        self.sinSignal = sinsignal_Window()
        self.action_sinwave.triggered.connect(self.drawSin)
        self.squareSignal = squaresignal_Window()
        self.action_squarewave.triggered.connect(self.drawSquare)
        self.pulseSignal = pulsesignal_Window()
        self.action_pulsewave.triggered.connect(self.drawPulse)
        self.sweep = sweep_Window()
        self.action_sweep.triggered.connect(self.drawSweep)
        self.action_exit.triggered.connect(self.close)
        #以下为更新输入输出设备列表
        self.update_device_info()
        #以下为信号的处理
        self.action_open.triggered.connect(self.open_file)
        self.action_new.triggered.connect(self.new_file)
        self.action_save.triggered.connect(self.save_file)
        self.action_close.triggered.connect(self.close_file)
        self.action_freq.triggered.connect(self.frequency_analyze)
        self.button_play.clicked.connect(self.play)
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

    def drawSin(self):#弹出单频信号生成子窗口
        self.sinSignal.show()
        self.sinSignal._signal.connect(self.get_sin_data)#接受调制信号子窗口回传的数据

    def drawSquare(self):#弹出单频信号生成子窗口
        self.squareSignal.show()
        self.squareSignal._signal.connect(self.get_square_data)#接受调制信号子窗口回传的数据

    def drawPulse(self):#弹出单频信号生成子窗口
        self.pulseSignal.show()
        self.pulseSignal._signal.connect(self.get_pulse_data)#接受调制信号子窗口回传的数据
    
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

    def get_modify_data(self, AMorFM, signal_type, signal_freq, signal_samplerate, signal_offset_or_ratio, carry_freq, modify_param, duration):#接收调制信号子窗口回传的数据
        print("接收到调制信号数据：调制类型{0}，基带信号类型：{1}，频率{2}，采样率{3}，相位或占空比{4}，载波频率{5}，调制参数{6}，持续时间{7}".format(AMorFM, signal_type, signal_freq, signal_samplerate, signal_offset_or_ratio, carry_freq, modify_param, duration))
        self.ret2origin()
        #从左至右依次为：采样率、声道数（默认为2）、位深(2)、分贝数、消息信号类型、消息信号频率、载波频率、持续时间、相位偏移（度数单位）或占空比（百分制）、调制参数
        if AMorFM == "AM":
            waveinfo = [signal_samplerate, 2, 2, -3, signal_type, signal_freq, carry_freq, duration, signal_offset_or_ratio, modify_param]
            self._wave,self._amp_axis,self._time_axis = generate_AM_modify(waveinfo)
        elif AMorFM == "FM":
            waveinfo = [signal_samplerate, 2, 2, -3, signal_type, signal_freq, carry_freq, duration, signal_offset_or_ratio, modify_param]
            self._wave,self._amp_axis,self._time_axis = generate_FM_modify(waveinfo)
        self._nchannels = 2
        self._framerate = signal_samplerate
        self.plot_waveform()
        self.modify.disconnect()

    def get_sin_data(self, signal_freq, signal_offset, signal_duration, signal_samplerate):#接收调制信号子窗口回传的数据
        print("接收到单频信号数据：频率{0}，相位{1}，持续时间{2}，采样率{3}".format(signal_freq, signal_offset, signal_duration, signal_samplerate))
        self.ret2origin()
        #从左至右参数依次为：采样率、声道数（默认为2）、位深(2)、分贝（-3）、左声道频率、右声道频率、持续时间、相位偏移（度数单位）
        waveinfo = [signal_samplerate, 2, 2, -3, signal_freq, signal_freq, signal_duration, signal_offset]
        self._wave,self._amp_axis,self._time_axis = generate_sinewave(waveinfo)
        self._nchannels = 2
        self._framerate = signal_samplerate
        self.plot_waveform()
        self.sinSignal.disconnect()

    def get_square_data(self, signal_freq, signal_ratio, signal_duration, signal_samplerate):#signal_freq, signal_ratio, signal_duration, signal_samplerate
        print("生成矩形波信号：频率{0}，占空比{1}，持续时间{2}，采样率{3}".format(signal_freq, signal_ratio, signal_duration, signal_samplerate))
        self.ret2origin()
        #从左至右参数依次为：采样率、声道数（默认为2）、位深(2)、分贝（-3）、左声道频率、右声道频率、持续时间、相位偏移（度数单位）
        waveinfo = [signal_samplerate, 2, 2, -3, signal_freq, signal_freq, signal_duration, signal_ratio]
        self._wave,self._amp_axis,self._time_axis = generate_squarewave(waveinfo)
        self._nchannels = 2
        self._framerate = signal_samplerate
        self.plot_waveform()
        self.squareSignal.disconnect()
    
    def get_pulse_data(self, signal_freq, signal_duration, signal_samplerate):
        print("生成矩形波信号：频率{0}，持续时间{1}，采样率{2}".format(signal_freq, signal_duration, signal_samplerate))
        self.ret2origin()
        #从左至右参数依次为：采样率、声道数（默认为2）、位深(2)、分贝（-3）、左声道频率、右声道频率、持续时间、相位偏移（度数单位）
        signal_ratio = 10
        waveinfo = [signal_samplerate, 2, 2, -3, signal_freq, signal_freq, signal_duration, signal_ratio]
        self._wave,self._amp_axis,self._time_axis = generate_pulsewave(waveinfo)
        #print(self._amp_axis)
        self._nchannels = 2
        self._framerate = signal_samplerate
        self.plot_waveform()
        self.pulseSignal.disconnect()

    def get_sweep_data(self, signal_type, signal_start, signal_end, signal_duration, signal_samplerate):
        print("接收到扫频信号数据：扫频类型{0}，起始频率{1}，终止频率{2}，扫频时间{3}, 采样率{4}".format(signal_type, signal_start, signal_end, signal_duration, signal_samplerate))
        self.ret2origin()
        #从左至右参数依次为：采样率、声道数（默认为2）、位深(2)、分贝（-3）、起始频率、终止频率、持续时间、扫频类型
        waveinfo = [signal_samplerate, 2, 2, -3, signal_start, signal_end, signal_duration, signal_type]
        self._wave,self._amp_axis,self._time_axis = generate_sweepwave(waveinfo)
        self._nchannels = 2
        self._framerate = signal_samplerate
        self.plot_waveform()
        self.sweep.disconnect()

    def open_file(self):
        self.ret2origin()
        if not self._filename:#如果为空
            fname, ftype = QFileDialog.getOpenFileName(self, "打开音频文件", "./", "All Files(*);;Wav(*.wav)")
        else:
            fname = self._filename
        if fname:
            title = "声音信号处理软件  " + fname 
            self.setWindowTitle(title)
            self.status_open = True
            self._filename = fname
            self._time_axis,self._amp_axis,self._framerate = calculate_axis(fname)
            self.showminx = self._time_axis[0]
            self.showmaxx = self._time_axis[-1]
            self.p1.setLimits(xMax=self._time_axis[-1])
            self.p1.setXRange(0,self._time_axis[-1])
            self.p1.setYRange(-1.1,1.1)
            self.L1.setValue(0)
            self.L1.setBounds([0,self._time_axis[-1]])
            #以下清除已有的频率图
            self.plot2.setData([],[],pen='b', clear=True)
            #以下更新wave的音频参数
            p = pyaudio.PyAudio()
            self.wf = wave.open(fname, 'rb')
            self._nchannels = self.wf.getnchannels()
            self._sampwidth = self.wf.getsampwidth()
            self._framerate = self.wf.getframerate()
            self._FORMAT = p.get_format_from_width(self.wf.getsampwidth())
            p.terminate()
            print("打开文件{}——声道数：{}，采样率：{}hz，位深：{}".format(self._filename,self._nchannels,self._framerate,self._sampwidth))
            #以下调用绘图方法
            self.plot_waveform()
        else:
            print("open file Error!")

    def new_file(self):
        print("创建新文件")
        if not self.status_saved and self._wave:#如果还没有保存文件并且wave非空，即生成或录制音频且尚未保存
            yesorno = QMessageBox.question(self,"Unsaved file...","是否保存当前音频？",QMessageBox.Yes | QMessageBox.No)
            if yesorno == QMessageBox.Yes:
                self.save_file()
            else:
                pass
        self.ret2origin()

    def save_file(self):
        fname, ftype = QFileDialog.getSaveFileName(self, "保存音频文件", "./", "Wav(*.wav)")
        print(fname,ftype)
        self._filename = fname
        print("准备保存文件")
        if fname and self._wave:
            wf = wave.open(fname, 'wb')
            wf.setnchannels(self._nchannels)
            wf.setsampwidth(self._sampwidth)
            wf.setframerate(self._framerate)
            wf.writeframes(self._wave)
            wf.close()
            self.status_saved = True
            return fname, ftype
        elif not self._wave:
            print("内容不能为空")
        elif not fname:
            print("文件路径不能为空")
        return None
    
    def close_file(self):
        try:
            self.wf.close()
        except:
            print("close file error")
        self.status_open = False
        self.setWindowTitle("声音信号处理软件")
        self.ret2origin()
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
                self.locate.setText("光标位置：X=%0.2f Y=%0.2f"%(point.x(),point.y()))

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
                self.locate.setText("光标位置：X=%0.2f Y=%0.2f\t"%(point.x(),point.y()))

    def frequency_analyze(self):
        self.plot_fft()

    def ret2origin(self):
        #将图像清空
        self.plot1.setData([],[],pen='b', clear=True)
        self.plot2.setData([],[],pen='b', clear=True)
        #所有参数还原
        self.status_play = False
        self.status_stop = False
        self.status_end = False
        self.status_record = False
        self._nchannels = 1
        self._sampwidth = 2
        self._framerate = 0
        self._CHUNK = 1024
        self._FORMAT = pyaudio.paInt16
        self._nframes = None
        self._data_list = []#wave的列表格式
        self._wave = b"" #byte格式
        self._current_time = 0
        self._time_axis = []
        self._amp_axis = []
        self._filename = ''
        self._drawsample = 10000#绘制图像时的坐标数量

    def record_music(self):
        #以下为设置参数
        audio = pyaudio.PyAudio()
        device_name = self.input_device.currentText()
        print("input device name:",device_name)
        index = get_device_index_by_name(device_name)
        device_info = audio.get_device_info_by_index(index)
        print(device_info)
        self._nchannels = device_info["maxInputChannels"]#声轨数
        self._framerate = int(device_info["defaultSampleRate"])#采样率
        t0 = time.time()
        #以下为开始录制     
        stream = audio.open(format=self._FORMAT,
                    channels=self._nchannels,
                    frames_per_buffer=self._CHUNK,
                    rate=self._framerate,
                    input_device_index=device_info["index"],
                    input=True)
        while(not self.status_end):#不按终止按钮，就一直录制
            if not self.status_stop:#只要不暂停
                data = stream.read(self._CHUNK)
                self._wave = self._wave + data
                y = decode_wavedata(data,self._sampwidth,self._nchannels).tolist()
                self._amp_axis = self._amp_axis + y[0]
                self._time_axis = np.linspace(0,(len(self._amp_axis)-1)/self._framerate, len(self._amp_axis), endpoint=False)
                self._current_time = (len(self._amp_axis)-1)/self._framerate
                print(self._current_time)
                print("len(y):",len(self._time_axis))
                print("len(amp)",len(self._amp_axis))
                print("standard time:",time.time()-t0)
                print("sample time:",self._current_time)
                self.showminx = 0
                self.showmaxx = self._current_time
                self.plot_waveform()
                self.L1.setValue(self._current_time)
        self.status_record = False
        stream.stop_stream()
        stream.close()
        audio.terminate()
        print("结束录制")

    def record(self):
        if not self.status_record:#如果当前还没有开始录制
            self.ret2origin()
            self.status_record = True
            self._CHUNK = 2048
            t=threading.Thread(target=self.record_music,daemon=True)
            t.start()
        else:
            self.status_stop = False

    def play_music(self):
        audio = pyaudio.PyAudio()
        #以下为获取输出设备的信息
        device_name = self.output_device.currentText()
        print("output device name:",device_name)
        index = get_device_index_by_name(device_name)
        device_info = audio.get_device_info_by_index(index)
        print(device_info)
        #self._nchannels = device_info["maxOutputChannels"]#声轨数
        #self._framerate = int(device_info["defaultSampleRate"])#采样率
        #以下为播放音频
        stream = audio.open(format=self._FORMAT,
                    channels=self._nchannels,
                    rate=self._framerate,
                    output_device_index=index,
                    output=True)
        data = self.wf.readframes(self._CHUNK)
        #chunk_total = 0
        while data!=b'' and self.status_play:
            if not self.status_stop:#只要不暂停，就播放
                stream.write(data)#播放
                #print(data)
                data = self.wf.readframes(self._CHUNK)
                print(self.wf.tell())
                self._current_time += self._CHUNK/self._framerate
                self.L1.setPos(self._current_time)
            if self.status_end:#如果按了结束键，则直接结束
                self.wf.rewind()
                self._current_time = 0
                self.L1.setPos(self._current_time)
                break
            time.sleep(0.01)
        self.status_play = False
        stream.close()
        audio.terminate()
        print("结束播放")

    def play(self):
        if not self.status_play:#如果还没有处于播放状态
            if self.status_open:#如果有打开文件,就播放
                print("准备播放")
                self.status_play = True
                self.wf.rewind()
                self._current_time = 0
                t=threading.Thread(target=self.play_music,daemon=True)
                t.start()
            else:#如果没有打开文件
                if self._wave:#若wave非空（即生成或录制结束），就先保存然后打开文件
                    print("请先保存文件")
                    yesorno = QMessageBox.information(self,"Unsaved file...","播放音频前请先保存",QMessageBox.Yes | QMessageBox.No)
                    if yesorno == QMessageBox.Yes:
                        self.save_file()
                        self.open_file()
                else:#若wave为空，说明处于初始阶段，不处理
                    print("请先打开文件")
        self.status_stop=False

    def stop(self):
        if self.status_record:#如果是在录制
            self.status_stop = True
            print("暂停录制")
        elif self.status_play:#如果是在播放
            self.status_stop = True
            print("暂停播放")

    def end(self):
        self.status_end = True

    def plot_Coordinate_system(self):#只做框架（不画曲线图）
        pg.setConfigOptions(antialias=True, background='#ffffff', foreground="#000000")  # pg全局变量设置函数，antialias=True开启曲线抗锯齿
        win1 = pg.GraphicsLayoutWidget()  # 创建pg layout，可实现数据界面布局自动管理
        win2 = pg.GraphicsLayoutWidget()  
        self.graph_time.addWidget(win1)
        self.graph_time.addWidget(win2)
        #以下为坐标系的建立
        self.p1 = win1.addPlot(title="Time domain")  # 添加绘图窗口,PlotItem类
        self.p2 = win2.addPlot(title="Freq domain")  
        self.p1.setMenuEnabled(enableViewBoxMenu=False)
        self.p2.setMenuEnabled(enableViewBoxMenu=False)
        self.p1.setLabel('left', text='Amp', color='#000000')  # y轴设置函数
        self.p2.setLabel('left', text='db', color='#000000')  
        self.p1.showGrid(x=True, y=True)  # 栅格设置函数
        self.p2.showGrid(x=True, y=True)  
        self.p1.setLogMode(x=False, y=False)  # False代表线性坐标轴，True代表对数坐标轴
        self.p2.setLogMode(x=False, y=False)  
        self.p1.setLabel('bottom', text='time', units='s')  # x轴设置函数
        self.p2.setLabel('bottom', text='freq', units='hz')  
        self.p1.setLimits(xMin=0,yMin=-1.1,yMax=1.1)
        self.p2.setLimits(xMin=0)
        self.p1.setYRange(-1.1,1.1)
        #以下为显示光标位置
        self.setMouseTracking(True)
        #pg.SignalProxy(self.p1.scene().sigMouseMoved,rateLimit=60,slot=self.mouse_located1)
        self.p1.scene().sigMouseMoved.connect(self.mouse_located1)
        self.p2.scene().sigMouseMoved.connect(self.mouse_located2)
        self.p1.sigRangeChanged.connect(self.update_region)
        #以下为创建plot
        self.plot1 = self.p1.plot()
        self.plot2 = self.p2.plot()
        #以下为创建定位线
        self.L1 = self.p1.addLine(movable=True, pen='g', angle=90, pos=0)
        self.L1.addMarker(marker='v', position=1)
        self.L1.sigPositionChangeFinished.connect(self.update_progress)

    def update_progress(self):
        if self.status_play:
            #if self.status_stop or self.status_end:#如果处于暂停或结束播放的状态
            self._current_time = self.L1.value()#改时间
            self.wf.setpos(int(self._current_time*self._framerate))#改文件指针

    def plot_waveform(self):#画时域图,需备好self.showmaxx,self.showminx,self._framerate,self._drawsample
        interval = (self.showmaxx-self.showminx)* self._framerate//self._drawsample  #画图间隔
        interval = int(interval + 1)
        minx = int(self.showminx * self._framerate)
        maxx = int(self.showmaxx * self._framerate)
        #print("X:",len(self._time_axis[minx:maxx:interval]))
        #print("Y:",len(self._amp_axis[minx:maxx:interval]))
        self.plot1.setData(self._time_axis[minx:maxx:interval], self._amp_axis[minx:maxx:interval], pen='b', clear=True)
        #print(minx,maxx,interval)
        
        #print(self.L1.bounds())

    def update_region(self,a,lineshow):#坐标轴缩放后重新绘制图像
        self.showminx = lineshow[0][0]
        self.showmaxx = lineshow[0][1]
        #print(self.showminx,"----",self.showmaxx)
        #如果开始
        self.plot_waveform()

    def plot_fft(self):
        n=len(self._time_axis)# 信号长度
        #方法一
        """ freq = np.fft.fftfreq(n, d=1/self._framerate) #x轴
        # amp_y = []
        # for x in self._amp_axis:
        #     amp_y.append(x*math.pow(2,self._sampwidth * 8))
        fft_y = np.fft.fft(self._amp_axis) #y轴
        abs_y = np.abs(fft_y)
        amplitude_y = np.abs(abs_y[1:int(n/2)])/n
        #amplitude_y = amplitude_y/math.pow(2,self._sampwidth * 8 - 1)
        print(amplitude_y)
        print(max(amplitude_y))
        self.plot2.setData(freq[1:int(n/2)],  amplitude_y, pen='b', clear=True)
        self.p2.setLimits(yMin=0,yMax=1.1,xMin=0,xMax=np.max(freq)) """
        #方法二
        x = fftfreq(n, 1/self._framerate)[:n//2]
        y = fft(self._amp_axis)
        y = 2.0/n * np.abs(y[0:n//2])#初始格式
        y = 20 * np.log10(y)#db格式
        x_new = x[np.where(y>-90)]
        y_new = y[np.where(y>-90)]#只显示db>-90的频率
        
        self.plot2.setData(x_new, y_new, pen='b', clear=True)
        self.p2.setLimits(yMin=-90,xMin=0,xMax=np.max(x))

if __name__== '__main__':
    app = QApplication(sys.argv)
    main = Main_Window() 
    main.show()
    sys.exit(app.exec_())