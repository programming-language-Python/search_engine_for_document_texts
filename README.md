# Запуск через Docker
1) Клонировать репозиторий git
```cmd
git clone https://github.com/programming-language-Python/search_engine_for_document_texts.git
```
2) Перейти в проект
```cmd
cd search_engine_for_document_texts
```
3) Выполнить команду Docker
```cmd
docker-compose up -d --build
```
4) Перейти в браузер по адресу http://localhost:8000/docs#

# Запуск тестов
После запуска через Docker вводим команду
```cmd
docker compose --profile test up tests
```
