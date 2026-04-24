from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

db = SQLAlchemy()

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            # do not serialize the password, its a security breach
        }
    

class Item(db.Model):
    __abstract__ = True
    name: Mapped[str] = mapped_column(unique=True)
    url: Mapped[str] = mapped_column(unique=True)
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
        }


class Character(Item): 
    id: Mapped[int] = mapped_column(primary_key=True)
    hair_color: Mapped[str] = mapped_column(nullable=True)
    eye_color: Mapped[str] = mapped_column(nullable=True)
    skin_color: Mapped[str] = mapped_column(nullable=True)
    height: Mapped[str] = mapped_column(nullable=True)

    def full_serialize(self):
        base_dictionary = super().serialize()
        base_dictionary.update({
            "hair_color": self.hair_color,
            "eye_color": self.eye_color,
            "skin_color": self.height,
            "height": self.height
        })
        return base_dictionary

class Planet(Item): 
    id: Mapped[int] = mapped_column(primary_key=True)
    climate: Mapped[str] = mapped_column(nullable=True)
    gravity: Mapped[str] = mapped_column(nullable=True)
    surface_water: Mapped[str] = mapped_column(nullable=True)
    terrain: Mapped[str] = mapped_column(nullable=True)
    diameter: Mapped[str] = mapped_column(nullable=True)
    rotation_period: Mapped[str] = mapped_column(nullable=True)


class Favorite(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    character_id: Mapped[int] = mapped_column(ForeignKey("character.id"), nullable=True)
    planet_id: Mapped[int] = mapped_column(ForeignKey("planet.id"), nullable=True)

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "character_id": self.character_id,
            "planet_id": self.planet_id
        }


# class Post(db.Model):
#     id: Mapped[int] = mapped_column(primary_key=True)
#     text: Mapped[str] = mapped_column(String(1024), nullable=False)
#     user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
#     user: Mapped["User"] = relationship(
#         "User",
#         back_populates="posts"
#     )

class Kris(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    text: Mapped[str] = mapped_column(String(1024), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))