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

    @classmethod
    def get_by_pk(cls, pk: int):
        return db.session.query(cls).get(pk)


class ProductFile(Base):
    __tablename__ = "product_file"

    file_path = db.Column(db.String)
    status = db.Column(db.Enum(ProductFileStatus), default=ProductFileStatus.PENDING)


class Product(Base):
    __tablename__ = "product"

    name = db.Column(db.String(240))
    sku = db.Column(db.String(240), unique=True, index=True)
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    @property
    def serialize(self):
        return {
            "name": self.name,
            "sku": self.sku,
            "description": self.description,
            "is_active": self.is_active,
        }

    def update_obj(self, data):
        self.name = data.get("name", self.name)
        self.description = data.get("description", self.description)
        self.is_active = data.get("is_active", self.is_active)
        db.session.commit()
        return self


class WebHook(Base):
    __tablename__ = "product_webhook"

    name = db.Column(db.String(240))
    url = db.Column(db.String(240))
    is_active = db.Column(db.Boolean, default=True)
