#!/bin/bash
# 在 Mac 上一键打包出原生 HelloKittyPet.app 的脚本
cd "$(dirname "$0")"

echo "正在准备在 Mac 上打包 Hello Kitty 桌宠..."
pip3 install pyinstaller PyQt5 Pillow

pyinstaller --noconfirm --onedir --windowed \
  --name "HelloKittyPet" \
  --add-data "assets:assets" \
  main.py

echo "打包完成！生成的原生 Mac 应用在 dist/HelloKittyPet.app"
open dist/
