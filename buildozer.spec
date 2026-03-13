[app]
title = Prisma Music
package.name = prismamusic
package.domain = org.bron
source.dir = .
source.include_exts = py,png,jpg,kv,db
version = 0.1

# Список зависимостей для Android
requirements = python3,kivy==2.3.1,kivymd==1.2.0,pygame,requests,yt-dlp,certifi

orientation = portrait
fullscreen = 0
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

# Разрешения на интернет и запись файлов
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
