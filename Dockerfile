# Указываем образ с нужной версией Python
FROM python:3.12

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем все файлы проекта в контейнер
COPY . /app

# Устанавливаем зависимости
RUN pip install -r requirements.txt

# Запускаем приложение
CMD ["python", "main.py"]
