[app]
title = My Music Player
package.name = mymusicplayer
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1

# ВАЖНО: Убрал Pillow, KivyMD сам возьмет что нужно стабильной версии
requirements = python3,kivy==2.2.1,kivymd==1.1.1

orientation = portrait
fullscreen = 0

# Разрешения для работы с музыкой
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, MANAGE_EXTERNAL_STORAGE

# Настройки для GitHub Actions (Ubuntu 24.04)
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True

# Фикс для ошибки "patch unexpectedly ends"
p4a.branch = master
p4a.bootstrap = sdl2
