name: Build Music Player APK

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-22.04 # 22.04 намного стабильнее для сборки Kivy приложений

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10' # Оптимальная версия Python для Buildozer

      - name: Install System Dependencies
        run: |
          sudo apt update
          sudo apt install -y git zip unzip autoconf libtool pkg-config zlib1g-dev \
          libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev \
          build-essential libsqlite3-dev sqlite3 bzip2 libbz2-dev libgdbm-dev \
          libgdbm-compat-dev liblzma-dev libreadline-dev uuid-dev \
          libgstreamer1.0-dev gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
          gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly libmtp-dev

      - name: Install Buildozer and Cython
        run: |
          pip install --upgrade pip
          pip install --user --upgrade buildozer Cython==0.29.33

      - name: Build APK with Buildozer
        run: |
          # Используем путь к локально установленному buildozer
          yes | /home/runner/.local/bin/buildozer android debug
        env:
          # Указываем путь к Java 17, которая установлена на GitHub Runners по умолчанию
          JAVA_HOME: ${{ env.JAVA_HOME_17_X64 }}

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: music-player-app
          path: bin/*.apk
          
