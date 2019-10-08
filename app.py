from hmac import HMAC

import jsonschema
from flask import Flask, request, make_response, Response
from flask_jsonschema_validator import JSONSchemaValidator
from mongoengine import SaveConditionError

import config
from constants.operation_status import OperationStatus
from helpers.exchange import get_exchange_rates
from helpers.reports import create_csv_report
from models import db
from models.operations_log import OperationLogEntry
from models.wallet import Wallet

app = Flask(__name__)

app.config.update(config.config_data)
JSONSchemaValidator(app=app, root="schemas")

db.init_app(app)


@app.errorhandler(jsonschema.ValidationError)
def onValidationError(e):
    return Response("There was a validation error: " + str(e), 400)


@app.route('/signup', methods=["POST"])
@app.validate("user", "signup")
def register():
    print(request.json)
    wallet_data = request.json
    password_hashed = HMAC(b"somesecret", str.encode(wallet_data['password'])).digest()
    wallet_data['password'] = password_hashed
    wallet = Wallet(**wallet_data)
    wallet.save()
    return make_response((app.json_encoder().encode(wallet.get_sanitized_object()), "201"))


@app.route('/signin', methods=["POST"])
@app.validate("user", "signin")
def signin():
    raise NotImplementedError()


@app.route('/wallet/<uuid:wallet_id>/', methods=["GET"])
def wallet_info(wallet_id):
    wallet_query = Wallet.objects(wallet_id=wallet_id)
    if wallet_query.count() != 1:
        return make_response(("Databse consistency error", 500))
    wallet = wallet_query.first()
    return make_response((app.json_encoder().encode(wallet.get_sanitized_object()), "201"))


@app.route('/wallet/<uuid:wallet_id>/topup/', methods=["POST"])
@app.validate("wallet", "topup")
def wallet_topup(wallet_id):
    wallet_query = Wallet.objects(wallet_id=wallet_id)
    if wallet_query.count() != 1:
        return make_response(("Databse consistency error", 500))
    wallet = wallet_query.first()
    old_balance = wallet.balance
    OperationLogEntry.log_topup(wallet, request.json['amount'], OperationStatus.NEW)
    wallet.balance += request.json['amount']
    try:
        wallet.save(save_condition={'balance': old_balance})
    except SaveConditionError as e:
        wallet.reload()
        OperationLogEntry.log_topup(wallet, request.json['amount'], OperationStatus.FAILED)
        return make_response((app.json_encoder().encode(wallet.get_sanitized_object()), 409))
    else:
        OperationLogEntry.log_topup(wallet, request.json['amount'], OperationStatus.SUCCESS)
        return make_response((app.json_encoder().encode(wallet.get_sanitized_object()), 200))


@app.route('/wallet/<uuid:wallet_id>/report/<string:mode>/', methods=["GET"])
def wallet_report(wallet_id, mode):
    allowed_modes = {'json', 'xml', 'csv'}
    if mode not in allowed_modes:
        return make_response(('Wrong report type requested!', 400))
    wallet_query = Wallet.objects(wallet_id=wallet_id)
    if wallet_query.count() != 1:
        return make_response(("Databse consistency error", 500))
    report_list = OperationLogEntry.objects(wallet_id=wallet_id).all()
    if mode == 'csv':
        return make_response((create_csv_report(report_list), 200))
    if mode == 'xml':
        return make_response(("XML not supported", 417))

    return make_response((app.json_encoder().encode([i.to_mongo() for i in report_list]), 200))


@app.route('/wallet/<uuid:source_wallet_id>/transfer/<uuid:target_wallet_id>/', methods=["POST"])
@app.validate("wallet", "transfer")
def wallet_transfer(source_wallet_id, target_wallet_id):
    source_wallet_query = Wallet.objects(wallet_id=source_wallet_id)
    if source_wallet_query.count() != 1:
        return make_response(("Database consistency error", 500))

    target_wallet_query = Wallet.objects(wallet_id=target_wallet_id)
    if target_wallet_query.count() != 1:
        return make_response(("Database consistency error", 500))

    source_wallet = source_wallet_query.first()
    target_wallet = target_wallet_query.first()
    transfer_amount = request.json['amount']

    OperationLogEntry.log_transfer(source_wallet, target_wallet, transfer_amount, OperationStatus.NEW)
    OperationLogEntry.log_transfer(target_wallet, source_wallet, 0, OperationStatus.NEW)

    if source_wallet.balance < transfer_amount:
        return make_response(('Low balance', 400))

    initial_balance = source_wallet.balance

    source_currency = source_wallet.currency
    target_currency = target_wallet.currency

    exchange_rate = get_exchange_rates(source_currency, target_currency)

    converted_transfer_amount = transfer_amount * exchange_rate
    source_wallet.balance -= transfer_amount

    try:
        source_wallet.save(save_condition={'balance': initial_balance})
    except SaveConditionError as e:
        source_wallet.reload()
        OperationLogEntry.log_transfer(source_wallet, target_wallet, transfer_amount, OperationStatus.FAILED)
        OperationLogEntry.log_transfer(target_wallet, source_wallet, -converted_transfer_amount, OperationStatus.FAILED)
    else:
        try:
            target_wallet.update(inc__balance=converted_transfer_amount)
        except Exception as e:
            target_wallet.reload()
            OperationLogEntry.log_transfer(source_wallet, target_wallet, transfer_amount,
                                           OperationStatus.CRITICAL)  # Should raise an alarm and be investigated ASAP
        else:
            OperationLogEntry.log_transfer(source_wallet, target_wallet, transfer_amount, OperationStatus.SUCCESS)
            OperationLogEntry.log_transfer(target_wallet, source_wallet, -converted_transfer_amount,
                                           OperationStatus.SUCCESS)
    return make_response((app.json_encoder().encode(source_wallet.get_sanitized_object()), "200"))


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)
