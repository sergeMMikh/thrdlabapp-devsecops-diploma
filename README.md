# THRDLabApp DevSecOps Diploma

Дипломный репозиторий для построения безопасного CI/CD-пайплайна вокруг реального Django-приложения **THRDLabApp**.

Исходный рабочий проект: [sergeMMikh/thrdlabapp](https://github.com/sergeMMikh/thrdlabapp).

Этот репозиторий создан отдельно, чтобы разработка и тестирование DevSecOps-пайплайна, контейнеризации, SAST/DAST и security gates не затрагивали рабочую версию приложения.

## Исходное состояние проекта

На момент начала дипломной работы приложение уже содержит:

- Django web application;
- PostgreSQL как основную БД;
- SQLite in-memory для автоматизированных тестов;
- `pytest` и Django tests;
- `flake8`;
- GitHub Actions для lint/test;
- Gunicorn и WhiteNoise в зависимостях;
- переменные окружения для Django, PostgreSQL и SMTP.

Целевой дипломный pipeline будет развиваться по этапам:

1. CI/CD и воспроизводимое развёртывание;
2. SAST;
3. DAST;
4. secret/dependency/config/container security checks;
5. Security Gateway с блокировкой небезопасного релиза и публикацией результатов.

## Docker Compose deployment

Для учебного хоста добавлены:

- `Dockerfile` — образ Django/Gunicorn на Python 3.10, приложение запускается от непривилегированного пользователя;
- `compose.yaml` — сервисы `web` и `db`;
- `.env.example` — шаблон конфигурации без реальных секретов;
- `.dockerignore` — исключение локальных, Git и secret-файлов из build context.

### Архитектура стенда

```text
Client / DAST scanner
        |
        | :8000
        v
+-------------------+
| Django / Gunicorn |
| container: web    |
+---------+---------+
          |
          | PostgreSQL :5432
          v
+-------------------+
| PostgreSQL 15     |
| container: db     |
+---------+---------+
          |
          v
   postgres_data
   Docker volume
```

PostgreSQL наружу не публикуется. Доступ к БД возможен только из внутренней Docker-сети `app_net`.

### Подготовка учебного хоста

На сервере должны быть установлены Docker Engine, Docker Compose plugin и Git.

```bash
git clone https://github.com/sergeMMikh/thrdlabapp-devsecops-diploma.git
cd thrdlabapp-devsecops-diploma
cp .env.example .env
```

Отредактировать `.env`:

```env
DEBUG=False
SECRET_KEY=<long-random-secret>
ALLOWED_HOSTS=127.0.0.1,localhost,<SERVER_IP_OR_DOMAIN>
CSRF_TRUSTED_ORIGINS=http://<SERVER_IP_OR_DOMAIN>:8000

PGDATABASE=electrochemistry_lab
PGUSER=postgres
PGPASSWORD=<strong-database-password>
PGPORT=5432

APP_BIND_ADDRESS=0.0.0.0
APP_PORT=8000
```

`.env` входит в `.gitignore` и не должен попадать в Git.

Для генерации Django secret key можно использовать, например:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(50))"
```

### Запуск

```bash
docker compose config
docker compose build
docker compose up -d
```

При старте `web` автоматически:

1. ждёт успешного healthcheck PostgreSQL через Compose dependency;
2. выполняет `python manage.py migrate --noinput`;
3. выполняет `python manage.py collectstatic --noinput`;
4. запускает Gunicorn на `0.0.0.0:8000` внутри контейнера.

Проверка состояния:

```bash
docker compose ps
docker compose logs --tail=100 web
docker compose logs --tail=100 db
```

Приложение должно быть доступно по адресу:

```text
http://<SERVER_IP_OR_DOMAIN>:8000
```

### Остановка и повторный запуск

Остановить контейнеры, сохранив данные PostgreSQL:

```bash
docker compose down
```

Повторно запустить:

```bash
docker compose up -d
```

Полностью удалить стенд вместе с volume базы данных:

```bash
docker compose down -v
```

Последнюю команду следует использовать только тогда, когда данные учебной БД действительно можно удалить.

### Обновление приложения на учебном хосте

До реализации автоматического CD обновление выполняется вручную:

```bash
git pull
docker compose up -d --build
```

На следующем этапе эти действия будут перенесены в CI/CD pipeline.

## Security decisions in the deployment baseline

Уже на базовом этапе приняты несколько решений, полезных для последующего DevSecOps-контроля:

- PostgreSQL не публикует порт на host network;
- реальные пароли и `SECRET_KEY` не записаны в Compose/Dockerfile;
- `.env` исключён из Git и Docker build context;
- application container запускается не от `root`;
- для PostgreSQL и Django/Gunicorn настроены healthchecks;
- PostgreSQL хранит данные в именованном volume;
- для контейнеров установлена restart policy `unless-stopped`;
- версия PostgreSQL зафиксирована как `15-alpine`.

Это исходный deployment baseline. Далее он будет расширен scanner'ами, отчётами, staging DAST и Security Gateway.