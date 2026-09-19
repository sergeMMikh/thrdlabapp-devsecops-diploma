# Локальный запуск (Windows)

Нужны Python 3.12, Docker Desktop с запущенным Linux engine и Chrome
для браузерного теста Selenium.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
```

В Git Bash окружение активируется командой `source .venv/Scripts/activate`.
Без активации можно использовать `.venv/Scripts/python.exe` вместо `python`.

`requirements.txt` содержит зависимости приложения и сервера Gunicorn.
`requirements-test.txt` добавляет pytest и Selenium для test-job в CI.
`requirements-dev.txt` добавляет к ним линтеры и `requests` для `client.py`.
Транзитивные зависимости устанавливаются автоматически; `sqlparse` явно
закреплён на обновлённой версии. Production Docker image устанавливает
только `requirements.txt`.

Создайте `.env` на основе `.env.example`, если файла ещё нет. Для запуска
Django на хосте задайте:

```dotenv
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost,testserver
CSRF_TRUSTED_ORIGINS=http://127.0.0.1:8000,http://localhost:8000
PGHOST=127.0.0.1
PGPORT=55432
```

Также установите собственные случайные `SECRET_KEY` и `PGPASSWORD`.
Файл `.env` и окружение `.venv` исключены из Git.

```powershell
docker compose -f compose.yaml -f compose.local.yaml up -d --wait db
python manage.py migrate --noinput
python manage.py runserver 127.0.0.1:8000
```

Приложение: <http://127.0.0.1:8000/>. PostgreSQL хранит данные в Docker volume
и доступен только локально на порту 55432. При необходимости создайте
администратора командой `python manage.py createsuperuser`.

Проверки:

```powershell
python -m pip check
python manage.py check
python -m pytest -q
python manage.py test
```

Тесты используют отдельную SQLite-базу в памяти; локальная PostgreSQL-база
не очищается. Selenium Manager может скачать ChromeDriver при первом запуске.

Для остановки сервера нажмите Ctrl+C. Остановка базы без удаления данных:

```powershell
docker compose -f compose.yaml -f compose.local.yaml stop db
```
