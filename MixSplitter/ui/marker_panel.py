from PySide6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton, QHBoxLayout

from core.segments import Segment


class MarkerPanel(QWidget):
    def __init__(self, waveform):
        super().__init__()

        self.waveform = waveform
        self.waveform.markers_changed.connect(self.refresh)

        layout = QVBoxLayout()

        self.list = QListWidget()
        self.list.itemClicked.connect(self.select_marker)

        add_btn = QPushButton("Add Marker")
        gen_btn = QPushButton("Generate Segments")
        delete_btn = QPushButton("Delete Marker")
        delete_all_btn = QPushButton("Delete All Markers")

        add_btn.clicked.connect(self.add_marker)
        gen_btn.clicked.connect(self.generate_segments)
        delete_btn.clicked.connect(self.delete_selected_marker)
        delete_all_btn.clicked.connect(self.delete_all_markers)

        layout.addWidget(self.list)
        layout.addWidget(add_btn)
        layout.addWidget(gen_btn)

        delete_row = QHBoxLayout()
        delete_row.addWidget(delete_btn)
        delete_row.addWidget(delete_all_btn)
        layout.addLayout(delete_row)

        self.setLayout(layout)

    def refresh(self):
        self.list.clear()
        for marker in self.waveform.markers:
            self.list.addItem(f"{marker.name} - {marker.time:.1f}s")

    def select_marker(self, item):
        index = self.list.row(item)
        if 0 <= index < len(self.waveform.markers):
            self.waveform.selected_marker = self.waveform.markers[index]
            self.waveform.update()

    def add_marker(self):
        self.waveform.add_marker()

    def delete_selected_marker(self):
        row = self.list.currentRow()
        if row < 0:
            return
        self.waveform.delete_marker(row)

    def delete_all_markers(self):
        self.waveform.delete_all_markers()

    def generate_segments(self):
        sorted_markers = sorted(self.waveform.markers, key=lambda m: m.time)
        if len(sorted_markers) < 2:
            return

        generated = []
        for i in range(len(sorted_markers) - 1):
            start = sorted_markers[i]
            end = sorted_markers[i + 1]
            generated.append(
                Segment(
                    start=start.time,
                    end=end.time,
                    name=start.name,
                )
            )

        self.waveform.segments.extend(generated)
        self.waveform.update()
        self.waveform.segments_changed.emit()
