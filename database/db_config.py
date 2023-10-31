import sqlalchemy as db
from vadimskymusic.logger import log
from sqlalchemy_utils import database_exists

eng = db.create_engine('sqlite:///vsm-database.db', echo=True)
conn = eng.connect()
meta = db.MetaData()

users = db.Table('users', meta,
            db.Column('id', db.Integer, primary_key=True),
            db.Column('premium', db.Boolean)
                         #заглушка
)
tracks = db.Table('tracks', meta,
                          db.Column('id', db.Integer, primary_key=True),
                          db.Column('name', db.Text),
                          db.Column('listened', db.Integer),
                          db.Column('listened_recently', db.Integer),
                          db.Column('path', db.Text),
                          db.Column('image_path', db.Text),
                          db.Column('description', db.Text)
)
meta.create_all(eng, checkfirst=True)

