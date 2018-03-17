import random

import flask
import flask_sqlalchemy
import sqlalchemy

from models.models import Base, Relays
import os
print(os.getcwd())

SECRET_CODE = open('models/info/key.txt', 'r').read()
KEY_LENGTH = 8


class InvalidError(Exception):
    pass


def catch_db_error(return_none=True):
    def db_decorator(f):
        def func_wrapper(self, *args, **kwargs):
            try:
                return f(self, *args, **kwargs)
            except sqlalchemy.exc.OperationalError as e:
                print('error in catch_db_error: %s' % e)
                self.db.session.rollback()
                if return_none:
                    return None
                else:
                    return False
        return func_wrapper

    return db_decorator


class RelayManager:

    def __init__(self, username, password, host, db_name='relays', port=5432):
        self.username = username
        self.password = password
        self.host = host
        self.db_name = db_name
        self.port = port

        self.db = None

    @property
    def uri(self):
        return 'mysql://%s:%s@%s:%d/%s' % (self.username,
                                           self.password,
                                           self.host,
                                           self.port,
                                           self.db_name)

    def connect_to_db(self):
        app = flask.Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = self.uri
        self.db = flask_sqlalchemy.SQLAlchemy(app)

    def create_db(self):
        try:
            test_engine = sqlalchemy.create_engine(self.uri)
            test_conn = test_engine.connect()
            test_conn.execute('commit')
            test_conn.close()
        except sqlalchemy.exc.OperationalError:
            default_uri = 'mysql://%s:%s@%s:%d/mysql' % (self.username,
                                                         self.password,
                                                         self.host,
                                                         self.port)
            default_engine = sqlalchemy.create_engine(default_uri)
            default_conn = default_engine.connect()
            default_conn.execute('commit')
            default_conn.execute('CREATE DATABASE %s;' % self.db_name)
            default_conn.execute('commit')
            default_conn.close()

    def create_tables(self):
        engine = sqlalchemy.create_engine(self.uri, convert_unicode=True)
        Base.metadata.create_all(engine)

    @catch_db_error(True)
    def add_relay(self, secret_key, destination_url):
        if secret_key != SECRET_CODE:
            return None

        key = ''.join([str(random.randint(0, 9)) for i in range(KEY_LENGTH)])

        relay = Relays(key, destination_url)
        self.db.session.add(relay)
        self.db.session.commit()
        return key

    @catch_db_error(True)
    def get_url_head(self, key):
        url_head = self.db.session.query(Relays).filter(Relays.hash_key == key).with_entities(Relays.destination_url).first()
        return url_head[0]
