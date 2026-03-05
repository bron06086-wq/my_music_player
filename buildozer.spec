[app]

# Название твоего приложения
title = My Music Player
# Имя пакета (без пробелов)
package.name = mymusicplayer
# Домен (любой)
package.domain = org.test

# Где лежит код (текущая папка)
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3,wav

# Версия приложения
version = 0.1

# ТРЕБОВАНИЯ (requirements) - Это критически важно!
# Мы зафиксировали версию kivy, добавили android и jnius для прав доступа
requirements = python3,kivy==2.2.1,android,jnius,pillow

# Ориентация экрана
orientation = portrait

# Включать ли полноэкранный режим
fullscreen = 0

# ПРАВА ДОСТУПА (Permissions) - Без них плеер не увидит музыку!
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, INTERNET, MANAGE_EXTERNAL_STORAGE

# Настройки SDK / NDK (под GitHub Actions)
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a

# Использовать ли автоматическую установку прав при запуске
android.skip_update_buildozer = False
android.accept_sdk_license = True

# Прочее
# (Включаем поддержку SQLite на случай, если будешь делать плейлисты)
android.copy_libs = 1

[buildozer]
# Уровень логирования (2 - самый подробный)
log_level = 2
# Папка для сборки
build_dir = ./.buildozer
# Папка для готовых APK
bin_dir = ./bin

