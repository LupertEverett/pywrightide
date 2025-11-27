from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPalette, QImageReader, QPixmap, QWheelEvent
from PyQt6.QtWidgets import QMessageBox, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem

from data import IDESettings

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
        self._zoom_level = 1

    def wheelEvent(self, event: QWheelEvent):
        hasShift = bool(event.modifiers() & Qt.KeyboardModifier.ShiftModifier)
        hasControl = bool(event.modifiers() & Qt.KeyboardModifier.ControlModifier)

        if not hasShift and hasControl == IDESettings.get_image_viewer_zoom_style():
            # Zoom
            zoom_factor = 1.5 ** (event.angleDelta().y()/120)

            previous_zoom_level = self._zoom_level
            self._zoom_level *= zoom_factor

            # Limit zoom level:
            if self._zoom_level < 1:
                self._zoom_level = 1
                zoom_factor = self._zoom_level / previous_zoom_level
            elif self._zoom_level > 20:
                self._zoom_level = 20
                zoom_factor = self._zoom_level / previous_zoom_level
    
            self.scale(zoom_factor, zoom_factor)
        else:
            # Pan
            delta = event.angleDelta() if event.pixelDelta().isNull() else event.pixelDelta()
            x, y = delta.x(), delta.y()
            if hasShift:
                x, y = y, -x
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - x)
            self.verticalScrollBar()  .setValue(self.verticalScrollBar()  .value() - y)
