import os
import sqlite3
import subprocess
import threading
import requests
import pygame
from kivy.lang import Builder
from kivy.properties import StringProperty, BooleanProperty, NumericProperty, ListProperty
from kivy.clock import Clock
from kivymd.app import MDApp
from kivymd.uix.list import TwoLineAvatarListItem, ImageLeftWidget
from kivy.uix.modalview import ModalView  # Используем стандартный ModalView
DEFAULT_ICON = "music.png"  # Путь к картинке-заглушке

KV = '''
<FullPlayer>:
    canvas.before:
        Color:
            rgba: 0.07, 0.07, 0.07, 1
        Rectangle:
            pos: self.pos
            size: self.size
    MDBoxLayout:
        orientation: 'vertical'
        padding: "20dp"
        spacing: "15dp"

        MDIconButton:
            icon: "chevron-down"
            on_release: root.dismiss()
            pos_hint: {"center_x": .5}
            theme_text_color: "Custom"
            text_color: 1, 1, 1, 0.5

        MDAnchorLayout:
            size_hint_y: None
            height: "320dp"
            MDCard:
                size_hint: None, None
                size: "280dp", "280dp"
                radius: [25,]
                elevation: 4
                # --- ИСПРАВЛЕНИЕ АНИМАЦИИ ---
                scale_x: 1
                scale_y: 1
                canvas.before:
                    PushMatrix
                    Scale:
                        x: self.scale_x
                        y: self.scale_y
                        origin: self.center
                canvas.after:
                    PopMatrix
                # ----------------------------
                on_touch_down: if self.collide_point(*args[1].pos): app.animate_card(self)
                FitImage:
                    source: app.current_thumb
                    radius: [25,]

        MDBoxLayout:
            orientation: 'vertical'
            adaptive_height: True
            spacing: "12dp"  # Увеличено расстояние, чтобы текст не сливался
            padding: [0, "10dp", 0, "10dp"] # Добавлен отступ сверху и снизу
            MDLabel:
                text: app.current_title
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                font_style: "H6"
                halign: "center"
                bold: True  # Сделаем название жирным для контраста
            MDLabel:
                text: app.current_artist
                theme_text_color: "Custom"
                text_color: 1, 0.8, 0, 1
                halign: "center"
                font_style: "Subtitle1"

        MDBoxLayout:
            orientation: 'vertical'
            adaptive_height: True
            padding: ["20dp", "10dp"]
            MDSlider:
                id: progress_slider
                min: 0
                max: app.track_length if app.track_length > 0 else 1
                value: app.track_pos
                color: 1, 0.8, 0, 1
                hint: False
                on_touch_up: if self.collide_point(*args[1].pos): app.seek_track(self.value)
            MDBoxLayout:
                adaptive_height: True
                MDLabel:
                    text: app.time_elapsed
                    font_style: "Caption"
                    theme_text_color: "Hint"
                MDLabel:
                    text: app.time_total
                    halign: "right"
                    font_style: "Caption"
                    theme_text_color: "Hint"

        MDBoxLayout:
            adaptive_height: True
            padding: [0, "10dp", 0, "40dp"]
            MDAnchorLayout:
                MDBoxLayout:
                    adaptive_width: True
                    spacing: "15dp"

                    MDIconButton:
                        icon: "heart" if app.is_fav else "heart-outline"
                        icon_size: "30sp"
                        theme_text_color: "Custom"
                        text_color: (1, 0.2, 0.2, 1) if app.is_fav else (1, 1, 1, 1)
                        on_release: app.save_current_to_fav()
                        pos_hint: {"center_y": .5}

                    MDIconButton:
                        icon: "skip-previous"
                        icon_size: "35sp"
                        on_release: app.play_prev()
                        pos_hint: {"center_y": .5}

                    MDIconButton:
                        icon: "pause-circle" if app.is_playing else "play-circle"
                        icon_size: "75sp"
                        theme_text_color: "Custom"
                        text_color: 1, 0.8, 0, 1
                        on_release: app.toggle_playback()
                        pos_hint: {"center_y": .5}

                    MDIconButton:
                        icon: "skip-next"
                        icon_size: "35sp"
                        on_release: app.play_next()
                        pos_hint: {"center_y": .5}

                    MDIconButton:
                        icon: "repeat"
                        icon_size: "30sp"
                        theme_text_color: "Custom"
                        text_color: (1, 0.8, 0, 1) if app.is_repeating else (1, 1, 1, 0.5)
                        on_release: app.toggle_repeat()
                        pos_hint: {"center_y": .5}

MDFloatLayout:
    md_bg_color: 0.05, 0.05, 0.05, 1

    MDBottomNavigation:
        id: tab_manager
        panel_color: 0.1, 0.1, 0.1, 1
        MDBottomNavigationItem:
            name: 'search'
            text: 'Поиск'
            icon: 'magnify'
            MDBoxLayout:
                orientation: 'vertical'
                padding: ["10dp", "10dp", "10dp", "160dp"]
                MDTextField:
                    id: search_field
                    hint_text: "Найти музыку..."
                    mode: "round"
                    on_text_validate: app.search_tracks(self.text)
                ScrollView:
                    MDList:
                        id: search_results
        MDBottomNavigationItem:
            name: 'fav'
            text: 'Любимые'
            icon: 'heart'
            on_tab_press: app.load_favorites()
            ScrollView:
                MDList:
                    id: favorites_list
                    padding: [0, 0, 0, "160dp"]

    MDCard:
        id: mini_player
        size_hint: (0.96, None)
        height: "85dp"
        pos_hint: {"center_x": .5, "y": 0.11}
        md_bg_color: 0.12, 0.12, 0.12, 1
        radius: [18,]
        elevation: 4
        on_release: app.open_full_player()

        MDBoxLayout:
            orientation: 'horizontal'
            padding: ["10dp", "0dp", "10dp", "0dp"]
            spacing: "12dp"

            FitImage:
                source: app.current_thumb
                size_hint: None, None
                size: "60dp", "60dp"
                radius: [12,]
                pos_hint: {"center_y": .5}

            MDBoxLayout:
                orientation: 'vertical'
                pos_hint: {"center_y": .5}
                MDLabel:
                    text: app.current_title
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    font_style: "Subtitle1"
                    shorten: True
                MDLabel:
                    text: app.current_artist
                    theme_text_color: "Hint"
                    font_style: "Caption"

            MDBoxLayout:
                adaptive_width: True
                spacing: "8dp"
                pos_hint: {"center_y": .5}
                MDIconButton:
                    icon: "heart" if app.is_fav else "heart-outline"
                    theme_text_color: "Custom"
                    text_color: (1, 0, 0, 1) if app.is_fav else (1, 1, 1, 0.6)
                    on_release: app.save_current_to_fav()
                MDIconButton:
                    icon: "pause" if app.is_playing else "play"
                    theme_text_color: "Custom"
                    text_color: 1, 0.8, 0, 1
                    on_release: app.toggle_playback()
'''
class FullPlayer(ModalView):
    pass


