import wave
import numpy as np
import struct
import matplotlib.pyplot as plt
from scipy import signal
import math
import ctypes

def generate_sinewave(waveinfo):#从左至右依次为：采样率、声道数（默认为2）、位深(2)、分贝数、左声道频率、右声道频率、持续时间、相位偏移（度数单位）
    samplerate = waveinfo[0]
    ch_num = waveinfo[1]
    bytes_width = waveinfo[2]
    xdb = waveinfo[3]
    sinewave_freq_l = waveinfo[4]
    sinewave_freq_r = waveinfo[5]
    duration = waveinfo[6]
    offset = waveinfo[7]
    
    # volume xdb
    db = math.pow(10,xdb/20)
    # sample/every second
    framerate = samplerate
    # channel_num
    channel_num = ch_num
    # bytes needed every sample
    sample_width = bytes_width
    bits_width = sample_width*8
    # seconds, long of data
    duration = duration
    # frequeny of sinewave
    sinewave_frequency_l = sinewave_freq_l
    sinewave_frequency_r = sinewave_freq_r
    # max value of samples, depends on bits_width
    max_val = 2**(bits_width-1) - 1
    #print ('max_val : ', max_val)
    #volume = 32767*db #0x7FFF=32767
    volume = max_val*db #2**(bits_width-1) - 1
    #offset
    offset = offset / 180 * np.pi
    #多个声道生成波形数据
    x = np.linspace(0, duration, num=int(duration*framerate), endpoint=False)
    y_l = np.sin(2 * np.pi * sinewave_frequency_l * x + offset) * volume #db*sin(2*pi*f*x)
    y_r = np.sin(2 * np.pi * sinewave_frequency_r * x) * volume #类型为ndarray，可用tolist()转成list类型
    #print("type(y_l)",type(y_l))
    # 将多个声道的波形数据转换成数组
    y = zip(y_l,y_r)
    #print("zip y", y)
    y = list(y)
    #print("list y",y)
    y = np.array(y,dtype=int)
    #print("array y",y)
    y = y.reshape(-1)
    #print("reshap array y",y)
    # 最终生成的一维数组(ndarray类型)
    sine_wave = y
    list_y = y.tolist()#list类型
    byte_data = b''
    for v in list_y:
        data = struct.pack('<h',int(v))
        byte_data += data
    #print(byte_data)
    #以下对单声轨做归一化
    Timedata=[]
    for v in y_l:
        Timedata.append(v/math.pow(2, 8 * sample_width - 1))
    # plt.subplot(211)
    # plt.plot(x, Timedata, color='r')
    # plt.subplot(212)
    # plt.plot(x, y_r, color='r')
    # plt.show()
    return byte_data,Timedata,x#返回的是信号的byte格式、归一化处理过的单声轨list以及对应的时间尺度

def generate_squarewave(waveinfo):#从左至右依次为：采样率、声道数（默认为2）、位深(2)、分贝数、左声道频率、右声道频率、持续时间、占空比（百分制）
    samplerate = waveinfo[0]
    ch_num = waveinfo[1]
    bytes_width = waveinfo[2]
    xdb = waveinfo[3]
    squarewave_freq_l = waveinfo[4]
    squarewave_freq_r = waveinfo[5]
    duration = waveinfo[6]
    ratio = waveinfo[7]/100
    # volume xdb
    db = math.pow(10,xdb/20)
    # bytes needed every sample
    bits_width = bytes_width*8
    max_val = 2**(bits_width-1) - 1 #量化后的最大值
    #print ('max_val : ', max_val)
    volume = max_val*db #2**(bits_width-1) - 1
    #周期
    squarewave_T_l = 1/squarewave_freq_l
    squarewave_T_r = 1/squarewave_freq_r

    #多个声道生成波形数据
    x = np.linspace(0, duration, num=int(duration*samplerate), endpoint=False)
    list_left = []
    list_right = []
    square_wave = volume * signal.square(2 * np.pi * squarewave_freq_l * x, duty=ratio)#生成ndarray格式
    #print(type(square_wave))
    list_left = square_wave.tolist()
    list_right = square_wave.tolist()

    list_total = []#2个声轨合并为一维列表
    for i in range(len(list_left)):
        list_total.append(list_left[i])
        list_total.append(list_right[i])

    byte_data = b''#byte格式的双声道数据
    for v in list_total:
        data = struct.pack('<h',int(v))
        byte_data += data
    #print(byte_data)
    list_left_normalized = []
    for i in list_left:#左声道归一化
        list_left_normalized.append(i / math.pow(2, 8 * bytes_width - 1))
    # plt.subplot(211)
    # plt.plot(x, list_left_normalized, color='r')
    # plt.subplot(212)
    # plt.plot(x, square_wave, color='r')
    # plt.show()
    #print("list_left:\n",list_left)
    #print("list_left_normalized:\n",list_left_normalized)
    return byte_data,list_left_normalized,x

