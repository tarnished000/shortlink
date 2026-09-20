# shortlink

Небольшой сервис сокращения ссылок — pet-проект для демонстрации базовых DevOps-навыков: контейнеризация, docker-compose, реверс-прокси, CI.

## Архитектура

```
                 ┌────────┐
  клиент ───────►│ Nginx  │
                 └───┬────┘
                     │ reverse proxy
                     ▼
                 ┌────────┐
                 │  app   │  FastAPI (uvicorn)
                 └───┬────┘
                     │
                     ▼
                 ┌────────┐
                 │Postgres│
                 └────────┘
```

- **app** — FastAPI-приложение: создание коротких ссылок, редирект по коду, счётчик переходов.
- **db** — PostgreSQL, хранит ссылки.
- **nginx** — реверс-прокси перед приложением.

## Быстрый старт

```bash
git clone https://github.com/tarnished000/shortlink.git
cd shortlink
docker compose up --build
```

Сервис будет доступен на `http://localhost:8080`.

## API

| Метод | Путь | Описание |
| --- | --- | --- |
| `POST` | `/links` | Создать короткую ссылку. Тело: `{"target_url": "https://..."}` |
| `GET` | `/{code}` | Редирект на целевой URL, увеличивает счётчик переходов |
| `GET` | `/links/{code}` | Статистика по ссылке (сколько раз перешли) |
| `GET` | `/health` | Проверка живости — используется Docker healthcheck |

Пример:

```bash
curl -X POST http://localhost:8080/links \
  -H "Content-Type: application/json" \
  -d '{"target_url": "https://github.com/tarnished000"}'

# {"code": "aZ3kLp9", "target_url": "...", "clicks": 0, "created_at": "..."}

curl -L http://localhost:8080/aZ3kLp9
```

## Локальная разработка без Docker

```bash
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

По умолчанию (без переменной `DATABASE_URL`) приложение использует локальный SQLite-файл — удобно для разработки и для тестов.

## Тесты и CI

```bash
pytest -v
```

`.github/workflows/ci.yml` на каждый push/PR в `main` прогоняет тесты и собирает Docker-образ.

## Стек

Python · FastAPI · SQLAlchemy · PostgreSQL · Docker · Docker Compose · Nginx · GitHub Actions

## Статус

Рабочий MVP: основные эндпоинты покрыты тестами, есть healthcheck и CI. Дальше можно развивать: rate limiting, TTL для ссылок, деплой через Kubernetes/Helm.

---

