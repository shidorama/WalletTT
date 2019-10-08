import datetime
import uuid

from mongoengine import fields

from constants.operation_status import OperationStatus
from models import db
from models.wallet import Wallet


class OperationLogEntry(db.Document):
    meta = {
        'indexes': [
            'wallet_id',
            'date',
            'target_wallet_id',
            'state',
            'event_type'
        ]
    }

    entry_id = fields.UUIDField(required=True, default=lambda: str(uuid.uuid4()), primary_key=True)
    wallet_id = fields.UUIDField(required=True)
    target_wallet_id = fields.UUIDField()
    state = fields.StringField(required=True)
    date = fields.DateTimeField(required=True, default=lambda: datetime.datetime.now())
    event_type = fields.StringField(required=True)
    amount = fields.FloatField()
    currency = fields.StringField()
    balance = fields.FloatField()

    additional_info = fields.StringField()  # For any last minute additions / diag data

    @classmethod
    def log_topup(cls, wallet, amount, state):
        if not isinstance(wallet, Wallet) or not isinstance(state, OperationStatus):
            return False
        entry = OperationLogEntry()

        entry.wallet_id = wallet.wallet_id
        entry.state = state.name
        entry.event_type = 'TOPUP'
        entry.amount = amount
        entry.balance = wallet.balance
        entry.save()

        return entry

    @classmethod
    def log_transfer(cls, source_wallet, target_wallet, amount, state):
        if not isinstance(source_wallet, Wallet) \
                or not isinstance(target_wallet, Wallet) \
                or not isinstance(state, OperationStatus):
            return False
        entry = OperationLogEntry()

        entry.state = state.name
        entry.wallet_id = source_wallet.wallet_id
        entry.target_wallet_id = target_wallet.wallet_id
        entry.balance = source_wallet.balance
        entry.currency = source_wallet.currency
        entry.event_type = 'TRANSFER'
        entry.amount = amount
        entry.save()

        return entry