def generate_pulsewave(waveinfo):#从左至右依次为：采样率、声道数（默认为2）、位深(2)、分贝数、左声道频率、右声道频率、持续时间、占空比（10）
    samplerate = waveinfo[0]
    ch_num = waveinfo[1]
    bytes_width = waveinfo[2]
    xdb = waveinfo[3]
    pulsewave_freq_l = waveinfo[4]
    pulsewave_freq_r = waveinfo[5]
    duration = waveinfo[6]
    ratio = waveinfo[7]/100
    # volume xdb
    db = math.pow(10,xdb/20)
    # bytes needed every sample
    bits_width = bytes_width*8
    max_val = 2**(bits_width-1) - 1 #量化后的最大值
    #print ('max_val : ', max_val)
    volume = max_val*db #2**(bits_width-1) - 1
    #周期
    pulsewave_T_l = 1/pulsewave_freq_l
    pulsewave_T_r = 1/pulsewave_freq_r

    #多个声道生成波形数据
    x = np.linspace(0, duration, num=int(duration*samplerate), endpoint=False)
    list_left = []
    list_right = []
    pulse_wave = volume * signal.square(2 * np.pi * pulsewave_freq_l * x, duty=ratio)#生成ndarray格式
    pulse_wave = np.clip(pulse_wave, 0, None)
    #print(type(square_wave))
    list_left = pulse_wave.tolist()
    list_right = pulse_wave.tolist()

    list_total = []#2个声轨合并为一维列表
    for i in range(len(list_left)):
        list_total.append(list_left[i])
        list_total.append(list_right[i])

    byte_data = b''#byte格式的双声道数据
    for v in list_total:
        data = struct.pack('<h',int(v))
        byte_data += data
    #print(byte_data)
    list_left_normalized = []
    for i in list_left:#左声道归一化
        list_left_normalized.append(i / math.pow(2, 8 * bytes_width - 1))
    # plt.subplot(211)
    # plt.plot(x, list_left_normalized, color='r')
    # plt.subplot(212)
    # plt.plot(x, square_wave, color='r')
    # plt.show()
    #print("list_left:\n",list_left)
    #print("list_left_normalized:\n",list_left_normalized)
    return byte_data,list_left_normalized,x

