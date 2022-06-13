import enum

from app.models import db


class ProductFileStatus(enum.Enum):
    PENDING = "Pending"
    SUCCESS = "Success"
    ERROR = "Error"


class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

    def save(self):
        db.session.add(self)
        db.session.commit()
        return self


class ProductFile(Base):
    __tablename__ = "product_file"

    file = db.Column(db.LargeBinary)
    status = db.Column(db.Enum(ProductFileStatus), default=ProductFileStatus.PENDING)


class Product(Base):
    __tablename__ = "product"

    name = db.Column(db.String(240))
    sku = db.Column(db.String(240), unique=True, index=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
