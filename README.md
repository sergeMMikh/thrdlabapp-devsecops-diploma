# THRDLabApp DevSecOps Diploma

Дипломный проект по треку **DevSecOps**.

Цель работы — построить безопасный CI/CD-пайплайн для веб-приложения с автоматизированными проверками безопасности и механизмом остановки небезопасного релиза.

Задание Нетологии: [sib-Diplom-Track-DevSecOps](https://github.com/netology-code/sib-Diplom-Track-DevSecOps)

Исходный репозиторий приложения: [THRDLabApp](https://github.com/sergeMMikh/thrdlabapp.git).

---

## План работы

Работа выполняется последовательно по этапам дипломного задания.

### Этап 0. Подготовка стенда и исходного проекта

Задачи:

- подготовить отдельный дипломный репозиторий;
- развернуть учебный VPS;
- настроить SSH-доступ по ключу;
- ограничить сетевой доступ с помощью UFW;
- контейнеризировать приложение;
- подготовить `Dockerfile` и `docker compose`;
- вынести конфигурацию и секреты в переменные окружения;
- развернуть приложение и PostgreSQL на учебном хосте;
- проверить доступность приложения извне;
- зафиксировать исходное состояние проекта и инфраструктуры.

Результат этапа:

- приложение воспроизводимо разворачивается на учебном VPS;
- PostgreSQL доступен только внутри Docker-сети;
- наружу опубликованы только необходимые сервисы;
- секреты не хранятся в репозитории.

<details>
<summary>Скриншоты</summary>

</br>
Список поднятых Docker контейнеров на целевом хосте

![docker ps](image.png)</br>

Web приложение

![web-app](image-1.png)</br>

Панель администратора Django

![admin](image-2.png)</br>

Подключение git репозиториев

![git](image-3.png)</br>

</details>

Ссылки на репозитории проекта:
* [Исходный проект](https://github.com/sergeMMikh/thrdlabapp.git)
* [GitLab](https://gitlab.com/sergeMMikh/thrdlabapp-devsecops-diploma.git)
* [DockerHub](https://hub.docker.com/repository/docker/sergemmikh/thrdlabapp-devsecops-diploma/general)

### Этап 1. CI/CD

Критерии задания:

1. настроенный пайплайн сборки и доставки программного обеспечения;
2. использование удалённого сервера для развёртывания;
3. документированный процесс.

#### Реализованная архитектура

Для CI/CD используется **GitLab CI/CD**, для хранения собранных контейнерных образов — **Docker Hub**, а целевой средой развёртывания является учебный VPS.

Принципиальное решение этапа — **не собирать приложение на целевом сервере**. Docker-образ является готовым версионируемым артефактом: он собирается в CI, публикуется в Docker Hub и после успешного прохождения предыдущих стадий доставляется на VPS.

Pipeline на текущем этапе реализован как последовательность:

```text
validate
   |
   v
auth
   |-- Docker Hub authentication
   `-- SSH authentication
   |
   v
lint
   |
   v
build
   |-- docker build
   |-- tag :<commit-sha>
   `-- push -> Docker Hub
   |
   v
deploy
   |-- SSH -> training VPS
   |-- docker compose pull
   |-- docker compose up -d
   `-- application starts with persistent PostgreSQL data
```

Docker-образ публикуется с тегом, соответствующим commit SHA. Это обеспечивает трассируемость:

```text
Git commit
    |
    v
GitLab pipeline
    |
    v
Docker image:<commit-sha>
    |
    v
Training VPS
```

Таким образом, можно однозначно определить, какой исходный код соответствует реально развёрнутому контейнеру, а также выполнить откат на предыдущий образ.

Production Compose использует готовый `image:`, а не локальный `build:`. PostgreSQL хранит данные в постоянном Docker volume, поэтому пересоздание контейнера приложения и доставка нового образа не приводят к пересозданию базы данных. При старте приложения Django применяет только отсутствующие миграции.

Использование контейнерного образа как основного deployment artifact также позволяет в дальнейшем использовать тот же образ для развёртывания в Kubernetes без изменения принципа доставки приложения.

#### Разделение runner-ов

Для проекта настроен собственный **GitLab Runner** в WSL (Ubuntu 22.04) с Docker executor. Он используется как контролируемая CI-среда для локальных стадий pipeline и в дальнейшем будет использоваться для security scanning.

При настройке CD было выявлено сетевое ограничение: университетская сеть, в которой работает self-hosted WSL runner, блокирует исходящие подключения к SSH-порту `2217` учебного VPS. Поэтому deployment с этого runner технически невозможен без изменения сетевой инфраструктуры.

В связи с этим задачи pipeline разделены между runner-ами:

```text
GitLab
   |
   +--> Self-hosted WSL Runner (Docker executor)
   |       |
   |       +--> validate
   |       +--> Docker Hub authentication
   |       +--> lint
   |       +--> build
   |       `--> security checks (следующие этапы)
   |
   `--> GitLab-hosted Runner
           |
           +--> SSH authentication
           `--> deploy -> VPS:2217
```

Такое разделение является следствием сетевого ограничения, а не способом обхода security checks. Deploy остаётся отдельной финальной стадией pipeline и выполняется только после успешного завершения зависимых CI-задач.

С точки зрения безопасности CI/CD разделение runner-ов не снижает контроль над релизом при соблюдении следующих условий:

- deployment job не выполняет повторную сборку приложения;
- на VPS доставляется именно образ, созданный предыдущей стадией pipeline;
- образ идентифицируется immutable-тегом на основе commit SHA;
- секреты Docker Hub и SSH хранятся в защищённых GitLab CI/CD variables и не находятся в репозитории;
- deployment выполняется по SSH с ключевой аутентификацией;
- целевой сервер не используется как CI/build runner;
- будущий Security Gateway располагается **до deployment**, поэтому GitLab-hosted deploy runner не сможет выпустить артефакт, не прошедший обязательные security checks.

Дополнительным преимуществом такого разделения является уменьшение совмещения ролей: self-hosted runner выполняет сборку и анализ, а deployment выполняется отдельным runner. При этом необходимо учитывать границу доверия между двумя средами. Поэтому в дальнейшей реализации pipeline deployment будет привязан к конкретному проверенному тегу/commit SHA, а доступ к deployment credentials будет предоставляться только deployment job в защищённой ветке.

#### Разделение ответственности

```text
GitHub             — основной репозиторий проекта и документации
GitLab             — CI/CD pipeline
WSL GitLab Runner  — build и security jobs
GitLab Runner      — deployment transport до VPS
Docker Hub         — registry готовых Docker-образов
VPS                — целевая среда развёртывания
```

Для работы с GitHub и GitLab используется один локальный Git-репозиторий с отдельными remote. CI/CD выполняется на стороне GitLab.

#### Реализовано

- создан GitLab-репозиторий и подключён отдельным Git remote;
- подготовлен `.gitlab-ci.yml`;
- настроены protected CI/CD variables;
- отдельно проверяется наличие обязательных переменных;
- проверена аутентификация в Docker Hub;
- проверена SSH-аутентификация на учебном VPS;
- настроен self-hosted GitLab Runner в WSL с Docker executor;
- реализован lint через отдельный `requirements-lint.txt`;
- Docker-образ собирается после успешного lint;
- образ публикуется в Docker Hub с тегом commit SHA;
- подготовлен `compose.prod.yaml`, использующий готовый Docker image;
- настроен автоматический deployment по SSH;
- PostgreSQL использует постоянный Docker volume;
- выполнен успешный pipeline `validate -> auth -> lint -> build -> deploy`;
- после автоматического deployment подтверждена работоспособность Django-приложения на учебном VPS.

#### Дальнейшее развитие CI/CD

На следующих этапах текущий pipeline будет расширен тестированием и security-проверками. Deployment должен стать конечной точкой после Security Gateway:

```text
commit
   |
   v
lint -> tests -> SAST/SCA/Secrets -> build -> image scan
                                      |
                                      v
                               Security Gateway
                                      |
                         PASS --------+-------- FAIL
                           |                     |
                           v                     v
                       Docker Hub           block release
                           |
                           v
                        deploy
```

### Этап 2. SAST

Критерии задания:

1. покрытие исходного кода проверками;
2. автоматический запуск проверок во время сборки;
3. выгрузка результатов в CI или систему управления уязвимостями.

План реализации:

- выполнить статический анализ Python/Django-кода;
- использовать несколько подходящих инструментов, например Semgrep и Bandit;
- запускать SAST автоматически в GitLab CI/CD;
- сохранять отчёты как artifacts;
- провести анализ найденных проблем и ложных срабатываний.

Цель — покрыть проверками весь применимый исходный код проекта.

### Этап 3. DAST

Критерии задания:

1. покрытие работающего сервиса динамическими проверками;
2. успешный запуск доступных методов сканирования;
3. выгрузка результатов в CI или систему управления уязвимостями.

План реализации:

- выполнять DAST против развернутого приложения на учебном стенде;
- использовать OWASP ZAP;
- выполнить baseline scan;
- при необходимости добавить authenticated/API scan;
- сохранять HTML/JSON/XML отчёты как CI artifacts;
- разобрать обнаруженные уязвимости и false positive результаты.

Целевая схема:

```text
GitLab CI/CD
      |
      v
   deploy
      |
      v
training VPS
      |
      v
  OWASP ZAP
      |
      v
DAST report
```

### Этап 4. Security Checks

Критерии задания:

1. проверка репозитория на секреты;
2. проверка конфигурации или контейнерных образов.

План реализации:

- secret scanning — Gitleaks;
- dependency scanning — pip-audit и/или Trivy;
- container image scanning — Trivy;
- Dockerfile / configuration checks;
- проверка CI/CD и deployment-конфигурации;
- формирование SBOM при необходимости;
- сохранение отчётов в artifacts.

Контролируемые области:

```text
source code
    |
    +-- secrets
    +-- dependencies
    +-- configuration
    +-- Dockerfile
    +-- container image
    +-- CI/CD configuration
```

### Этап 5. Security Gateway

Критерии задания:

1. остановка релиза при наличии недопустимых уязвимостей;
2. дополнительные автоматизированные действия: комментарии в MR и рекомендации по исправлению.

План реализации:

- определить правила допуска релиза;
- блокировать deployment при критических результатах security scans;
- определить допустимые уровни `Critical`, `High`, `Medium`, `Low`;
- агрегировать результаты SAST, DAST, secret scanning и container scanning;
- выводить понятный Security Summary в GitLab CI/CD;
- публиковать информацию о проблемах в merge request;
- документировать исключения и false positives.

Целевой pipeline:

```text
                         +--> SAST -----------+
                         |                    |
commit --> lint --> tests+--> Secret Scan ----+--> Security Gateway --> Build --> Docker Hub --> Deploy
                         |                    |
                         +--> SCA ------------+
                                              |
Docker image ----------------> Image Scan ----+
                                              |
                                              +--> block release
                                              +--> report
                                              +--> MR feedback
```

### Этап 6. Анализ результатов и итоговая документация

После реализации pipeline необходимо:

- собрать результаты всех проверок;
- классифицировать обнаруженные проблемы;
- отделить подтверждённые уязвимости от false positives;
- оценить риски и приоритет исправления;
- описать remediation;
- зафиксировать архитектуру итогового DevSecOps pipeline;
- собрать evidence работы каждого этапа;
- подготовить итоговое описание дипломного проекта.

---

## Планируемые инструменты

| Задача | Инструмент |
|---|---|
| Source / documentation | GitHub |
| CI/CD | GitLab CI/CD |
| CI runner | Self-hosted GitLab Runner / WSL / Docker executor |
| Deployment runner | GitLab-hosted Runner |
| Container registry | Docker Hub |
| Containerization | Docker / Docker Compose |
| Future orchestration | Kubernetes (при необходимости) |
| Web application | Django / Gunicorn |
| Database | PostgreSQL |
| SAST | Semgrep, Bandit |
| Dependency scanning | pip-audit, Trivy |
| Secret scanning | Gitleaks |
| Container scanning | Trivy |
| DAST | OWASP ZAP |
| Security reports | GitLab CI artifacts / reports |
| Security Gateway | GitLab CI jobs, rules and release conditions |

Состав инструментов может уточняться по мере выполнения работы. Для каждого выбранного средства в итоговой документации будет указана причина выбора и область покрытия.

---

## Принципы выполнения работы

При разработке pipeline придерживаемся следующих правил:

- каждый этап сначала реализуется и проверяется отдельно;
- Docker-образ является основным версионируемым артефактом доставки;
- целевой сервер не используется как build-среда приложения;
- security checks являются частью CI/CD, а не отдельной ручной процедурой;
- реальные секреты не коммитятся в Git и не включаются в Docker image;
- результаты проверок сохраняются и доступны для анализа;
- найденные уязвимости не только фиксируются, но и анализируются;
- false positives документируются;
- критические проблемы должны иметь возможность остановить релиз;
- deployment credentials должны быть доступны только jobs, которым они действительно необходимы;
- все ключевые решения и результаты отражаются в документации.

---

## Статус выполнения

| Этап | Статус |
|---|---|
| 0. Подготовка стенда | Выполнен |
| 1. CI/CD | Базовый pipeline и deployment выполнены |
| 2. SAST | Не начат |
| 3. DAST | Не начат |
| 4. Security Checks | Не начат |
| 5. Security Gateway | Не начат |
| 6. Итоговая документация | Не начат |

README будет обновляться по мере прохождения этапов дипломной работы.
