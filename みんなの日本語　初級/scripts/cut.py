import os
from pydub import AudioSegment
from pydub.silence import detect_silence

file_name = "第50课.wav"
dir_name = "output"

if __name__ == "__main__":
    # 创建输出目录。
    try:
        os.mkdir(dir_name)
    except FileExistsError:
        pass

    # 读取音频文件。
    sound = AudioSegment.from_file(file_name)

    # 检测静音。
    start_end = detect_silence(sound, min_silence_len=500, silence_thresh=-50)

    # 分割音频。
    start_end = [[s, e] for (_, s), (e, _) in zip(start_end, start_end[1:])]
    segments = [sound[s - 200 : e + 400] for (s, e) in start_end]

    # 写入文件。
    for i, segment in enumerate(segments):
        segment.export(f"{dir_name}/{i}.mp3")
