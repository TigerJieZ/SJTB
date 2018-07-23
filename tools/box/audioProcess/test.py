from tools.box.audioProcess.formatConversion import transAudio


def testTransAudio():
    transAudio('/home/ubuntu/Python_Workspace/SJTB/static/audio/simple.mp3', 'wav')


if __name__ == '__main__':
    testTransAudio()
