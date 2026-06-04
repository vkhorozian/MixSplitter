def export_segment(audio, start, end, output_path):
    start_ms = int(start * 1000)
    end_ms = int(end * 1000)
    audio[start_ms:end_ms].export(output_path, format="mp3")
