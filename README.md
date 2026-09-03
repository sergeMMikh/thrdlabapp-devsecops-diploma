## Django Template

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template/GB6Eki?referralCode=U5zXSw)

### Recent updates

* Added client-side availability checks for both equipment and furnace bookings. When a date/equipment combination is already taken, a red warning appears beneath the form before submission explaining why the request will fail. Backend still enforces uniqueness so double submissions remain impossible.

### Testing notes

* The project defaults to using **PostgreSQL** in normal operation. During automated tests, either via `manage.py test` or `pytest`, the settings module switches to an in-memory SQLite database.
* This avoids failures on CI runners or developer machines where the configured Postgres hostname may not be reachable.
* The same behaviour is triggered when the environment variable `CI` is set.

### Deploy notes

The GitHub Actions workflow now has two stages:

* `tests`: installs dependencies, runs `flake8`, and runs `pytest`.
* `deploy`: after successful tests on `main`, connects to the remote server over SSH and runs `git pull`.

Required GitHub repository secrets:

* `DEPLOY_HOST` - server hostname or IP, for example `192.168.1.160`
* `DEPLOY_USER` - SSH user, for example `smm`
* `DEPLOY_SSH_KEY` - private SSH key for the deploy user

Recommended server `.env` values in `~/thrdlabapp/.env`:

```env
DEBUG=False
PGDATABASE=electrochemistry_lab
PGUSER=postgres
PGPASSWORD=your-password
PGHOST=localhost
PGPORT=5432
ALLOWED_HOSTS=127.0.0.1,192.168.1.160,electrochemistry-lab.up.railway.app
CSRF_TRUSTED_ORIGINS=https://electrochemistry-lab.up.railway.app
SECRET_KEY=your-production-secret-key
```

Why this matters:

* `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS` are now environment-driven, so future `git pull` on the server will not conflict with local server-only settings.
* The deploy job stays simple and avoids `sudo`, so it does not stop on a password prompt.
