FROM mcr.microsoft.com/windows/servercore:ltsc2019
# ENV chocolateyVersion=1.4.0

# Chocolateyのインストール
RUN powershell -Command "Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))"

# Pythonのインストール
RUN powershell -Command "choco install -y python --version 3.12.7"

# ホストマシンのコードをコンテナにコピー
COPY ./src /app/src
WORKDIR /app/src

# requirements.txtをコンテナにコピー
COPY requirements.txt .

# 依存関係をインストール
RUN pip install --no-cache-dir -r requirements.txt

# 依存関係のインストール
RUN pip install --no-cache-dir pyinstaller
