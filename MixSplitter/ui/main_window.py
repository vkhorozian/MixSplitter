from PySide6.QtWidgets import QMainWindow, QFileDialog, QWidget, QHBoxLayout, QPushButton, QVBoxLayout, QListWidget, QInputDialog

from PySide6.QtCore import QUrl, Qt
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput
from ui.waveform_widget import WaveformWidget
from core.audio_loader import load_audio
from core.exporter import export_segment
from core.settings import EXPORT_FOLDER
import os


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("MixSplitter")

        self.audio_data = None
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()

        self.player.setAudioOutput(self.audio_output)

        self.player.positionChanged.connect(
            self.on_position_changed
        )
        
        # ---------------- UI ----------------
        container = QWidget()
        layout = QHBoxLayout()

        # waveform
        self.waveform = WaveformWidget(self)
        self.waveform.segments_changed.connect(self.refresh_segment_list)

        # segment list panel
        self.segment_list = QListWidget()
        self.segment_list.setMinimumWidth(200)

        self.segment_list.itemClicked.connect(self.select_segment)

        # buttons
        btn_layout = QVBoxLayout()

        load_btn = QPushButton("Load MP3")
        load_btn.clicked.connect(self.load_file)

        rename_btn = QPushButton("Rename")
        rename_btn.clicked.connect(self.rename_segment)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self.delete_segment)

        export_btn = QPushButton("Export All")
        export_btn.clicked.connect(self.export_all)

        btn_layout.addWidget(load_btn)
        btn_layout.addWidget(rename_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addWidget(export_btn)
        btn_layout.addStretch()

        play_btn = QPushButton("Play")
        pause_btn = QPushButton("Pause")
        stop_btn = QPushButton("Stop")

        play_btn.clicked.connect(self.play_audio)
        pause_btn.clicked.connect(self.pause_audio)
        stop_btn.clicked.connect(self.stop_audio)

        btn_layout.addWidget(play_btn)
        btn_layout.addWidget(pause_btn)
        btn_layout.addWidget(stop_btn)

        layout.addLayout(btn_layout)

        from ui.marker_panel import MarkerPanel

        self.marker_panel = MarkerPanel(self.waveform)

        right_side = QWidget()
        right_layout = QVBoxLayout()
        right_layout.addWidget(self.segment_list)
        right_layout.addWidget(self.marker_panel)

        right_side.setLayout(right_layout)

        layout.addWidget(self.waveform, 1)
        layout.addWidget(right_side)

        container.setLayout(layout)
        self.setCentralWidget(container)

    # ---------------- Playback Methods ----------------

    def play_audio(self):
        self.player.play()

    def pause_audio(self):
        self.player.pause()

    def stop_audio(self):
        self.player.stop()

    # ---------------- LOAD ----------------

    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open MP3", "", "MP3 Files (*.mp3)")

        if not file_path:
            return

        self.audio_data = load_audio(file_path)
        self.waveform.set_audio(self.audio_data)
        self.refresh_segment_list()
        self.marker_panel.refresh()
        self.player.setSource(QUrl.fromLocalFile(file_path))

    def on_position_changed(self, position):
        seconds = position / 1000.0

        self.waveform.set_playhead(seconds)


    #----------------- Keyboard Shortcuts ----------------

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
        
            if self.player.playbackState() == QMediaPlayer.PlayingState:
                self.player.pause()
            else:
                self.player.play()
    
        elif event.key() == Qt.Key_M:
            self.waveform.add_marker()
    
            if hasattr(self, "marker_panel"):
                self.marker_panel.refresh()

    # ---------------- SEGMENTS ----------------

    def refresh_segment_list(self):
        self.segment_list.clear()

        for seg in self.waveform.segments:
            self.segment_list.addItem(seg.name)

    def select_segment(self, item):
        name = item.text()

        for seg in self.waveform.segments:
            if seg.name == name:
                self.waveform.selected_segment = seg
                self.waveform.update()

    def rename_segment(self):
        item = self.segment_list.currentItem()
        if not item:
            return

        new_name, ok = QInputDialog.getText(self, "Rename Segment", "Name:")
        if ok and new_name:
            for seg in self.waveform.segments:
                if seg.name == item.text():
                    seg.name = new_name

            self.refresh_segment_list()
            self.waveform.update()

    def delete_segment(self):
        item = self.segment_list.currentItem()
        if not item:
            return

        self.waveform.segments = [
            s for s in self.waveform.segments if s.name != item.text()
        ]

        self.refresh_segment_list()
        self.waveform.update()

    # ---------------- EXPORT ----------------

    def export_all(self):
        if not self.audio_data:
            return

        if not self.waveform.segments:
            return

        os.makedirs(EXPORT_FOLDER, exist_ok=True)

        audio = self.audio_data["audio"]

        for seg in self.waveform.segments:
            safe_name = seg.name.replace(" ", "_")
            output_path = os.path.join(EXPORT_FOLDER, f"{safe_name}.mp3")

            export_segment(
                audio,
                seg.start,
                seg.end,
                output_path
            )

        from PySide6.QtWidgets import QMessageBox

        QMessageBox.information(
            self,
            "Export Complete",
            f"Exported {len(self.waveform.segments)} file(s) to:\n{EXPORT_FOLDER}",
        )