def generate_sweepwave(waveinfo):#从左至右依次为：采样率、声道数（默认为2）、位深(2)、分贝数、起始频率、终止频率、持续时间、扫频类型
    samplerate = waveinfo[0]
    ch_num = waveinfo[1]
    bytes_width = waveinfo[2]
    xdb = waveinfo[3]
    start_freq = waveinfo[4]
    end_freq = waveinfo[5]
    duration = waveinfo[6]
    sweep_type = waveinfo[7]
    # volume xdb
    db = math.pow(10,xdb/20)
    # bytes needed every sample
    bits_width = bytes_width*8
    max_val = 2**(bits_width-1) - 1 #量化后的最大值
    #print ('max_val : ', max_val)
    volume = max_val*db #2**(bits_width-1) - 1
    t = np.linspace(0, duration, int(duration * samplerate), endpoint=False)
    sweep_signal = np.zeros(int(duration * samplerate))
    if sweep_type == '线性':
        sweep_signal = volume * signal.chirp(t, f0=start_freq, f1=end_freq, t1=duration, method='linear')
        print("create linear sweep signal")
    elif sweep_type == '对数':    
        sweep_signal = volume * signal.chirp(t, f0=start_freq, f1=end_freq, t1=duration, method='logarithmic')
        print("create logarithmic sweep signal")
    elif sweep_type == '双曲线':#hyperbolic    
        sweep_signal = volume * signal.chirp(t, f0=start_freq, f1=end_freq, t1=duration, method='hyperbolic')
        print("create hyperbolic sweep signal")
    elif sweep_type == '抛物线':#quadratic
        sweep_signal = volume * signal.chirp(t, f0=start_freq, f1=end_freq, t1=duration, method='quadratic')
        print("create quadratic sweep signal")
    # plt.plot(t,sweep_signal)
    # plt.show()

    list_left = sweep_signal.tolist()
    list_right = sweep_signal.tolist()

    list_total = []#2个声轨合并为一维列表list
    for i in range(len(list_left)):
        list_total.append(list_left[i])
        list_total.append(list_right[i])

    byte_data = b''#byte格式的双声道数据
    for v in list_total:
        data = struct.pack('<h',int(v))
        byte_data += data
    #print(byte_data)

    list_left_normalized = []
    for i in list_left:#list归一化
        list_left_normalized.append(i / math.pow(2, 8 * bytes_width - 1))
    # plt.plot(t,sweep_signal)
    # plt.show()
    return byte_data,list_left_normalized,t

def generate_AM_modify(waveinfo):#从左至右依次为：采样率、声道数（默认为2）、位深(2)、分贝数、消息信号类型、消息信号频率、载波频率、持续时间、相位偏移（度数单位）或占空比（百分制）
    samplerate = waveinfo[0]
    ch_num = waveinfo[1]
    bytes_width = waveinfo[2]
    xdb = waveinfo[3]
    message_type = waveinfo[4]
    message_freq = waveinfo[5]
    carrier_freq = waveinfo[6]
    duration = waveinfo[7]
    offset_or_ratio = waveinfo[8]
    modulation_index = waveinfo[9]

    db = math.pow(10,xdb/20)
    sample_width = bytes_width
    bits_width = sample_width*8
    max_val = 2**(bits_width-1) - 1
    volume = max_val*db

    print("采样率{}，原信号类型{}，原信号频率{}，载波频率{}，持续时间{}，相位或占空比{}，调制参数{}".format(samplerate,message_type,message_freq,carrier_freq,duration,offset_or_ratio,modulation_index))
    t = np.linspace(0, duration, int(duration * samplerate), endpoint=False)
    # 载波信号
    carrier_signal = np.sin(2 * np.pi * carrier_freq * t)
    # 消息信号
    if message_type == "正弦波":
        message_signal = volume * np.sin(2 * np.pi * message_freq * t + offset_or_ratio/180 *np.pi)#正弦
    elif message_type == "矩形波":
        message_signal = signal.square(2 * np.pi * message_freq * t, duty=offset_or_ratio/100)#矩形
    # AM调制信号
    modulated_signal = (1 + modulation_index * message_signal) * carrier_signal
    #绘制信号波形
    """ plt.figure(figsize=(10, 6))
    plt.subplot(3, 1, 1)
    plt.plot(t, carrier_signal)

    plt.subplot(3, 1, 2)
    plt.plot(t, message_signal)

    plt.subplot(3, 1, 3)
    plt.plot(t, modulated_signal)

    plt.tight_layout()
    plt.show() """

    list_left = modulated_signal.tolist()
    list_right = modulated_signal.tolist()

    list_total = []#2个声轨合并为一维列表list
    for i in range(len(list_left)):
        list_total.append(list_left[i])
        list_total.append(list_right[i])

    byte_data = b''#byte格式的双声道数据
    for v in list_total:
        data = struct.pack('<h',int(v))
        byte_data += data
    #print(byte_data)

    list_left_normalized = []
    for i in list_left:#list归一化
        list_left_normalized.append(i / math.pow(2, 8 * bytes_width - 1))

    return byte_data,list_left_normalized,t

