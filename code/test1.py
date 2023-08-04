import pyaudio
import time

path = "record.wav"
data_list = []  # 录制用list会好一点，因为bytes是常量，+操作会一直开辟新存储空间，时间开销大


def decode_wavedata(self,wavedata,wavewidth,wavechannel):#byte转list
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
        Timedata.append(b)
    Timedata = np.array(Timedata)
    Timedata.shape = -1, wavechannel
    Timedata = Timedata.T

def callback(in_data, frame_count, time_info, status):
    data_list.append(in_data)
    # output=False时数据可以直接给b""，但是状态位还是要保持paContinue，如果是paComplete一样会停止录制
    print("data = ",in_data)
    print("data type is ",type(in_data))
    print("data len is",len(in_data))
    print("frame_count = ",frame_count)
    print("frame_count type is ",type(frame_count))
    print("time info :",time_info)
    print("time info type is ",type(time_info))
    print("status = ",status)
    print("status type is ",type(status))
    return b"", pyaudio.paContinue

record_seconds = 3  # 录制时长/秒
pformat = pyaudio.paInt16
channels = 1
rate = 16000  # 采样率/Hz

audio = pyaudio.PyAudio()
stream = audio.open(format=pformat,
                    channels=channels,
                    rate=rate,
                    input=True,
                    stream_callback=callback)

stream.start_stream()
print("开始录制1")

t1 = time.time()
# 录制在stop_stream之前应该都是is_active()的，所以这里不能靠它来判断录制是否结束
while time.time() - t1 < record_seconds:
    time.sleep(0.1)
    if 0.2 < time.time() - t1 < 2.8:
        stream.stop_stream()
        print("暂停录制")
    if time.time() - t1 >= 2.8:
        stream.start_stream()
        print("开始录制2")

# wav_data = b"".join(data_list)
# with wave.open("tmp.wav", "wb") as wf:
#     wf.setnchannels(channels)
#     wf.setsampwidth(pyaudio.get_sample_size(pformat))
#     wf.setframerate(rate)
#     wf.writeframes(wav_data)



stream.stop_stream()
stream.close()
print("停止录制")
print("total data len is ",len(data_list))
audio.terminate()


