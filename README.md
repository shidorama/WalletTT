# Test task
Wallet system

# Summary
Core of the service is working and most of the endpoints are operational. 
Unfortunately, time available prohibited me from writing tests or working with edge cases - __we can discuss options online if you wish__.

# Tech stack
* DB: Mongo - lgihtweight, easy to use with high load/big data. Individual document updates are atomic
* Framework: Flask: lightweight with fast debugging and building, good out of the box rest support, easy to extend

# Extras
* Most of the requests are checked using JSONSchema to validate data that we're getting from users

# Caveats
 * Wallet can only be topped up using it's default currency. In full system conversion mechanism may be implemented.
 * Wallet report right now dumps all the entries. This is obviously suboptimal. For "real" implementation I would favor 
 either worker that would assemble data in background and post it to user or paginated output.
 * To make all updates consistent 
 * There is no 'rollback' action for transfer if it fails - should be implemented
 * code in some parts are suboptimal as I hadnt had enough time 
 to go through it and optimize it we can discuss it online afterwards
 
# Not implemented
 * No tests except for PEP8 checks 
 * XML export
 * Login
 * Docker file / automatic setup
 * no updated statuses, though logs are present
 * Python Logging is not implemented - we're logging operations to mongo
 * Signup/report requests are not logged as operations
 
# Running locally
 * Any Ubuntu or compatible machine
 * Ensure that you have python 3.7 (should work with lower version, but hadnt'checked)
 * Install reqs from requirements.txt (using pip probably)
 * Install local instance of mongodb or change config settings in config.py
 * Run service locally (python3 app.py)
 * access it on http://localhost:8080 or using hosts FQDN
 
# Endpoints

* `POST /signup`
    * Create new wallet
    * request structure: schemas/user.json#signup
* `GET /wallet/<wallet_id>/`
* `POST /wallet/<wallet_id>/topup/`
    * request structure: schemas/wallet.json#topup
* `POST /wallet/<wallet_id>/transfer/<wallet_id>/`
    * request structure: schemas/wallet.json#transfer
* `GET /wallet/<wallet_id>/report/<mode>/`
    * mode is either `csv` or `json`