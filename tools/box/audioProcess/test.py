from tools.box.audioProcess import audio2text,formatConversion


def testTransAudio():
    formatConversion.transAudio('/home/ubuntu/Python_Workspace/SJTB/static/audio/a2t_zh_simple.mp3', 'wav')

def testAudio2Text():
    audio2text.audio2text('/home/ubuntu/Python_Workspace/SJTB/static/audio/a2t_zh_simple.wav','zh-CN')


if __name__ == '__main__':
    # testTransAudio()
    testAudio2Text()