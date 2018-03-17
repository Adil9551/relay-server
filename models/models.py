import sqlalchemy

Base = sqlalchemy.ext.declarative.declarative_base()


class Relays(Base):
    __tablename__ = 'relays'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    hash_key = sqlalchemy.Column(sqlalchemy.String(16), nullable=False)
    destination_url = sqlalchemy.Column(sqlalchemy.String(200), nullable=False)

    def __init__(self, hash_key, destination_url):
        self.hash_key = hash_key
        self.destination_url = destination_url
