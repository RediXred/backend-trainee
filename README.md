# PR Reviewer Assignment Service

## Тех.стек

- Python3
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL
- Docker Compose

### Выполненные доп.задания:
1. Эндпоинт статистики - `/statistics`
2. Результаты нагрузочного тестирования - в папке `reports_load_tests`, описание тестов - `tests_results.md`
3. Добавлен метод массовой деактивации пользователей и безопасная переназначаемость открытых PR (`/users/bulkDeactivate`)
4. Реализовано интеграционное тестирование (pytest)
5. Описана конфигурация линтера (ниже в `README.md`)

---

* При проверке нагрузочного тестирования необходимо установить python locust или:
* Установка окружения:
```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### Запуск проекта

1. Запуск с помощью Docker Compose:
   ```bash
   docker-compose up --build -d
   ```

   Или Makefile:
   ```bash
   make up
   ```

2. Сервис будет доступен по адресу:
   - API: http://localhost:8080
   - Документация: http://localhost:8080/docs

### Настройка .env

* Скопируйте .env.example в .env в корне проекта

## API endpoints

### Teams
- `POST /team/add` - Создать команду с участниками
- `GET /team/get?team_name=<name>` - Получить команду

### Users
- `POST /users/setIsActive` - Установить флаг активности пользователя
- `POST /users/bulkDeactivate` - Массовая деактивация пользователей команды
- `GET /users/getReview?user_id=<id>` - Получить PR'ы пользователя

### Pull Requests
- `POST /pullRequest/create` - Создать PR и назначить ревьюверов
- `POST /pullRequest/merge` - Пометить PR как MERGED
- `POST /pullRequest/reassign` - Переназначить ревьювера

### Health
- `GET /health` - Проверка здоровья сервиса

### Statistics
- `GET /statistics` - Получение статистики по PR

## Тестирование

### Запуск интеграционных тестов (pytest)

1. Приложение должно быть запущено:
   ```bash
   make up
   ```

2. Запустите тесты:
   ```bash
   make test
   ```

### Запуск нагрузочных тестов (python locust)
* Должен быть установлен python locust (см. выше)

1. Приложение должно быть запущено:
   ```bash
   make up
   ```

2. Запуск locust-ui:
   ```bash
   make load-test-ui
   ```

3. Или запуск без ui (предварительно настроить load_test.sh):
   ```bash
   ./load_test.sh
   ```

## Линтинг и форматирование кода

Проект использует несколько линтеров:

- flake8 - проверка стиля кода
- mypy - type checking
- black - автоматическое форматирование кода
- isort - автоматическая сортировка импортов

### Конфигурация

Конфигурация линтеров находится в следующих файлах:

- `.flake8` - конфигурация для flake8
- `setup.cfg` - конфигурация для black и isort
- `mypy.ini` - конфигурация для mypy

#### Основные настройки:

* flake8:
   - Максимальная длина строки: 100 символов
   - Максимальная сложность функции: 10
   - Игнорируются файлы миграций Alembic
   - Игнорируются некоторые правила, несовместимые с black (E203, W503) и mypy (E712)

* mypy:
   - Python версия: 3.11
   - Строгая проверка опциональных типов
   - Предупреждения о неиспользуемых импортах, недостижимых местах кода, отсутствии возврата
   - Проверка соответствия типов передаваемых аргументов
   - Игнорирование отсутствующих импортов для сторонних библиотек
   - Файлы миграций исключены из проверки

* black и isort:
   - Длина строки: 100 символов
   - Профиль isort совместим с black
   - Файлы миграций исключены из форматирования

### Запуск
* Необходимы зависимости (см. выше про python locust).
```bash
flake8 app/ tests/

mypy app/ tests/

black app/ tests/

isort app/ tests/
```

### Или запуск в Docker

```bash
docker compose exec app flake8 app/ tests/

docker compose exec app mypy app/

docker compose exec app black app/ tests/

docker compose exec app isort app/ tests/
```

## Пояснения о допущениях

1. В эндпоинте `/users/getReview` в openapi.yml нет 404 возврата. В коде добавлен код 404 при обращении к несуществующему пользователю

2. В эндпоинте `/users/setIsActive` в ответе добавлен reassigned_prs - количество переназначенных PR. Если у активного пользователя были PR, в которых он был ревьюером, а потом его статус активности поменялся на False, то во всех PR, где он был ревьюером, неактивный пользователь поменяется на активного. Это добавлено после реализации безопасно переназначаемости открытых PR и массовой деактивации пользователей команды.
