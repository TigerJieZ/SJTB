import speech_recognition as sr

IBM_USERNAME = 'a624a57e-9e5b-4947-ab52-dcd41df3becd'
IBM_PASSWORD = 'JMD0xjhMo2f0'


def audio2text(file, language):
    r = sr.Recognizer()
    with sr.WavFile(file) as source:
        # 请把引号内改成你自己的音频文件路径
        audio = r.record(source)
        text = r.recognize_ibm(audio, username=IBM_USERNAME, password=IBM_PASSWORD, language=language)
        print(text)
