# MixSplitter

A desktop app for splitting long MP3 mixes into separate tracks. Load a DJ set or podcast, mark regions on a waveform, and export each segment as its own MP3 file.

Built with Python and PySide6 (Qt).

## Features

- Load MP3 files and view a normalized waveform with a time ruler
- Zoom and pan the waveform for precise editing
- Click or drag to scrub through the track with a moving playhead
- Create segments manually with Shift + drag
- Add markers and generate segments between markers (keeps existing manual segments)
- Delete individual markers or clear all markers
- Rename, select, and delete segments from the sidebar
- Play, pause, and stop playback
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

### Loading and playback

1. Click **Load MP3** and choose your file.
2. **Click or drag** on the waveform to move the red playhead and scrub through the track.
3. Use **Play**, **Pause**, or **Stop**, or press **Space** to toggle playback.
4. The timeline along the bottom shows time ticks and the current playhead position.

### Creating segments manually

1. Hold **Shift** and **drag** on the waveform to highlight a region (must be longer than about 1 second).
2. The segment appears in the list on the right.
3. Click a segment in the list to select it on the waveform.
4. Use **Rename** or **Delete** to manage the selected segment.

### Using markers

Markers are useful when you want to split a mix at several points and generate segments between them.

1. Move the playhead to the desired position.
2. Press **M** or click **Add Marker** in the marker panel.
3. Repeat for each split point (you need at least two markers to generate segments).
4. Click **Generate Segments** to create segments between consecutive markers.
   - Manually created segments are **kept** — generated segments are added to the list.
5. To remove a bad marker, select it in the marker list and click **Delete Marker**.
6. Click **Delete All Markers** to clear every marker from the waveform.

### Zoom and pan

- **Scroll wheel** on the waveform zooms in/out, centered on the cursor.
- **Shift + scroll wheel** pans left/right when zoomed in.

### Export

1. Click **Export All** when your segments are ready.
2. Files are saved to `Documents/MixSplitter/Exports/`  
   (on Windows: `C:\Users\<you>\Documents\MixSplitter\Exports\`)

## Keyboard shortcuts

| Input | Action |
|-------|--------|
| Click / drag on waveform | Move playhead (seek) |
| `Shift` + drag on waveform | Create segment |
| Scroll wheel on waveform | Zoom in / out (centered on cursor) |
| `Shift` + scroll wheel | Pan left / right when zoomed |
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
- Generating segments from markers requires at least two markers.
- Re-running **Generate Segments** will add another set of marker-based segments without removing manual ones.
- Do not commit large sample MP3s to the repository; keep test audio local or use Git LFS if needed.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
