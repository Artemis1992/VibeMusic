from pathlib import Path                    # объектно-ориентированная работа с путями (files/dirs)
import os                                   # утилиты ОС: переменные окружения, пути, cwd, список файлов
from datetime import timedelta              # интервалы времени (часы/дни), для таймаутов/TTL/расписаний


BASE_DIR = Path(__file__).resolve().parent.parent.parent    # корень проекта (поднимаемся на 3 уровня вверх)