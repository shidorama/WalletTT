# In real application depending on circumstances I would store this in DB
# and refresh this with worker frequently


def get_exchange_to_usd():
    return {
        "USD": 1,
        "EUR": 1.1,
        "CNY": 0.14,
        "CAD": 0.75
    }


def get_exchange_rates(source_currency, target_currency):
    exchange_rate_data = get_exchange_to_usd()
    if len({source_currency, target_currency}.intersection(exchange_rate_data)) != len({source_currency, target_currency}):
        raise Exception('Currency not supported/exchange rate error')
        # We probably need checks for negative values and other edge cases

    source_rate = exchange_rate_data.get(source_currency)
    target_currency = exchange_rate_data.get(target_currency)
    return source_rate / target_currency
