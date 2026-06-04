def build_waveform_levels(audio_segment, bin_count=2000):
    """Downsample audio to normalized 0-1 peak levels for drawing."""
    duration_ms = len(audio_segment)
    if duration_ms <= 0:
        return []

    step = max(1, duration_ms // bin_count)
    levels = []

    for i in range(bin_count):
        start = i * step
        if start >= duration_ms:
            levels.append(0.0)
            continue

        end = min(start + step, duration_ms)
        chunk = audio_segment[start:end]
        levels.append(float(chunk.rms))

    peak = max(levels) if levels else 1.0
    if peak <= 0:
        return levels

    return [level / peak for level in levels]
