from flask_mongoengine import MongoEngine

db = MongoEngine()
print(id(db))
