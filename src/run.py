from core import GunicornApplication, get_app_options
from main import app as fastapi_app


def main():
    gunicorn_app = GunicornApplication(
        application=fastapi_app,
        options=get_app_options(
            host="0.0.0.0",
            port=8000,
            workers=4,
            timeout=45
        )
    )
    gunicorn_app.run()


if __name__ == '__main__':
    main()
