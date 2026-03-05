import os, threading, requests, yt_dlp
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.utils import platform
from kivymd.app import MDApp
from kivymd.uix.list import OneLineListItem

KV = '''
MDScreen:
    md_bg_color: 0, 0, 0, 1
    MDBoxLayout:
        orientation: 'vertical'
        padding: "10dp"
        MDLabel:
            text: "MUSIC PLAYER"
            halign: "center"
            font_style: "H4"
            theme_text_color: "Custom"
            text_color: 1, 0.4, 0, 1
            size_hint_y: None
            height: "60dp"
        MDTextField:
            id: search_field
            hint_text: "Поиск в SoundCloud..."
            mode: "fill"
            fill_color_normal: 0.1, 0.1, 0.1, 1
        MDRaisedButton:
            text: "НАЙТИ ТРЕКИ"
            md_bg_color: 1, 0.4, 0, 1
            pos_hint: {"center_x": .5}
            on_release: app.start_search()
        MDScrollView:
            MDList:
                id: results_list
        MDCard:
            size_hint_y: None
            height: "100dp"
            md_bg_color: 0.1, 0.1, 0.1, 1
            radius: [20, 20, 0, 0]
            MDBoxLayout:
                orientation: 'vertical'
                padding: "10dp"
                MDLabel:
                    id: track_label
                    text: "Плеер готов"
                    halign: "center"
                    theme_text_color: "Custom"
                    text_color: "white"
                MDProgressBar:
                    id: progress
                    value: 0
                    color: 1, 0.4, 0, 1
'''

class SCPlayer(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        self.track_path = os.path.join(self.user_data_dir, "track.mp3")
        self.player = None
        return Builder.load_string(KV)

    def start_search(self):
        q = self.root.ids.search_field.text
        if q:
            self.root.ids.results_list.clear_widgets()
            threading.Thread(target=self.run_search, args=(q,), daemon=True).start()

    def run_search(self, q):
        opts = {'format': 'bestaudio/best', 'default_search': 'scsearch10', 'quiet': True}
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(q, download=False)
                for e in info.get('entries', []):
                    Clock.schedule_once(lambda dt, entry=e: self.add_item(entry))
        except: pass

    def add_item(self, e):
        self.root.ids.results_list.add_widget(OneLineListItem(
            text=e.get('title', 'Unknown'),
            on_release=lambda x, u=e.get('url'), t=e.get('title'): self.play_track(u, t)
        ))

    def play_track(self, url, title):
        self.root.ids.track_label.text = "Загрузка..."
        threading.Thread(target=self.download, args=(url,), daemon=True).start()

    def download(self, url):
        try:
            r = requests.get(url, stream=True, headers={'User-Agent': 'Mozilla/5.0'})
            with open(self.track_path, 'wb') as f:
                for chunk in r.iter_content(64*1024): f.write(chunk)
            Clock.schedule_once(self.start_audio)
        except: Clock.schedule_once(lambda dt: self.set_status("Ошибка загрузки"))

    def start_audio(self, dt):
        if platform == 'android':
            from jnius import autoclass
            MP = autoclass('android.media.MediaPlayer')
            if not self.player: self.player = MP()
            else: self.player.reset()
            self.player.setDataSource(self.track_path)
            self.player.prepare()
            self.player.start()
        else:
            from kivy.core.audio import SoundLoader
            self.player = SoundLoader.load(self.track_path)
            if self.player: self.player.play()
        self.root.ids.track_label.text = "Играет ▶️"

if __name__ == "__main__":
    SCPlayer().run()
  
