# Importing needed modules
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
Base = declarative_base()


# Class to store user info
class User(Base):
    """
    Registered user information is stored in db
    """
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


# Class to store list of categories
class Category(Base):
    """
    All Categories are stored in db
    """
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
           'name': self.name,
           'id': self.id,
        }


# Class to store items
class Items(Base):
    """
    Store all items in db along with their categories
    and also users that created them.
    """
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    description = Column(String(250))
    date = Column(String(20))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
           'id': self.id,
           'name': self.name,
           'description': self.description,
           'date': self.date,
           'category_id': self.category_id,
           'user_id': self.user_id
        }


engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.create_all(engine)
