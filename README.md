### Directory Notes

- runtime.txt: required by Heroku to know the python environment
- Procfile: required by Heroku to know webserver stuff
- .env: optional for Heroku, has local env vars. [https://devcenter.heroku.com/articles/heroku-local#add-a-config-var-to-your-env-file](https://devcenter.heroku.com/articles/heroku-local#add-a-config-var-to-your-env-file)
- requirements.txt: required by Heroku AND used for tracking python packages used
- manage.py: django file used for interacting with django
- db.sqlite3: sqlite3 database for development locally.
- Makefile: For reusable CLI commands. https://en.wikipedia.org/wiki/Makefile
- example_django_site/: main "django app", entry for django. Has files like settings.py
- docs/: "django app" with page basic documentation.
- util/: Not a django app, just a utility folder for misc. reusable stuff.
- **/: other django apps

might need to do pip install --upgrade pip after activating your venv
You might need to run sudo apt-get install python3-dev

Using python3.5 because couldn't run prospector in python3.6. This is unfortunate because at the
time of writing, everything else can run with python3.6.