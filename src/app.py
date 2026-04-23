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

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200


# Select all people from database
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


# Select all planets from database
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


# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
