import logging
import pandas as pd
from app.celery_app import celery

from app.models.products import Product, ProductFile, ProductFileStatus
from app.utils import set_data_in_redis


@celery.task()
def save_product_to_db(file_id: int):
    """
    Task to save data in DB from csv file.
    Also, set the current upload status in Redis cache
    for tracking the progress of the file upload.
    """
    from app import app

    app.app_context().push()
    try:
        product_file = ProductFile.get_by_pk(file_id)
        df = pd.read_csv(product_file.file_path)
        total_rows = len(df)
        logging.info(f"total_rows: {total_rows}")
        inserted_rows = 0
        for _, row in df.iterrows():
            obj = Product.query.filter(Product.sku == str(row["sku"])).first()
            if obj:
                obj.update_obj({"name": row["name"], "description": row["description"]})
            else:
                obj = Product(
                    sku=row["sku"], name=row["name"], description=row["description"]
                )
                obj.save()
            inserted_rows = inserted_rows + 1
            set_data_in_redis(
                f"product_{file_id}",
                {
                    "status": ProductFileStatus.PENDING,
                    "inserted_rows": inserted_rows,
                    "total_rows": total_rows,
                },
            )
        logging.info(f"Total inserted rows: {inserted_rows}")
        set_data_in_redis(
            f"product_{file_id}",
            {
                "status": ProductFileStatus.SUCCESS,
                "inserted_rows": inserted_rows,
                "total_rows": total_rows,
            },
        )
        product_file.status = ProductFileStatus.SUCCESS
        product_file.save()
    except Exception as e:
        set_data_in_redis(
            f"product_{file_id}",
            {
                "status": ProductFileStatus.ERROR,
                "inserted_rows": inserted_rows,
                "total_rows": total_rows,
            },
        )
        product_file.status = ProductFileStatus.ERROR
        product_file.save()
        logging.error(e)
