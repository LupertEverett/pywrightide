from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QColor, QPainter
from PyQt6.QtWidgets import QLabel


class SpriteViewWidget(QLabel):
    """A custom label that draws a checkerboard pattern as a background and centers pixmaps"""

    def __init__(self, parent=None):
        super().__init__(parent)

    def scale_and_pad_pixmap(self, pixmap, target_width, target_height):
        scaled = pixmap.scaledToHeight(target_height)

        result = QPixmap(target_width, target_height)
        result.fill(Qt.GlobalColor.transparent)  # correctly sized canvas

        painter = QPainter(result)
        # center pixmap
        x_offset = (target_width - scaled.width()) // 2
        painter.drawPixmap(x_offset, 0, scaled)
        painter.end()

        return result

    def setPixmap(self, new_pixmap):
        if new_pixmap:
            scaled_pixmap = self.scale_and_pad_pixmap(new_pixmap, self.width(), self.height())
            super().setPixmap(scaled_pixmap)

    def paintEvent(self, event):
        painter = QPainter(self)

        light_gray = QColor(210, 210, 210)
        white = QColor(255, 255, 255)

        for y in range(0, self.height(), 16):
            for x in range(0, self.width(), 16):
                color = light_gray if ((x // 16) + (y // 16)) % 2 else white
                painter.fillRect(x, y, 16, 16, color)

        if self.pixmap() and not self.pixmap().isNull():
            painter.drawPixmap(0, 0, self.pixmap())