def generate_FM_modify(waveinfo):#从左至右依次为：采样率、声道数（默认为2）、位深(2)、分贝数、消息信号类型、消息信号频率、载波频率、持续时间、相位偏移（度数单位）或占空比（百分制）
    samplerate = waveinfo[0]
    ch_num = waveinfo[1]
    bytes_width = waveinfo[2]
    xdb = waveinfo[3]
    message_type = waveinfo[4]
    message_freq = waveinfo[5]
    carrier_freq = waveinfo[6]
    duration = waveinfo[7]
    offset_or_ratio = waveinfo[8]
    modulation_index = waveinfo[9]

    db = math.pow(10,xdb/20)
    sample_width = bytes_width
    bits_width = sample_width*8
    max_val = 2**(bits_width-1) - 1
    volume = max_val*db

    print("采样率{}，原信号类型{}，原信号频率{}，载波频率{}，持续时间{}，相位或占空比{}，调制参数{}".format(samplerate,message_type,message_freq,carrier_freq,duration,offset_or_ratio,modulation_index))
    t = np.linspace(0, duration, int(duration * samplerate), endpoint=False)
    # 载波信号
    carrier_signal = np.sin(2 * np.pi * carrier_freq * t)
    # 消息信号
    if message_type == "正弦波":
        message_signal = volume * np.sin(2 * np.pi * message_freq * t + offset_or_ratio/180 *np.pi)#正弦
    elif message_type == "矩形波":
        message_signal = signal.square(2 * np.pi * message_freq * t, duty=offset_or_ratio/100)#矩形
    # FM调制信号
    modulated_signal = volume * signal.chirp(t, f0=carrier_freq - modulation_index * message_freq, 
                               t1=duration, f1=carrier_freq + modulation_index * message_freq)
    #绘制信号波形
    """ plt.figure(figsize=(10, 6))
    plt.subplot(3, 1, 1)
    plt.plot(t, carrier_signal)

    plt.subplot(3, 1, 2)
    plt.plot(t, message_signal)

    plt.subplot(3, 1, 3)
    plt.plot(t, modulated_signal)

    plt.tight_layout()
    plt.show() """

    list_left = modulated_signal.tolist()
    list_right = modulated_signal.tolist()

    list_total = []#2个声轨合并为一维列表list
    for i in range(len(list_left)):
        list_total.append(list_left[i])
        list_total.append(list_right[i])

    byte_data = b''#byte格式的双声道数据
    for v in list_total:
        data = struct.pack('<h',int(v))
        byte_data += data
    #print(byte_data)

    list_left_normalized = []
    for i in list_left:#list归一化
        list_left_normalized.append(i / math.pow(2, 8 * bytes_width - 1))

    return byte_data,list_left_normalized,t

if __name__ == '__main__':
    #byte_data,Timedata,x = generate_sinewave(waveinfo)
    # waveinfo = [48000, 2, 2, -3, 100, 100, 0.1, 50]
    # generate_squarewave(waveinfo)
    generate_FM_modify([48000, 2, 2, -3, "正弦波", 10, 100, 1, 0, 0])
    #byte_data1,list_left_normalized1,t1 = generate_sweepwave([48000, 2, 2, -3, 1, 10, 1, '线性'])

    #print("byte:\n",byte_data)
    #print("list:\n",Timedata)
    #print(x)