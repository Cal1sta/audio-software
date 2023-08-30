import torch
import time
import math
import torchaudio
import numpy as np
import matplotlib.pyplot as plt
import struct

def calculate_axis(filename):
    print("读取文件...")
    waveform, sample_rate = torchaudio.load(filename)
    waveform = waveform.numpy()
    num_channels, num_frames = waveform.shape#读取声道数与帧数
    time_axis = torch.arange(0, num_frames) / sample_rate
    print("Shape of waveform:{}".format(waveform.shape)) #音频大小
    print("sample rate of waveform:{}".format(sample_rate))#采样率
    return time_axis, waveform[0], sample_rate

def data_fft(t,y,Fs):
    n=len(t)# 信号长度
    # fft_result = np.fft.fft(y)  # 使用NumPy的fft函数进行离散傅立叶变换
    # magnitude_dB = 20 * np.log10(np.abs(fft_result))
    # frequency = np.fft.fftfreq(len(t), 1.0/Fs)  # 计算频率轴上的点
    # return frequency[1:int(n/2)], magnitude_dB[1:int(n/2)]
    freq = np.fft.fftfreq(n, d=1/Fs)
    fft_y = np.fft.fft(y)
    amplitude_y = 20 * np.log10(np.abs(fft_y[1:int(n/2)]))
    #plt.plot(freq[1:int(n/2)], np.abs(fft_y[1:int(n/2)]))
    #plt.show()
    return freq[1:int(n/2)], np.abs(fft_y[1:int(n/2)])

def decode_wavedata(wavedata,wavewidth,wavechannel):#byte转list,归一化
    Timedata=[]
    n = int(len(wavedata) / wavewidth)
    i = 0
    j = 0
    for i in range(0, n):
        b = 0
        for j in range(0, wavewidth):
            temp = wavedata[i * wavewidth:(i + 1) * wavewidth][j] * int(math.pow(2, 8 * j))
            b += temp
        if b > int(math.pow(2, 8 * wavewidth - 1)):
            b = b - int(math.pow(2, 8 * wavewidth))
        Timedata.append(b/math.pow(2, 8 * wavewidth - 1))
    Timedata = np.array(Timedata)
    Timedata.shape = -1, wavechannel
    Timedata = Timedata.T
    return Timedata

def encode_wavedata(data_list):#list转byte
    byte_data = b''
    for data in data_list:
        byte_data += struct.pack('<h',int(data))

if __name__ == '__main__':
    filename = r"D:\audio-software\wav\sample1.wav"
    x,y,fs = calculate_axis(filename)
    f,a = data_fft(x,y,fs)
    plt.plot(f, a)
    plt.show()