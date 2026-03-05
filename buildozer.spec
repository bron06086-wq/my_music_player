name: Build Android APK

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-22.04 # Используем 22.04, так как на 24.04 Buildozer часто падает

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10' # Самая стабильная версия для сборки Kivy

      - name: Install System Dependencies
        run: |
          sudo apt update
          sudo apt install -y git zip unzip autoconf libtool pkg-config zlib1g-dev \
          libncurses5-dev libncursesw5-dev libtinfo5 cmake libffi-dev libssl-dev \
          python3-pip python3-setuptools build-essential libsqlite3-dev sqlite3 \
          bzip2 libbz2-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
          libreadline-dev uuid-dev libgstreamer1.0-dev gstreamer1.0-plugins-base \
          gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-plugins-ugly \
          gstreamer1.0-libav libmtp-dev

      - name: Install Buildozer & Cython
        run: |
          pip install --upgrade pip
          pip install --user --upgrade buildozer Cython==0.29.33

      - name: Build APK with Buildozer
        run: |
          # Команда 'yes |' автоматически принимает все лицензии Android SDK
          yes | /home/runner/.local/bin/buildozer android debug
        env:
          # Принудительно используем Java 17, которая нужна для актуального SDK
          JAVA_HOME: ${{ env.JAVA_HOME_17_X64 }}

      - name: Upload APK Artifact
        uses: actions/upload-artifact@v4
        with:
          name: MusicPlayer-Debug-APK
          path: bin/*.apk
          
