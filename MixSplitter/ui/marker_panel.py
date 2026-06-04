from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QInputDialog

from core.segments import Segment

class MarkerPanel(QWidget):
    def __init__(self, waveform):
        super().__init__()

        self.waveform = waveform

        layout = QVBoxLayout()

        self.list = QListWidget()

        add_btn = QPushButton("Add Marker")
        gen_btn = QPushButton("Generate Segments")

        add_btn.clicked.connect(self.add_marker)
        gen_btn.clicked.connect(self.generate_segments)

        layout.addWidget(self.list)
        layout.addWidget(add_btn)
        layout.addWidget(gen_btn)

        self.setLayout(layout)

    def refresh(self):
        self.list.clear()
        for m in self.waveform.markers:
            self.list.addItem(f"{m.name} - {m.time:.1f}s")

    def add_marker(self):
        self.waveform.add_marker()
        self.refresh()

    def generate_segments(self):
        self.waveform.segments = []

        sorted_markers = sorted(self.waveform.markers, key=lambda m: m.time)

        for i in range(len(sorted_markers) - 1):
            start = sorted_markers[i]
            end = sorted_markers[i + 1]

            self.waveform.segments.append(
                Segment(
                    start=start.time,
                    end=end.time,
                    name=start.name,
                )
            )

        self.waveform.update()
        self.waveform.segments_changed.emit()