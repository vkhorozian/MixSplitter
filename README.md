# MixSplitter

A desktop app for splitting long MP3 mixes into separate tracks. Load a DJ set or podcast, mark regions on a waveform, and export each segment as its own MP3 file.

Built with Python and PySide6 (Qt).

## Features

- Load MP3 files and view a normalized waveform
- Drag on the waveform to create time-based segments
- Rename, select, and delete segments from the sidebar
- Add markers and generate segments between markers
- Play, pause, and stop playback with a moving playhead
- Export all segments to MP3 in one click

## Requirements

- **Python 3.11+** (tested on Python 3.13)
- **ffmpeg** on your system PATH (used by pydub for MP3 export)

### Windows (ffmpeg)

Download a build from [ffmpeg.org](https://ffmpeg.org/download.html) or [gyan.dev](https://www.gyan.dev/ffmpeg/builds/), extract it, and add the `bin` folder to your PATH.

## Installation

```bash
git clone https://github.com/vkhorozian/MixSplitter.git
cd MixSplitter
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

1. Click **Load MP3** and choose your file.
2. **Drag** left-to-right on the waveform to create a segment (selection must be longer than about 1 second).
3. Optionally use **Rename** or **Delete** on the selected segment in the list.
4. Use **Add Marker** / **Generate Segments** in the marker panel for marker-based splitting.
5. Click **Export All** when ready.

Exported files are saved to:

```
Documents/MixSplitter/Exports/
```

(on Windows: `C:\Users\<you>\Documents\MixSplitter\Exports\`)

## Keyboard shortcuts

| Key | Action |
|-----|--------|
| `Space` | Play / pause |
| `M` | Add marker at playhead |

## Project structure

```
MixSplitter/
├── main.py                 # Application entry point
├── requirements.txt
├── core/
│   ├── audio_loader.py     # MP3 loading via pydub
│   ├── waveform_levels.py  # Waveform peak normalization
│   ├── exporter.py         # Segment export
│   ├── segments.py         # Segment data model
│   ├── markers.py          # Marker data model
│   └── settings.py         # Export folder path
└── ui/
    ├── main_window.py      # Main window and controls
    ├── waveform_widget.py  # Waveform display and selection
    └── marker_panel.py     # Marker list and tools
```

## Notes

- Large files (e.g. full festival sets) may take a few seconds to load while waveform data is built.
- Do not commit large sample MP3s to the repository; keep test audio local or use Git LFS if needed.

## License

Add a license file (e.g. MIT) if you plan to share this project publicly.
