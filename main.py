import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView
from kivy.core.audio import SoundLoader
from kivy.utils import platform

# Импортируем специфичные для Android модули
if platform == 'android':
    from android.permissions import request_permissions, Permission

class MusicPlayer(App):
    def build(self):
        self.title = "Ultimate Music Player"
        self.sound = None
        
        # Запрашиваем права при запуске на Android
        if platform == 'android':
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])

        # Создаем интерфейс
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.label = Label(text="Выберите песню для воспроизведения", size_hint_y=0.1)
        layout.add_widget(self.label)

        # Выбор файлов
        self.file_chooser = FileChooserIconView(size_hint_y=0.7)
        # На Android обычно музыка лежит здесь: /storage/emulated/0/Music
        if platform == 'android':
            self.file_chooser.path = "/storage/emulated/0/Music"
        layout.add_widget(self.file_chooser)

        # Кнопки управления
        btn_layout = BoxLayout(size_hint_y=0.2, spacing=10)
        
        play_btn = Button(text="ИГРАТЬ", on_release=self.play_music)
        stop_btn = Button(text="СТОП", on_release=self.stop_music)
        
        btn_layout.add_widget(play_btn)
        btn_layout.add_widget(stop_btn)
        layout.add_widget(btn_layout)

        return layout

    def play_music(self, instance):
        if self.file_chooser.selection:
            # Останавливаем текущий трек, если он есть
            if self.sound:
                self.sound.stop()
            
            file_path = self.file_chooser.selection[0]
            self.sound = SoundLoader.load(file_path)
            
            if self.sound:
                self.sound.play()
                self.label.text = f"Играет: {os.path.basename(file_path)}"
            else:
                self.label.text = "Ошибка: Формат файла не поддерживается"

    def stop_music(self, instance):
        if self.sound:
            self.sound.stop()
            self.label.text = "Воспроизведение остановлено"

if __name__ == "__main__":
    MusicPlayer().run()
        
