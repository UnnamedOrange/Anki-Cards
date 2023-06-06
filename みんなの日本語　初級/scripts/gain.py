from pydub import AudioSegment

file_name = "第50课.mp3"

if __name__ == "__main__":
    sound = AudioSegment.from_file(file_name)
    x = sound.max_dBFS
    sound = sound.apply_gain(-sound.max_dBFS)
    sound.export(file_name.replace(".mp3", ".wav"), format="wav")
    print("Done!")
