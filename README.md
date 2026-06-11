# Pixel Draw

Рисуй на экране жестами руки через веб-камеру.

☝️ указательный вверх — рисуешь · ✊ кулак — стираешь · 🖐 ладонь открыта — пауза

## Быстрый старт

**Нужно:** Python 3.10+, веб-камера, интернет на первый запуск.

```bash
git clone https://github.com/denisholmov/pixel-draw.git
cd pixel-draw
chmod +x setup.sh && ./setup.sh
```

Windows:

```bash
git clone https://github.com/denisholmov/pixel-draw.git
cd pixel-draw
setup.bat
```

Скрипт сам создаст виртуальное окружение, установит зависимости, скачает модель (~8 MB) и запустит приложение.

## Управление

| Клавиша / действие | Что делает |
|--------------------|------------|
| ☝️ Указательный вверх, остальные сжаты | Рисование |
| ✊ Кулак | Стирает |
| 🖐 Все 5 пальцев раскрыты | Пауза |
| **Q** | Выход |
| **C** | Очистить холст |
| Клик по цветам слева | Выбор цвета |
| Кнопка **Clear** | Очистить холст |

## Собрать через Cursor / Claude Code

Открой **[PROMPT.md](PROMPT.md)** на GitHub → Raw → скопируй всё → вставь в Agent-чат.

Прямая ссылка: https://raw.githubusercontent.com/denisholmov/pixel-draw/main/PROMPT.md

## Структура проекта

```
pixel-draw/
├── hand_paint.py
├── setup.sh
├── setup.bat
├── requirements.txt
├── PROMPT.md
└── README.md
```

## Текст для Instagram

```
Рисуй рукой через веб-камеру ☝️✊🖐

git clone https://github.com/denisholmov/pixel-draw.git
cd pixel-draw && chmod +x setup.sh && ./setup.sh

Нужен Python 3.10+ и камера
```
