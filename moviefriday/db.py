from dataclasses import dataclass
from flask import current_app, g
from pymongo import MongoClient
from pymongo.database import Database


@dataclass
class DatabaseConfig:
    client: MongoClient
    flix_db: Database


def get_db():
    if 'db' not in g:
        cl = MongoClient(current_app.config['MONGO_URI'])
        flix_db = cl['flixdb']
        g.db = DatabaseConfig(client=cl, flix_db=flix_db)
    return g.db


def close_db(e=None):
    db: DatabaseConfig = g.pop('db', None)

    if db is not None:
        db.client.close()
