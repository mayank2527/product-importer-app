import logging
from flask import Flask
from flask_migrate import Migrate
from flask_restful import Api

from app.controllers.index import Index
from app.config import config_settings
from app.controllers.products import Product, ProductUpload, ProductUploadStatus
from app.models import db

migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(config_settings["development"])

    api = Api(app)
    api.add_resource(Index, "/")
    api.add_resource(Product, "/products")
    api.add_resource(ProductUpload, "/product_upload")
    api.add_resource(ProductUploadStatus, "/upload_status/<int:file_id>")

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    migrate.init_app(app, db)

    logging.basicConfig(level=logging.DEBUG)

    return app


app = create_app()
