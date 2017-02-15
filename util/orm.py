from sqlalchemy import Integer, Column, create_engine, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

Base = declarative_base()


class Status(Base):
    __tablename__ = 'status'
    id = Column(Integer, primary_key=True)
    progress = Column(Integer)
    result = Column(TEXT)

    def update(self, id=None, progress=None, result=None):
        if progress is not None:
            self.progress = progress

        if result is not None:
            self.result = result

    def dump(self):
        return dict([(k, v) for k, v in vars(self).items() if not k.startswith('_')])


def init_db(uri):
    engine = create_engine(uri, convert_unicode=True)
    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    Base.query = db_session.query_property()
    Base.metadata.create_all(bind=engine)
    return db_session
