from flask import Flask

app = Flask(__name__)


def app_run() -> None:
    app.run(port=3333)
