import os

from .config import load_env


def mysql_connect():
    import mysql.connector

    load_env()
    return mysql.connector.connect(
        host=os.environ["MYSQL_HOST"],
        port=int(os.environ["MYSQL_PORT"]),
        user=os.environ["MYSQL_USER"],
        password=os.environ["MYSQL_PASSWORD"],
        database=os.environ["MYSQL_DATABASE"],
    )


def mongo_client():
    from pymongo import MongoClient

    load_env()
    client = MongoClient(os.environ["MONGODB_URI"])
    return client, client[os.environ["MONGODB_DATABASE"]]
