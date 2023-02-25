# Provides ways to view various assets (textures, sound, music...)

from PyQt5.QtWidgets import QDockWidget, QTabWidget

from .AssetBrowserTextureWidget import AssetManagerTextureWidget
from .AssetBrowserAudioWidget import AssetBrowserAudioWidget, AudioType
from data.PyWrightGame import PyWrightGame


class AssetBrowserRootWidget(QDockWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Asset Browser")

        self.tab_widget = QTabWidget(self)

        self.setWidget(self.tab_widget)

        self.texture_browser = AssetManagerTextureWidget(self)
        self.music_browser = AssetBrowserAudioWidget(AudioType.Music, self)

        self.tab_widget.addTab(self.texture_browser, "Textures")
        self.tab_widget.addTab(self.music_browser, "Music")

    def update_assets(self, pywright_path: str, selected_game: PyWrightGame):
        self.texture_browser.select_pywright(pywright_path)
        self.texture_browser.set_selected_game(selected_game)
        self.texture_browser.refresh_art_folders()

        self.music_browser.select_pywright(pywright_path)
        self.music_browser.set_selected_game(selected_game)
        self.music_browser.refresh_music_folders()
