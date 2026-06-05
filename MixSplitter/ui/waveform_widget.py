import math

from PySide6.QtWidgets import QWidget
from PySide6.QtGui import QPainter, QColor, QPen, QFont
from PySide6.QtCore import Qt, QRect, Signal
from core.markers import Marker

from core.segments import Segment


class WaveformWidget(QWidget):
    segments_changed = Signal()
    markers_changed = Signal()
    seek_requested = Signal(float)

    PLAYHEAD_HIT_PX = 12
    TIMELINE_HEIGHT = 30
    MIN_VISIBLE_SECONDS = 5.0
    ZOOM_STEP = 1.15

    def __init__(self, parent=None):
        super().__init__(parent)

        self.audio = None
        self.waveform_levels = []
        self.segments = []
        self.selected_segment = None
        self.markers = []
        self.playhead_time = 0.0
        self.selected_marker = None

        self.zoom_factor = 1.0
        self.view_start = 0.0

        self.is_scrubbing = False
        self.is_segment_drag = False
        self.drag_start_x = None
        self.drag_end_x = None

        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)

    def set_audio(self, audio_data):
        self.audio = audio_data
        self.waveform_levels = audio_data.get("levels", [])
        self.segments = []
        self.markers = []
        self.selected_marker = None
        self.zoom_factor = 1.0
        self.view_start = 0.0
        self.update()

    def set_playhead(self, seconds):
        self.playhead_time = seconds
        self.update()

    @property
    def view_span(self):
        if not self.audio:
            return 1.0
        return self.audio["duration"] / self.zoom_factor

    def _max_zoom(self):
        if not self.audio:
            return 1.0
        return max(1.0, self.audio["duration"] / self.MIN_VISIBLE_SECONDS)

    def _clamp_view(self):
        if not self.audio:
            return
        max_start = max(0.0, self.audio["duration"] - self.view_span)
        self.view_start = max(0.0, min(self.view_start, max_start))

    def _time_to_x(self, seconds):
        if self.width() <= 0:
            return 0.0
        return ((seconds - self.view_start) / self.view_span) * self.width()

    def _x_to_time(self, x):
        width = max(1, self.width())
        return self.view_start + (x / width) * self.view_span

    def _waveform_height(self):
        return max(1, self.height() - self.TIMELINE_HEIGHT)

    def _playhead_x(self):
        return self._time_to_x(self.playhead_time)

    def _seek_to_x(self, x):
        seconds = max(0.0, min(self._x_to_time(x), self.audio["duration"]))
        self.playhead_time = seconds
        self.seek_requested.emit(seconds)
        self.update()

    def _near_playhead(self, x):
        return abs(x - self._playhead_x()) <= self.PLAYHEAD_HIT_PX

    def _format_time(self, seconds):
        total = max(0, int(seconds))
        hours, remainder = divmod(total, 3600)
        minutes, secs = divmod(remainder, 60)
        if hours > 0:
            return f"{hours}:{minutes:02d}:{secs:02d}"
        return f"{minutes}:{secs:02d}"

    def _tick_interval(self):
        target_seconds = self.view_span / max(1, self.width()) * 80
        for interval in (1, 2, 5, 10, 15, 30, 60, 120, 300, 600, 900, 1800, 3600):
            if interval >= target_seconds:
                return interval
        return 3600

    # -------------------------
    # MOUSE INTERACTION
    # -------------------------

    def wheelEvent(self, event):
        if not self.audio:
            return

        delta = event.angleDelta().y()
        if delta == 0:
            return

        x = event.position().x()

        if event.modifiers() & Qt.ShiftModifier:
            pan_amount = self.view_span * 0.1
            self.view_start += -pan_amount if delta > 0 else pan_amount
            self._clamp_view()
            self.update()
            return

        anchor_time = self._x_to_time(x)
        factor = self.ZOOM_STEP if delta > 0 else 1 / self.ZOOM_STEP
        new_zoom = max(1.0, min(self.zoom_factor * factor, self._max_zoom()))

        if new_zoom == self.zoom_factor:
            return

        self.zoom_factor = new_zoom
        self.view_start = anchor_time - (x / max(1, self.width())) * self.view_span
        self._clamp_view()
        self.update()

    def mousePressEvent(self, event):
        if not self.audio or event.button() != Qt.LeftButton:
            return

        if event.position().y() >= self._waveform_height():
            return

        x = event.position().x()
        self.drag_start_x = x
        self.drag_end_x = x

        if event.modifiers() & Qt.ShiftModifier:
            self.is_segment_drag = True
            return

        self.is_scrubbing = True
        self._seek_to_x(x)

    def mouseMoveEvent(self, event):
        x = event.position().x()

        if self.is_scrubbing:
            self._seek_to_x(x)
            return

        if self.is_segment_drag:
            self.drag_end_x = x
            self.update()
            return

        if event.position().y() < self._waveform_height() and self._near_playhead(x):
            self.setCursor(Qt.SizeHorCursor)
        else:
            self.unsetCursor()

    def mouseReleaseEvent(self, event):
        if not self.audio or event.button() != Qt.LeftButton:
            return

        if self.is_scrubbing:
            self.is_scrubbing = False
            return

        if not self.is_segment_drag:
            return

        self.is_segment_drag = False
        self.drag_end_x = event.position().x()

        start_time = self._x_to_time(min(self.drag_start_x, self.drag_end_x))
        end_time = self._x_to_time(max(self.drag_start_x, self.drag_end_x))

        if abs(end_time - start_time) > 1:
            self.segments.append(
                Segment(
                    start=start_time,
                    end=end_time,
                    name=f"Segment {len(self.segments) + 1}",
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
                name=f"Marker {len(self.markers)+1}",
            )
        )

        self.markers_changed.emit()
        self.update()

    def delete_marker(self, index):
        if 0 <= index < len(self.markers):
            del self.markers[index]
            self.markers_changed.emit()
            self.update()

    def delete_all_markers(self):
        if not self.markers:
            return
        self.markers.clear()
        self.markers_changed.emit()
        self.update()

    # -------------------------
    # Keyboard Interaction
    # -------------------------

    def keyPressEvent(self, event):
        if not self.audio:
            return

        if event.key() == Qt.Key_M:
            self.add_marker()

    # -------------------------
    # DRAWING
    # -------------------------

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(15, 15, 15))

        if not self.audio:
            return

        width = self.width()
        wave_height = self._waveform_height()
        timeline_top = wave_height
        levels = self.waveform_levels
        duration = self.audio["duration"]

        # -------------------------
        # waveform
        # -------------------------
        painter.setPen(QPen(QColor(0, 200, 0), 1))

        mid = wave_height // 2
        max_bar = max(1, int((wave_height / 2) * 0.92))

        if levels:
            last_idx = len(levels) - 1
            for x in range(width):
                t = self._x_to_time(x)
                if t < 0 or t > duration:
                    continue
                idx = int((t / duration) * last_idx)
                idx = max(0, min(idx, last_idx))
                y = int(levels[idx] * max_bar)
                painter.drawLine(x, mid - y, x, mid + y)

        # -------------------------
        # segments
        # -------------------------
        for seg in self.segments:
            self.draw_segment(painter, seg, wave_height)

        # -------------------------
        # active segment drag
        # -------------------------
        if self.is_segment_drag and self.drag_start_x is not None:
            painter.setBrush(QColor(0, 120, 255, 80))
            painter.setPen(Qt.NoPen)

            rect = QRect(
                int(min(self.drag_start_x, self.drag_end_x)),
                0,
                int(abs(self.drag_end_x - self.drag_start_x)),
                wave_height,
            )
            painter.drawRect(rect)

        # -------------------------
        # playhead
        # -------------------------
        playhead_x = int(self._playhead_x())
        if 0 <= playhead_x <= width:
            painter.setPen(QPen(QColor(255, 0, 0), 2))
            painter.drawLine(playhead_x, 0, playhead_x, self.height())

        # -------------------------
        # markers
        # -------------------------
        for marker in self.markers:
            x = int(self._time_to_x(marker.time))
            if x < 0 or x > width:
                continue

            selected = marker is self.selected_marker
            painter.setPen(QPen(QColor(255, 200, 200) if selected else QColor(255, 100, 100), 3 if selected else 1))
            painter.drawLine(x, 0, x, wave_height)
            painter.drawText(x + 2, 16, marker.name)

        # -------------------------
        # timeline
        # -------------------------
        self._draw_timeline(painter, width, timeline_top, playhead_x)

    def _draw_timeline(self, painter, width, timeline_top, playhead_x):
        timeline_height = self.TIMELINE_HEIGHT

        painter.fillRect(0, timeline_top, width, timeline_height, QColor(22, 22, 22))
        painter.setPen(QPen(QColor(60, 60, 60), 1))
        painter.drawLine(0, timeline_top, width, timeline_top)

        interval = self._tick_interval()
        tick_time = math.floor(self.view_start / interval) * interval

        painter.setFont(QFont("Segoe UI", 8))
        painter.setPen(QColor(140, 140, 140))

        while tick_time <= self.view_start + self.view_span:
            x = int(self._time_to_x(tick_time))
            if 0 <= x <= width:
                painter.drawLine(x, timeline_top + 2, x, timeline_top + timeline_height - 14)
                painter.drawText(x + 3, timeline_top + timeline_height - 4, self._format_time(tick_time))
            tick_time += interval

        if 0 <= playhead_x <= width:
            painter.setPen(QPen(QColor(255, 80, 80), 2))
            painter.drawLine(playhead_x, timeline_top, playhead_x, timeline_top + timeline_height)

            label = self._format_time(self.playhead_time)
            label_width = 52
            label_x = min(max(playhead_x + 4, 2), width - label_width)
            painter.fillRect(label_x, timeline_top + 4, label_width, 14, QColor(40, 40, 40))
            painter.setPen(QColor(255, 200, 200))
            painter.drawText(label_x + 4, timeline_top + 15, label)

    def draw_segment(self, painter, seg, wave_height):
        x1 = int(self._time_to_x(seg.start))
        x2 = int(self._time_to_x(seg.end))

        if x2 < 0 or x1 > self.width():
            return

        if self.selected_segment == seg:
            painter.setBrush(QColor(255, 80, 80, 100))
            painter.setPen(QColor(255, 0, 0))
        else:
            painter.setBrush(QColor(255, 255, 0, 60))
            painter.setPen(QColor(255, 200, 0))

        painter.drawRect(x1, 0, x2 - x1, wave_height)
