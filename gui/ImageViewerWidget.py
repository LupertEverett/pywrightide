from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QPalette, QImageReader, QPixmap, QWheelEvent, QMouseEvent
from PyQt6.QtWidgets import QMessageBox, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem

from pathlib import Path

class ImageViewerWidget(QGraphicsView):
    """A simple image viewer"""

    def __init__(self, image_path : Path, parent = None):
        super().__init__(parent)

        self._graphics_scene = QGraphicsScene()

        self._image_path = image_path
        self._image_width = 0
        self._image_height = 0
        self._zoom_level = 0

        self._photo = QGraphicsPixmapItem()

        self._graphics_scene.addItem(self._photo)
        self.setScene(self._graphics_scene)

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setBackgroundRole(QPalette.ColorRole.Dark)

        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

        if str(image_path) != "":
            self.load_image()

    def get_image_path(self):
        return self._image_path

    def load_image(self):
        reader = QImageReader(str(self._image_path))
        reader.setAutoTransform(True)
        new_image = reader.read()

        if new_image.isNull():
            error = reader.errorString()
            QMessageBox.information(self, "Error", "Cannot read the image file {}. Error: {}".format(str(self._image_path), error),
                                    QMessageBox.StandardButton.Ok, QMessageBox.StandardButton.Ok)
            return
        self._image_width = new_image.width()
        self._image_height = new_image.height()
        self._set_image(new_image)

    def _set_image(self, new_image):
        self._image = new_image
        self._photo.setPixmap(QPixmap.fromImage(self._image))
        self._zoom_level = 0

    def wheelEvent(self, event: QWheelEvent):
        zoom_in = event.angleDelta().y() > 0
        zoom_delta = event.angleDelta() / 8
        num_steps = zoom_delta / 15

        zoom_factor = 1.5 if zoom_in else 1 / 1.5

        self._zoom_level += num_steps.y()

        if self._zoom_level < 0:
            self._zoom_level = 0
            return
        elif self._zoom_level > 10:
            self._zoom_level = 10
            return

        self.scale(zoom_factor, zoom_factor)
