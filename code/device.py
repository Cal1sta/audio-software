import pyaudio

def get_device_info():#查询当前接入的输入输出设备信息
    input_device = []
    output_device = []
    device_dict = {}
    hostapi = 2 # 主机为MME
    p = pyaudio.PyAudio()
    device_index = 0
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0 and device_info['hostApi'] == hostapi:
            input_device.append(device_info)
            input_device[-1]["combobox_index"] = -1
        if device_info['maxOutputChannels'] > 0 and device_info['hostApi'] == hostapi:
            output_device.append(device_info)
            output_device[-1]["combobox_index"] = -1
    return input_device, output_device

def get_device_index_by_combobox(device_list,combobox_index):
    p = pyaudio.PyAudio()
    for device_dict in device_list:
        print(device_dict)
        if device_dict['combobox_index'] == combobox_index:
            return device_dict['index']
    return -1
    

if __name__ == '__main__':
    input_device,output_device = get_device_info()
    print("-------------------------------------------\ninput device:")
    for j in range(4):
        print("hostApi:",j)
        for device in input_device:
            if device['hostApi'] == j:
                print(device['name'])
    print("-------------------------------------------\noutput device:")
    for j in range(4):
        print("hostApi:",j)
        for device in output_device:
            if device['hostApi'] == j:
                print(device['name'])