# Используем официальный Python образ
FROM python:3.11-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Экспонируем порт, на котором работает Flask
EXPOSE 5000

# Устанавливаем переменные окружения для Flask
ENV FLASK_APP=run.py
ENV FLASK_ENV=development

# Запускаем приложение
CMD ["python", "run.py"]
