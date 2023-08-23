import numpy as np
from scipy import signal
import matplotlib.pyplot as plt

# 定义调制信号的参数
carrier_freq = 1000  # 载波信号频率
message_freq = 100  # 消息信号频率
modulation_index = 1.5  # 调制指数

# 生成时间轴
duration = 1  # 信号持续时间
sampling_rate = 10000  # 采样率
t = np.linspace(0, duration, int(duration * sampling_rate), endpoint=False)

# 载波信号
carrier_signal = np.sin(2 * np.pi * carrier_freq * t)

# 消息信号
message_signal = np.sin(2 * np.pi * message_freq * t)

# FM调制信号
modulated_signal = signal.chirp(t, f0=carrier_freq - modulation_index * message_freq, 
                               t1=duration, f1=carrier_freq + modulation_index * message_freq)

# 绘制信号图形
plt.figure(figsize=(10, 6))
plt.subplot(3, 1, 1)
plt.plot(t, carrier_signal)
plt.title('Carrier Signal')
plt.xlabel('Time')
plt.ylabel('Amplitude')

plt.subplot(3, 1, 2)
plt.plot(t, message_signal)
plt.title('Message Signal')
plt.xlabel('Time')
plt.ylabel('Amplitude')

plt.subplot(3, 1, 3)
plt.plot(t, modulated_signal)
plt.title('FM Modulated Signal')
plt.xlabel('Time')
plt.ylabel('Amplitude')

plt.tight_layout()
plt.show()
