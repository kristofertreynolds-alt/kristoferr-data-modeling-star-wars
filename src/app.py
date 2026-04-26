"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, Favorite
from sqlalchemy import select
#from models import Person

########## START API ##########
app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

########### ERRORS ##########
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

########### SITEMAP ##########
@app.route('/')
def sitemap():
    return generate_sitemap(app)









########## USERS ##########
@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200





########### PEOPLE ##########
@app.route("/people")
def get_all_characters():
    statement = (
        select(Character)
    )
    characters = db.session.execute(statement).scalars().all()
    character_dictionaries = []
    for character in characters:
        dictionary = character.serialize()
        character_dictionaries.append(dictionary)
    
    print(character_dictionaries)
    return jsonify(character_dictionaries), 200




########### PEOPLE 1,2,3 ##########
@app.route("/people/<int:person_id>")
def get_one_character(person_id: int):
    statement = (
        select(Character)
        .where(Character.id==person_id)
    )
    character = db.session.execute(statement).scalar_one_or_none()
    if not character: #is character none?
        return jsonify({"message": "character not found"}), 404
    return jsonify(character.full_serialize()), 200




########### USERS ##########
@app.route("/users")
def get_users():
    users = db.session.execute(select(User)).scalars().all()
    user_dictionaries = [user.serialize() for user in users]
    return jsonify(user_dictionaries), 200




########## FAVORITES ##########
@app.route("/users/favorites") #/users/favorites?user_id=5
def get_favorites_for_user_in_query_string():
    query_params = request.args
    favorites = db.session.execute(
        select(Favorite)
        .where(Favorite.user_id == query_params.get("user_id"))
    ).scalars().all()
    favorite_dictionaries = [favorite.serialize() for favorite in favorites]
    return jsonify(favorite_dictionaries), 200



########## FAVORITES 1,2,3 ##########
@app.route("/users/<int:user_id>/favorites/<int:favorite_id>", methods=["DELETE"])
def delete_a_favorite(user_id, favorite_id):
    favorite = db.session.execute(
        select(Favorite)
        .where(
            Favorite.user_id == user_id,
            Favorite.id == favorite_id
        )
    ).scalars().one_or_none()
    if favorite:
        db.session.delete(favorite)
        db.session.commit()
    return "", 204


# FAVORITES CHARACTER
@app.route("/favorites/people/<int:person_id>", methods=["POST"])
def add_person_as_favorite(person_id): 
    body = request.json
    user_id = body.get("user_id")
    if not user_id:
        return jsonify(dict(message="a user id is required!")), 400
    user = db.session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
    if not user: 
        return jsonify(dict(message="no such user")), 400
    person = db.session.execute(select(Character).where(Character.id==person_id)).scalar_one_or_none()
    if not person:
        return jsonify(dict(message="no such character")), 400
    already_exists = db.session.execute(
        select(Favorite)
        .where(
            Favorite.planet_id == None,
            Favorite.character_id == person.id,
            Favorite.user_id == user.id
        )
    ).scalar_one_or_none()
    if already_exists:
        return jsonify(dict(message="this character is already your favorite")), 400
    favorite = Favorite(
        user_id = user.id,
        character_id = person.id,
        planet_id= None
    )
    db.session.add(favorite)
    try:
        db.session.commit()
    except Exception as error:
        return jsonify(error.__dict__())
    favorite_dictionary = favorite.serialize()
    return jsonify(favorite_dictionary), 201


########### PLANETS ##########
@app.route("/planets")
def get_all_planets():
    statement = (
        select(Planet)
    )
    planets = db.session.execute(statement).scalars().all()
    planet_dictionaries = [planet.serialize() for planet in planets]
    # for planet in planets:
    #     dictionary = planet.serialize()
    #     planet_dictionaries.append(dictionary) 
    # print(planet_dictionaries)
    return jsonify(planet_dictionaries), 200



########## PLANETS/ID ##########
@app.route("/planets/<int:planet_ID>", methods=["GET"])
def get_a_single_planet(planet_ID):
    statement = (
        select(Planet)
        .where(Planet.id == planet_ID)
    )
    planet = db.session.execute(statement).scalar_one_or_none()
    if not planet:
        return jsonify({"msg": "there is no planet with that ID sorry"}), 404
    return jsonify(planet.serialize()), 200







# ########## FAVORITES/PLANET ##########
@app.route("/favorite/planet/<int:planet_ID>", methods=["POST"])
def add_favorite_planet(planet_ID):
    body = request.json
    user_id = body.get("user_id")
    if not user_id:
        return jsonify({"msg": "there is no user in request"}), 404
    sql = (
        select(User)
        .where(User.id == user_id)
    )
    user = db.session.execute(sql).scalar_one_or_none()
    if not user: 
        return jsonify({"msg": "there is no user in database"}), 400
    sql = (
        select(Planet)
        .where(Planet.id == planet_ID)
    )
    planet = db.session.execute(sql).scalar_one_or_none()
    if not planet: 
        return jsonify({"msg": "there is no planet in database"}), 400
    
    favorite = Favorite(
        user_id = user.id, 
        character_id = None,
        planet_id = planet.id
    )
    db.session.add(favorite)
    db.session.commit()
    return jsonify(favorite.serialize()), 201
    





# # FAVORITES CHARACTER
# @app.route("/favorites/people/<int:person_id>", methods=["POST"])
# def add_person_as_favorite(person_id): 
#     body = request.json
#     user_id = body.get("user_id")
#     if not user_id:
#         return jsonify(dict(message="a user id is required!")), 400
#     user = db.session.execute(select(User).where(User.id == user_id)).scalar_one_or_none()
#     if not user: 
#         return jsonify(dict(message="no such user")), 400
#     person = db.session.execute(select(Character).where(Character.id==person_id)).scalar_one_or_none()
#     if not person:
#         return jsonify(dict(message="no such character")), 400
#     already_exists = db.session.execute(
#         select(Favorite)
#         .where(
#             Favorite.planet_id == None,
#             Favorite.character_id == person.id,
#             Favorite.user_id == user.id
#         )
#     ).scalar_one_or_none()
#     if already_exists:
#         return jsonify(dict(message="this character is already your favorite")), 400
#     favorite = Favorite(
#         user_id = user.id,
#         character_id = person.id,
#         planet_id= None
#     )
#     db.session.add(favorite)
#     try:
#         db.session.commit()
#     except Exception as error:
#         return jsonify(error.__dict__())
#     favorite_dictionary = favorite.serialize()
#     return jsonify(favorite_dictionary), 201












# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
