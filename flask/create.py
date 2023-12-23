import os

from flask import Flask
from dotenv import load_dotenv

from models import db

load_dotenv()
def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"postgresql://{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}@{os.environ['POSTGRES_HOST']}/{os.environ['POSTGRES_DB']}"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
    return app


def main():
    db.create_all()


if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        main()
