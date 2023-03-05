# Provides ways to view various assets (textures, sound, music...)

from PyQt5.QtWidgets import QDockWidget, QTabWidget
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QAudio
from PyQt5.QtCore import QUrl

from .AssetBrowserTextureWidget import AssetManagerTextureWidget
from .AssetBrowserAudioWidget import AssetBrowserAudioWidget, AudioType
from data.PyWrightGame import PyWrightGame


class AssetBrowserRootWidget(QDockWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Asset Browser")

        self.tab_widget = QTabWidget(self)

        self.setWidget(self.tab_widget)

        self.audio_player = QMediaPlayer(self)

        self.texture_browser = AssetManagerTextureWidget(self)
        self.music_browser = AssetBrowserAudioWidget(AudioType.Music, self)
        self.sfx_browser = AssetBrowserAudioWidget(AudioType.Sfx, self)

        self.music_browser.audio_play_requested.connect(self._handle_audio_player_play)
        self.music_browser.audio_stop_requested.connect(self._handle_audio_player_stop)

        self.sfx_browser.audio_play_requested.connect(self._handle_audio_player_play)
        self.sfx_browser.audio_stop_requested.connect(self._handle_audio_player_stop)

        self.tab_widget.addTab(self.texture_browser, "Textures")
        self.tab_widget.addTab(self.music_browser, "Music")
        self.tab_widget.addTab(self.sfx_browser, "SFX")

    def update_assets(self, pywright_path: str, selected_game: PyWrightGame):
        self.texture_browser.select_pywright(pywright_path)
        self.texture_browser.set_selected_game(selected_game)
        self.texture_browser.refresh_art_folders()

        self.music_browser.select_pywright(pywright_path)
        self.music_browser.set_selected_game(selected_game)
        self.music_browser.refresh_music_folders()

        self.sfx_browser.select_pywright(pywright_path)
        self.sfx_browser.set_selected_game(selected_game)
        self.sfx_browser.refresh_music_folders()

    def _handle_audio_player_play(self, path: str, audio_type: AudioType):
        if self.audio_player.state() == QMediaPlayer.PlayingState:
            self._handle_audio_player_stop()

        self.audio_player.setMedia(QMediaContent(QUrl.fromLocalFile(path)))
        self.audio_player.setVolume(50)
        self.audio_player.play()

    def _handle_audio_player_stop(self):
        self.audio_player.stop()
