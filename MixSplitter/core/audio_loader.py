from pydub import AudioSegment

from core.waveform_levels import build_waveform_levels


def load_audio(file_path):
    audio = AudioSegment.from_mp3(file_path)

    return {
        "path": file_path,
        "duration": len(audio) / 1000.0,
        "audio": audio,
        "levels": build_waveform_levels(audio),
    }