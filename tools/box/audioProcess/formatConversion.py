from pydub import AudioSegment


def trans_mp3_to_wav(filepath):
    song = AudioSegment.from_mp3(filepath)
    song.export("now.wav", format="wav")