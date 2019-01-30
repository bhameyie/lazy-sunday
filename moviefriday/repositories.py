from dataclasses import dataclass
from typing import Optional

import bson

from moviefriday.db import DatabaseConfig


@dataclass
class User:
    username: str
    password: str
    id: bson.objectid = bson.ObjectId()


@dataclass
class Movie:
    title: str
    blob_id: str
    is_mp4: bool
    id: str = None


def convert_user_record(dico):
    if dico is None:
        return None

    return User(dico['username'], dico['password'], dico['_id'])


def convert_movie_record(dico):
    if dico is None:
        return None

    return Movie(dico['title'], dico['blobId'],
                 dico['isMp4'], str(dico['_id']))


class MovieRepository:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.movies = config.flix_db['movies']

    def find_by_id(self, movie_id):
        found = self.movies.find_one({'_id': bson.ObjectId(movie_id)})
        return convert_movie_record(found)

    def insert(self, movie: Movie):
        for_insert = {
            'title': movie.title,
            'blobId': movie.blob_id,
            'isMp4': movie.is_mp4,
            '_id': bson.ObjectId()
        }
        self.movies.insert(for_insert)
        return for_insert['_id']


class UserRepository:
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.users = config.flix_db['users']

    def find_by_username(self, user_name):
        found = self.users.find_one({'username': user_name})
        return convert_user_record(found)

    def insert(self, user: User):
        for_insert = {
            'username': user.username,
            'password': user.password,
            '_id': bson.ObjectId()
        }
        self.users.insert(for_insert)
        return for_insert['_id']

    def find_by_id(self, user_id):
        found = self.users.find_one({'_id': bson.ObjectId(user_id)})
        return convert_user_record(found)
