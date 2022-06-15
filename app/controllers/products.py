import os
import logging
import werkzeug
from werkzeug.utils import secure_filename
from flask import make_response, jsonify, request
from flask_api import status
from flask_restful import Resource, reqparse

from app.models.products import ProductFile, Product as ProductModel, WebHook
from app.tasks import call_webhooks, save_product_to_db
from app.config import config_settings
from app.utils import get_data_from_redis
from app.models import db


class ProductUpload(Resource):
    def post(self):
        """
        API to uplaod product csv file.
        It save's the file in upload path and calls the celery
        task to process the file asynchronously.
        """
        parse = reqparse.RequestParser()
        parse.add_argument(
            "file", type=werkzeug.datastructures.FileStorage, location="files"
        )
        args = parse.parse_args()
        csv_file = args["file"]
        filename = secure_filename(csv_file.filename)
        file_path = os.path.join(
            config_settings["file_upload_config"].FILE_UPLOAD_PATH, filename
        )
        if not os.path.isdir(config_settings["file_upload_config"].FILE_UPLOAD_PATH):
            os.mkdir(config_settings["file_upload_config"].FILE_UPLOAD_PATH)

        csv_file.save(file_path)

        file_obj = ProductFile(file_path=file_path)
        file_obj.save()

        save_product_to_db.delay(file_obj.id)
        return make_response("success", status.HTTP_201_CREATED)


class Product(Resource):
    def get(self):
        """
        Get Products API. Supports filters on name,sku,description
        and is_active. Also, supports sorting and pagination.
        """
        args = request.args
        limit = args.get("limit", 10)
        offset = args.get("offset", 0)
        query = db.session.query(ProductModel)

        if args.get("name", ""):
            query = query.filter(ProductModel.name == args.get("name"))
        if args.get("sku", ""):
            query = query.filter(ProductModel.sku == args.get("sku"))
        if args.get("description", ""):
            query = query.filter(ProductModel.description == args.get("description"))
        if args.get("is_active", ""):
            query = query.filter(
                ProductModel.is_active == True
                if args.get("is_active").lower() == "true"
                else False
            )

        if args.get("sort", "") and args.get("sort").startswith("-"):
            field = args.get("sort").replace("-", "")
            sort_by = getattr(ProductModel, field).desc()
        else:
            sort_by = getattr(ProductModel, args.get("sort", "") or "sku").asc()
        query = query.order_by(sort_by).limit(limit).offset(offset)

        return make_response(
            jsonify([i.serialize for i in query.all()]), status.HTTP_200_OK
        )

    def post(self):
        """
        POST products api to create new product.
        """
        body = request.json
        sku = body["sku"]
        product = ProductModel.query.filter(ProductModel.sku == sku).first()
        if product:
            return make_response(
                f"SKU {sku} already exist.", status.HTTP_400_BAD_REQUEST
            )
        obj = ProductModel(sku=sku, name=body["name"], description=body["description"])
        obj.save()
        call_webhooks.delay(obj.serialize)
        return make_response("Success", status.HTTP_201_CREATED)

    def put(self):
        """
        PUT products api to update existing product based on unique sku.
        """
        body = request.json
        product = ProductModel.query.filter(ProductModel.sku == body["sku"]).first()
        if product:
            product.update_obj(
                {
                    "name": body["name"],
                    "description": body["description"],
                    "is_active": body["is_active"],
                }
            )
            return make_response("Product updated", status.HTTP_200_OK)
        else:
            return make_response("SKU not found", status.HTTP_404_NOT_FOUND)

    def delete(self):
        """
        Delete API to delete all products.
        """
        try:
            ProductModel.query.delete()
            return make_response(
                "All products deleted successfully", status.HTTP_200_OK
            )
        except Exception as e:
            logging.error(e)
            return make_response(
                "Deletion Failed.", status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ProductUploadStatus(Resource):
    def get(self, file_id):
        """
        API endpoint to track the progress of the file upload.
        Checks the redis cache for the current upload status.
        """
        data = get_data_from_redis(f"product_{file_id}")
        if data:
            return make_response(jsonify(data), status.HTTP_200_OK)

        product_file = ProductFile.get_by_pk(file_id)
        if product_file:
            return make_response(
                jsonify({"status": product_file.status.value}), status.HTTP_200_OK
            )

        return make_response("File id not found", status.HTTP_404_NOT_FOUND)


class ProductWebHook(Resource):
    def get(self):
        """
        Get list of all webhooks.
        """
        web_hooks = WebHook.query.all()
        return make_response(
            jsonify([i.serialize for i in web_hooks]), status.HTTP_200_OK
        )

    def post(self):
        """
        API endpoint to create product create/update webhook.
        """
        body = request.json
        obj = WebHook(name=body["name"], url=body["url"])
        obj.save()
        return make_response("Success", status.HTTP_201_CREATED)