class MusicApp(MDApp):
    # --- Свойства данных ---
    current_title = StringProperty("Выберите трек")
    current_artist = StringProperty("SoundCloud")
    current_thumb = StringProperty(DEFAULT_ICON)
    time_elapsed = StringProperty("00:00")
    time_total = StringProperty("00:00")

    # --- Состояния ---
    is_playing = BooleanProperty(False)
    is_fav = BooleanProperty(False)
    is_repeating = BooleanProperty(False)
    music_loaded = BooleanProperty(False)

    # --- Технические свойства ---
    track_pos = NumericProperty(0)
    track_length = NumericProperty(1)
    current_playlist = ListProperty([])
    current_index = NumericProperty(-1)
    seek_offset = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pygame.mixer.init()

    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Orange"
        self.init_db()
        Clock.schedule_interval(self.update_ui, 0.5)
        return Builder.load_string(KV)

    # --- Логика воспроизведения ---

    def update_ui(self, dt):
        if self.music_loaded and self.is_playing:
            if pygame.mixer.music.get_busy():
                pos = pygame.mixer.music.get_pos() / 1000.0
                if pos >= 0:
                    self.track_pos = self.seek_offset + pos
                    self.time_elapsed = self.format_time(self.track_pos)

            if self.track_pos >= self.track_length - 0.5 and self.track_length > 1:
                if self.is_repeating:
                    self.seek_track(0)
                else:
                    self.play_next()

    def seek_track(self, value):
        if self.music_loaded:
            try:
                pygame.mixer.music.play(start=float(value))
                self.seek_offset = float(value)
                self.track_pos = float(value)
            except Exception as e:
                print(f"Ошибка перемотки: {e}")

    def toggle_playback(self):
        if not self.music_loaded: return
        if self.is_playing:
            pygame.mixer.music.pause()
        else:
            pygame.mixer.music.unpause()
        self.is_playing = not self.is_playing

    def toggle_repeat(self):
        self.is_repeating = not self.is_repeating

    def play_next(self):
        if self.current_index < len(self.current_playlist) - 1:
            self.load_and_play(self.current_index + 1)

    def play_prev(self):
        if self.current_index > 0:
            self.load_and_play(self.current_index - 1)

    def load_and_play(self, index):
        if 0 <= index < len(self.current_playlist):
            self.current_index = index
            entry = self.current_playlist[index]
            self.track_pos = 0
            self.seek_offset = 0
            self.current_title, self.current_artist = entry['title'], entry['artist']
            self.fetch_web_thumb(entry['title'], entry['artist'], entry['id'],
                                 entry['thumbnail'], lambda p: setattr(self, 'current_thumb', p))
            self.check_fav_status()
            f_path = os.path.abspath(os.path.join('downloads', f"{entry['id']}.mp3"))
            if os.path.exists(f_path):
                self.play_music(f_path)
            else:
                self.is_playing = False
                self.current_title = "Загрузка..."
                threading.Thread(target=self._download_task, args=(entry, f_path), daemon=True).start()

    def play_music(self, path):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            self.music_loaded = True
            self.is_playing = True
            sound = pygame.mixer.Sound(path)
            self.track_length = sound.get_length()
            self.time_total = self.format_time(self.track_length)
        except Exception as e:
            print(f"Ошибка воспроизведения: {e}")

    def init_db(self):
        self.conn = sqlite3.connect('music.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            "CREATE TABLE IF NOT EXISTS favorites (id TEXT PRIMARY KEY, title TEXT, artist TEXT, path TEXT, thumb TEXT)")
        self.conn.commit()

    def fetch_web_thumb(self, title, artist, track_id, fallback_url, callback):
        def task():
            thumb_path = os.path.abspath(os.path.join('cache', f"{track_id}.jpg"))
            if os.path.exists(thumb_path) and os.path.getsize(thumb_path) > 0:
                Clock.schedule_once(lambda dt: callback(thumb_path), 0)
                return
            img_url = fallback_url if fallback_url and fallback_url != "NA" else DEFAULT_ICON
            if img_url.startswith('http'):
                try:
                    res = requests.get(img_url, timeout=5, stream=True)
                    if res.status_code == 200:
                        with open(thumb_path, 'wb') as f:
                            for chunk in res.iter_content(8192): f.write(chunk)
                        Clock.schedule_once(lambda dt: callback(thumb_path), 0)
                        return
                except:
                    pass
            Clock.schedule_once(lambda dt: callback(DEFAULT_ICON), 0)
        threading.Thread(target=task, daemon=True).start()

    def search_tracks(self, query):
        if not query: return
        self.root.ids.search_results.clear_widgets()
        threading.Thread(target=self._search_logic, args=(query,), daemon=True).start()

    def _search_logic(self, query):
        cmd = ["yt-dlp", "--no-check-certificate", "--quiet", "--flat-playlist", "--print",
               "%(title)s|SEP|%(id)s|SEP|%(uploader)s|SEP|%(thumbnail)s|SEP|%(webpage_url)s", f"scsearch20:{query}"]
        try:
            si = None
            if os.name == 'nt':
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            output = subprocess.check_output(cmd, encoding='utf-8', startupinfo=si).strip().split('\n')
            new_list = []
            for line in output:
                if "|SEP|" in line:
                    parts = line.split('|SEP|')
                    entry = {'title': parts[0], 'id': parts[1], 'artist': parts[2], 'thumbnail': parts[3],
                             'url': parts[4]}
                    new_list.append(entry)
                    idx = len(new_list) - 1
                    Clock.schedule_once(lambda x, e=entry, i=idx: self.add_track_widget(e, i, "search"))
            self.current_playlist = new_list
        except Exception as e:
            print(e)

    def add_track_widget(self, entry, index, mode):
        item = TwoLineAvatarListItem(text=entry['title'][:50], secondary_text=entry['artist'],
                                     on_release=lambda x: self.load_and_play(index))
        img_w = ImageLeftWidget(source=DEFAULT_ICON)
        item.add_widget(img_w)
        self.fetch_web_thumb(entry['title'], entry['artist'], entry['id'], entry['thumbnail'],
                             lambda p: setattr(img_w, 'source', p))
        if mode == "search":
            self.root.ids.search_results.add_widget(item)
        else:
            self.root.ids.favorites_list.add_widget(item)

    def _download_task(self, entry, f_path):
        cmd = ["yt-dlp", "-f", "ba", "-x", "--audio-format", "mp3", "--quiet", "-o", f_path.replace('.mp3', ''),
               entry['url']]
        try:
            si = None
            if os.name == 'nt':
                si = subprocess.STARTUPINFO()
                si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.run(cmd, check=True, startupinfo=si)
            Clock.schedule_once(lambda dt: self.play_music(f_path), 0.1)
        except:
            pass

    def open_full_player(self):
        FullPlayer().open()

    def animate_card(self, instance):
        from kivy.animation import Animation
        anim = Animation(scale_x=0.9, scale_y=0.9, duration=0.1) + \
               Animation(scale_x=1.0, scale_y=1.0, duration=0.15)
        anim.start(instance)

    def format_time(self, seconds):
        m, s = divmod(max(0, int(seconds)), 60)
        return f"{m:02d}:{s:02d}"

    def check_fav_status(self):
        if 0 <= self.current_index < len(self.current_playlist):
            self.cursor.execute("SELECT 1 FROM favorites WHERE id=?",
                                (self.current_playlist[self.current_index]['id'],))
            self.is_fav = bool(self.cursor.fetchone())

    def save_current_to_fav(self):
        if self.current_index == -1: return
        t = self.current_playlist[self.current_index]
        p = os.path.abspath(os.path.join('downloads', f"{t['id']}.mp3"))
        if self.is_fav:
            self.cursor.execute("DELETE FROM favorites WHERE id=?", (t['id'],))
        else:
            self.cursor.execute("INSERT OR REPLACE INTO favorites VALUES (?, ?, ?, ?, ?)",
                                (t['id'], t['title'], t['artist'], p, t['thumbnail']))
        self.conn.commit()
        self.check_fav_status()

    def load_favorites(self):
        self.root.ids.favorites_list.clear_widgets()
        self.cursor.execute("SELECT id, title, artist, path, thumb FROM favorites")
        favs = []
        for i, r in enumerate(self.cursor.fetchall()):
            e = {'id': r[0], 'title': r[1], 'artist': r[2], 'thumbnail': r[4], 'url': ""}
            favs.append(e)
            self.add_track_widget(e, i, "fav")
        self.current_playlist = favs

# --- ТОЧКА ВХОДА ВНЕ КЛАССА ---
if __name__ == '__main__':
    for f in ['cache', 'downloads']:
        if not os.path.exists(f):
            os.makedirs(f)
    MusicApp().run()
