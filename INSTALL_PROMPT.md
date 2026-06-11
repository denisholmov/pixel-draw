# Промпт для установки Pixel Draw (скопируй целиком в Cursor / Claude Code)

```
Установи и запусти Pixel Draw на этом компьютере.

Репозиторий: https://github.com/denisholmov/pixel-draw

Сделай всё сам, без длинных пояснений. В конце приложение должно открыться с веб-камерой.

## Шаг 1 — определи ОС
Linux / macOS / Windows.

## Шаг 2 — установи то, чего нет

### Linux (Ubuntu/Debian)
Проверь: python3 --version (нужен 3.10+), git --version, wget --version
Если чего-то нет:
  sudo apt update
  sudo apt install -y python3 python3-venv python3-pip git wget

### Linux (Fedora)
  sudo dnf install -y python3 python3-pip git wget

### macOS
Проверь python3 --version (нужен 3.10+)
Если нет или старый — установи через Homebrew:
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  brew install python@3.12 git
Если brew нет и python3 < 3.10 — скачай с https://www.python.org/downloads/

### Windows (PowerShell от администратора)
  winget install Python.Python.3.12
  winget install Git.Git
Перезапусти терминал после установки.

## Шаг 3 — скачай проект
В домашней папке или на рабочем столе:

Linux/macOS:
  cd ~
  git clone https://github.com/denisholmov/pixel-draw.git
  cd pixel-draw

Windows:
  cd %USERPROFILE%
  git clone https://github.com/denisholmov/pixel-draw.git
  cd pixel-draw

## Шаг 4 — запусти
Linux/macOS:
  chmod +x setup.sh
  ./setup.sh

Windows:
  setup.bat

setup сам: создаст .venv, pip install, скачает модель hand_landmarker.task (~8 MB), запустит hand_paint.py.

## Шаг 5 — если ошибка
- «python3 not found» → установи Python 3.10+ (шаг 2)
- «git not found» → установи git (шаг 2)
- «Не удалось открыть веб-камеру» → проверь камеру и разрешения
- «No module named cv2» → активируй .venv и: pip install -r requirements.txt
- Linux: если нет wget → sudo apt install wget

Исправь и снова запусти setup.sh или setup.bat.

## Жесты (для справки)
☝️ указательный вверх, остальные сжаты — рисует
✊ кулак — стирает
🖐 ладонь раскрыта — пауза
Q — выход, C — очистить
```
