### Directory Notes

- runtime.txt: required by Heroku to know the python environment
- Procfile: required by Heroku to know webserver stuff
- .env: optional for Heroku, has local env vars. [https://devcenter.heroku.com/articles/heroku-local#add-a-config-var-to-your-env-file](https://devcenter.heroku.com/articles/heroku-local#add-a-config-var-to-your-env-file)
- requirements.txt: required by Heroku and used for tracking packages used
- manage.py: djagno file
- api/: django app, handles routing of all api endpoints
- example_django_site/: djagno app, main point of entry for django. Has files like settings.py
- my_user/: djagno app, Has user model and REST endpoints
