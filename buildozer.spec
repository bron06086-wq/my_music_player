[app]
title = My Music Player
package.name = mymusicplayer
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,kivy==2.2.1,kivymd,pillow
orientation = portrait
fullscreen = 0
android.permissions = INTERNET, READ_EXTERNAL_STORAGE, WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
# Это критически важно для работы на новых серверах GitHub:
p4a.branch = master
