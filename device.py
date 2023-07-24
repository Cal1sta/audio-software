import pyaudio

def get_device_info():#查询当前接入的输入输出设备信息
    input_device = []
    output_device = []
    p = pyaudio.PyAudio()
    device_index = 0
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            input_device.append(device_info)
        if device_info['maxOutputChannels'] > 0:
            output_device.append(device_info)
    # print("input device:")
    # for i in range(len(input_device)):
    #     print(input_device[i])
    # print("output device:")
    # for i in range(len(output_device)):
    #     print(output_device[i])
    return input_device, output_device