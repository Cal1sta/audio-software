import pyaudio

def get_device_info():#查询当前接入的输入输出设备信息
    input_device = []
    output_device = []
    device_dict = {}
    p = pyaudio.PyAudio()
    device_index = 0
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            input_device.append(device_info)
        if device_info['maxOutputChannels'] > 0:
            output_device.append(device_info)
    return input_device, output_device

def get_device_index_by_name(device_name):
    p = pyaudio.PyAudio()
    device_index = 0
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info['name']==device_name:
            return i
    return -1
    

if __name__ == '__main__':
    input_device,output_device = get_device_info()
    for i in range(len(input_device)):
        print(input_device[i])
    for i in range(len(output_device)):
        print(output_device[i])