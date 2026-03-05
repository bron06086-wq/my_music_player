[app]
title = Music Player
package.name = mymusicplayer
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,mp3

version = 0.1

#requirements - зафиксировал всё для стабильности
requirements = python3,kivy==2.2.1,android,jnius

orientation = portrait
fullscreen = 0

# Разрешения для музыки (Android 11+)
android.permissions = READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE, INTERNET, MANAGE_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True

[buildozer]
log_level = 2
warn_on_root = 1
