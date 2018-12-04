#!/usr/bin/env python3

# import os
# import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    auth_type = Column(String(2))
    first_name = Column(String(32))
    last_name = Column(String(32))
    email = Column(String(64))
    password_hash = Column(String(64))
    password_salt = Column(String(16))
    picture = Column(String(64))
    auth_token = Column(String(64))
    description = Column(String(256))


class Media(Base):
    __tablename__ = "media"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("user.id"))
    type = Column(String(32))
    genre = Column(String(64))
    medium = Column(String(32))
    artist = Column(String(64))
    title = Column(String(128))

    @property
    def serialize(self):
        # return object in serialisable format
        return {
            "id" :  self.id,
            "user_id" :  self.user_id,
            "type" :  self.type,
            "genre" :  self.genre,
            "medium" :  self.medium,
            "artist" :  self.artist,
            "title" :  self.title
        }




#################

# class Restaurant(Base):
#     __tablename__ = 'restaurant'
#
#     id = Column(Integer, primary_key=True)
#     name = Column(String(250), nullable=False)
#
#     @property
#     def serialize(self):
#         # return object in serialisable format
#         return {
#             'id' : self.id,
#             'name' : self.name,
#         }
#
#
# class MenuItem(Base):
#     __tablename__ = 'menu_item'
#
#     name = Column(String(80), nullable = False)
#     id = Column(Integer, primary_key = True)
#     description = Column(String(250))
#     price = Column(String(8))
#     course = Column(String(250))
#     restaurant_id = Column(Integer,ForeignKey('restaurant.id'))
#     restaurant = relationship(Restaurant)
#
#     @property
#     def serialize(self):
#         return {
#             'name' : self.name,
#             'description' : self.description,
#             'id' : self.id,
#             'price' : self.price,
#             'course' : self.course,
#         }



engine = create_engine("sqlite:///mcollector.sqlite3")
Base.metadata.create_all(engine)
