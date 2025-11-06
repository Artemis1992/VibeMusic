# Dockerfile
# Используем Python 3.12 slim
FROM python:3.12-slim

# Рабочая директория в контейнере
WORKDIR /app

# Копируем файл с зависимостями и устанавливаем их
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Копируем весь проект
COPY coolsite/ .

# Собираем статику
RUN python manage.py collectstatic --noinput

# Открываем порт для Gunicorn
EXPOSE 8000

# Запуск Gunicorn
CMD ["gunicorn", "coolsite.wsgi:application", "--bind", "0.0.0.0:8000"]
