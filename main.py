import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.filechooser import FileChooserIconView
from kivy.core.audio import SoundLoader
from kivy.utils import platform

# Специальный импорт для Android
if platform == 'android':
    from android.permissions import request_permissions, Permission

class MusicPlayerApp(App):
    def build(self):
        self.sound = None
        
        # Запрашиваем права при запуске
        if platform == 'android':
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE, 
                Permission.WRITE_EXTERNAL_STORAGE
            ])

        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        self.status_label = Label(
            text="Выберите аудиофайл", 
            size_hint_y=0.1,
            color=(0, 1, 0, 1)
        )
        layout.add_widget(self.status_label)

        # Путь для Android и ПК
        if platform == 'android':
            initial_path = "/storage/emulated/0/Music"
        else:
            initial_path = os.path.expanduser("~")
        
        # Проверяем существование пути, чтобы не было ошибки
        if not os.path.exists(initial_path):
            initial_path = "/"

        self.file_manager = FileChooserIconView(
            path=initial_path,
            size_hint_y=0.7,
            filters=['*.mp3', '*.wav', '*.ogg']
        )
        layout.add_widget(self.file_manager)

        controls = BoxLayout(size_hint_y=0.2, spacing=15)
        
        play_btn = Button(
            text="ИГРАТЬ", 
            background_color=(0.2, 0.8, 0.2, 1),
            on_release=self.play_audio
        )
        stop_btn = Button(
            text="СТОП", 
            background_color=(0.8, 0.2, 0.2, 1),
            on_release=self.stop_audio
        )
        
        controls.add_widget(play_btn)
        controls.add_widget(stop_btn)
        layout.add_widget(controls)

        return layout

    def play_audio(self, instance):
        if self.file_manager.selection:
            file_path = self.file_manager.selection[0]
            
            # Остановка предыдущего трека
            if self.sound:
                self.sound.stop()
                self.sound.unload()

            try:
                self.sound = SoundLoader.load(file_path)
                if self.sound:
                    self.sound.play()
                    self.status_label.text = f"Играет: {os.path.basename(file_path)}"
                else:
                    self.status_label.text = "Ошибка: Формат не поддерживается"
            except Exception as e:
                self.status_label.text = f"Ошибка: {str(e)}"
        else:
            self.status_label.text = "Сначала выберите файл!"

    def stop_audio(self, instance):
        if self.sound:
            self.sound.stop()
            self.status_label.text = "Остановлено"

    def on_stop(self):
        if self.sound:
            self.sound.stop()

if __name__ == '__main__':
    MusicPlayerApp().run()
    
