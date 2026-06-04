from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen
from PySide6.QtCore import Qt, QRect, Signal
from core.markers import Marker

from core.segments import Segment


class WaveformWidget(QWidget):
    segments_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.audio = None
        self.waveform_levels = []
        self.segments = []
        self.selected_segment = None
        self.markers = []
        self.playhead_time = 0
        self.selected_marker = None
        self.playhead_time = 0.0

        # selection state
        self.is_dragging = False
        self.drag_start_x = None
        self.drag_end_x = None

    def set_audio(self, audio_data):
        self.audio = audio_data
        self.waveform_levels = audio_data.get("levels", [])
        self.segments = []
        self.update()

    def set_playhead(self, seconds):
        self.playhead_time = seconds
        self.update()

    # -------------------------
    # MOUSE INTERACTION
    # -------------------------

    def mousePressEvent(self, event):
        if not self.audio:
            return

        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_start_x = event.position().x()
            self.drag_end_x = self.drag_start_x

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            self.drag_end_x = event.position().x()
            self.update()

    def mouseReleaseEvent(self, event):
        if not self.is_dragging or not self.audio:
            return

        self.is_dragging = False
        self.drag_end_x = event.position().x()

        start_x = min(self.drag_start_x, self.drag_end_x)
        end_x = max(self.drag_start_x, self.drag_end_x)

        duration = self.audio["duration"]
        width = self.width()

        # convert pixels -> time
        start_time = (start_x / width) * duration
        end_time = (end_x / width) * duration

        if abs(end_time - start_time) > 1:  # ignore tiny clicks
            self.segments.append(
                Segment(
                    start=start_time,
                    end=end_time,
                    name=f"Segment {len(self.segments) + 1}"
                )
            )
            self.segments_changed.emit()

        self.update()

    # -------------------------
    # MARKER MANAGEMENT
    # -------------------------

    def add_marker(self):
        if not self.audio:
            return
    
        self.markers.append(
            Marker(
                time=self.playhead_time,
                name=f"Marker {len(self.markers)+1}"
            )
        )
    
        self.update()

    # -------------------------
    # Keyboard Interaction
    # -------------------------

    def keyPressEvent(self, event):
        if not self.audio:
            return

        # M = add marker
        if event.key() == Qt.Key_M:
            self.add_marker()

    # -------------------------
    # DRAWING
    # -------------------------

    def paintEvent(self, event):
        painter = QPainter(self)

        # background
        painter.fillRect(self.rect(), QColor(15, 15, 15))

        if not self.audio:
            return

        width = self.width()
        height = self.height()
        levels = self.waveform_levels

        # -------------------------
        # waveform
        # -------------------------
        painter.setPen(QPen(QColor(0, 200, 0), 1))

        mid = height // 2
        max_bar = max(1, int((height / 2) * 0.92))

        if levels:
            last_idx = len(levels) - 1
            for x in range(width):
                idx = int((x / max(1, width - 1)) * last_idx)
                y = int(levels[idx] * max_bar)
                painter.drawLine(x, mid - y, x, mid + y)

        # -------------------------
        # draw existing segments
        # -------------------------
        for seg in self.segments:
            self.draw_segment(painter, seg, width, height)

        # -------------------------
        # draw active drag selection
        # -------------------------
        if self.is_dragging and self.drag_start_x is not None:
            painter.setBrush(QColor(0, 120, 255, 80))
            painter.setPen(Qt.NoPen)

            rect = QRect(
                int(min(self.drag_start_x, self.drag_end_x)),
                0,
                int(abs(self.drag_end_x - self.drag_start_x)),
                height
            )
            painter.drawRect(rect)

        if self.audio:
            x = int(
            (self.playhead_time / self.audio["duration"])
            * self.width()
        )

        painter.setPen(QPen(QColor(255, 0, 0), 2))
        painter.drawLine(x, 0, x, self.height())

        # -------------------------
        # draw markers
        # -------------------------
        for marker in self.markers:
            x = int((marker.time / self.audio["duration"]) * self.width())

            painter.setPen(Qt.red)
            painter.drawLine(x, 0, x, self.height())

            painter.drawText(x + 2, 20, marker.name)

    # -------------------------
    # SEGMENT DRAW
    # -------------------------

    def draw_segment(self, painter, seg, width, height):
        duration = self.audio["duration"]

        x1 = int((seg.start / duration) * width)
        x2 = int((seg.end / duration) * width)

        # highlight selected segment
        if hasattr(self, "selected_segment") and self.selected_segment == seg:
            painter.setBrush(QColor(255, 80, 80, 100))
            painter.setPen(QColor(255, 0, 0))
        else:
            painter.setBrush(QColor(255, 255, 0, 60))
            painter.setPen(QColor(255, 200, 0))

        painter.drawRect(x1, 0, x2 - x1, height)