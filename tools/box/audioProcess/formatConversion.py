from pydub import AudioSegment


def transAudio(file_path, type):
    '''
    转换音频格式
    :param file_path: 待转换的文件路径
    :param type: 目标格式
    '''

    # 获取文件名
    file_name = file_path.split('/')[-1]

    # 获取原始格式
    old_type = file_name.split('.')[-1]

    # 根据不同格式读取音频数据
    if old_type == 'mp3':
        song = AudioSegment.from_mp3(file_path)
    elif old_type == 'ogg':
        song = AudioSegment.from_ogg(file_path)
    elif old_type == 'wav':
        song = AudioSegment.from_wav(file_path)
    elif old_type == 'raw':
        song = AudioSegment.from_raw(file_path)
    else:
        return

    # 新的文件名
    new_file_name = file_name.split('.')[0] + '.' + type

    # 转换格式并输出到指定文件路径
    song.export('/home/ubuntu/Python_Workspace/SJTB/static/audio/'+new_file_name, format=type)

    return '/home/ubuntu/Python_Workspace/SJTB/static/audio/'+new_file_name,new_file_name