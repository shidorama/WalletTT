import uuid

from mongoengine import fields

from models import db


class Wallet(db.Document):
    safe_fields = {"_id", "balance", "currency", "name", "country"}
    wallet_id = fields.UUIDField(required=True, default=lambda: str(uuid.uuid4()), primary_key=True)

    balance = fields.FloatField(required=True, default=0.0)
    currency = fields.StringField(required=True)

    name = fields.StringField(required=True)
    city = fields.StringField(required=True)
    country = fields.StringField(required=True)
    password = fields.BinaryField(required=True)

    def get_sanitized_object(self):
        return {k: v for k, v in self.to_mongo().items() if k in self.safe_fields}
