# Provides ways to view various assets (textures, sound, music...)
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QDockWidget, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout

import pygame.mixer

from .AssetBrowserTextureWidget import AssetManagerTextureWidget
from .AssetBrowserAudioWidget import AssetBrowserAudioWidget, AudioType
from data.PyWrightGame import PyWrightGame


# Custom event type that signals the audio file currently playing has finished
AUDIO_END_EVENT = pygame.USEREVENT + 1

class AssetBrowserRootWidget(QDockWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Asset Browser")
        self.visibilityChanged.connect(self._handle_visibility_change)
        self.setObjectName("AssetBrowserRootWidget")

        self.tab_widget = QTabWidget(self)

        main_widget = QWidget()
        layout = QVBoxLayout()

        layout.addWidget(self.tab_widget)
        layout.setContentsMargins(4, 4, 4, 4)
        main_widget.setLayout(layout)

        self.title_bar_widget = QWidget()
        title_bar_layout = QHBoxLayout()

        self.title_bar_widget.setLayout(title_bar_layout)
        title_bar_layout.setContentsMargins(4, 6, 4, 6)

        self.topLevelChanged.connect(self._handle_top_level)

        self.setWidget(main_widget)
        self.setTitleBarWidget(self.title_bar_widget)

        # Have to init the ENTIRETY of pygame because we cannot check audio finished events otherwise
        # which is rather dumb when your use case of pygame only consist of it playing audio files
        pygame.init()
        pygame.mixer.music.set_endevent(AUDIO_END_EVENT)

        self._pymixer_check_timer = QTimer(self)
        self._pymixer_check_timer.timeout.connect(self._check_pygame_events)
        self._pymixer_check_timer.start(100)

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
        self.music_browser.refresh_audio_folders()

        self.sfx_browser.select_pywright(pywright_path)
        self.sfx_browser.set_selected_game(selected_game)
        self.sfx_browser.refresh_audio_folders()

    def _handle_visibility_change(self):
        from .IDEMainWindow import IDEMainWindow
        ide_main_window: IDEMainWindow = self.parent()
        ide_main_window.update_toolbar_toggle_buttons()

    def _handle_audio_player_play(self, path: str):
        if pygame.mixer.get_busy():
            pygame.mixer.stop()
            self.sfx_browser.unset_currently_playing_icon()
            self.music_browser.unset_currently_playing_icon()
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()

    def _handle_audio_player_stop(self):
        pygame.mixer.music.stop()

    def _check_pygame_events(self):
        for event in pygame.event.get():
            if event.type == AUDIO_END_EVENT:
                self.sfx_browser.unset_currently_playing_icon()
                self.music_browser.unset_currently_playing_icon()

    def deinit(self):
        self._pymixer_check_timer.stop()
        pygame.quit()

    def _handle_top_level(self, top_level: bool):
        self.setTitleBarWidget(None if top_level else self.title_bar_widget)
        if top_level:
            self.widget().layout().setContentsMargins(0, 0, 0, 0)
        else:
            self.widget().layout().setContentsMargins(12, 0, 12, 12)
