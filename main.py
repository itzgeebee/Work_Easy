from pprint import pprint
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import *
from wtforms.validators import DataRequired, URL
from flask import Flask, jsonify, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from random import choice

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
Bootstrap(app)

##Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        # Method 1.
        dictionary = {}
        # Loop through each column in the data record
        for column in self.__table__.columns:
            # Create a new dictionary entry;
            # where the key is the name of the column
            # and the value is the value of the column
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

        # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}


class AddCafeForm(FlaskForm):
    title = StringField("Cafe name", validators=[DataRequired()])
    location = StringField("Cafe location", validators=[DataRequired()])
    img_url = StringField("Image URL", validators=[DataRequired(), URL()])
    map_url = StringField("Location(map) URL", validators=[DataRequired(), URL()])
    seats = StringField("No of seats", validators=[DataRequired()])
    coffee = StringField("Coffee price", validators=[DataRequired()])
    has_toilet = BooleanField("Toilets", default=False)
    has_wifi = BooleanField("Wifi", default=False)
    has_sockets = BooleanField("sockets", default=False)
    can_take_calls = BooleanField("can take calls", default=False)
    submit = SubmitField("Submit")


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        search_input = request.form.get("search")
        print(search_input)
        all_cafe = Cafe.query.filter_by(name=search_input).all()
        if not all_cafe:
            return jsonify({"error": {"Not found": "Sorry we do not have a cafe at that location"}})
        else:
            cafes = []
            for i in all_cafe:
                result = i.to_dict()
                cafes.append(result)

            all_cafes_json = jsonify(cafes=cafes).json

    else:
        all_cafes = Cafe.query.all()
        caf_list = []
        for i in all_cafes:
            caf = i.to_dict()
            caf_list.append(caf)

        all_cafes_json = jsonify(cafes=caf_list).json
    pprint(all_cafes_json)
    return render_template("index.html", cafes=all_cafes_json)


@app.route("/random", methods=["GET"])
def random():
    all_cafes = Cafe.query.all()
    random_cafe = choice(all_cafes)

    cafe_json = jsonify(cafe=random_cafe.to_dict()).json

    return cafe_json


@app.route("/all", methods=["GET"])
def all():
    all_cafes = Cafe.query.all()
    caf_list = []
    for i in all_cafes:
        caf = i.to_dict()
        caf_list.append(caf)

    all_cafes_json = jsonify(cafes=caf_list).json
    pprint(all_cafes_json)

    return all_cafes_json


@app.route("/add", methods=["GET", "POST"])
def add():
    form = AddCafeForm()
    if form.validate_on_submit():

        new_cafe = Cafe(
            name=form.title.data,
            map_url=form.map_url.data,
            img_url=form.img_url.data,
            location=form.location.data,
            seats=form.seats.data,
            has_toilet=bool(form.has_toilet.data),
            has_wifi=bool(form.has_wifi.data),
            has_sockets=bool(form.has_sockets.data),
            can_take_calls=bool(form.can_take_calls.data),
            coffee_price=form.coffee.data
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for("home"))

    return render_template("add.html", form = form)


@app.route("/update-price/<int:cafe_id>", methods=["GET", "PATCH"])
def update_price(cafe_id):
    cafe_wanted = Cafe.query.get(cafe_id)
    if cafe_wanted:
        price = request.args.get("price")
        cafe_wanted.coffee_price = price
        db.session.commit()
        return jsonify({"success": "Successfully updated the price"})
    else:
        return jsonify({"error": {
            "Not found": "Sorry, a cafe with that id was not found in the database"
        }}), 404


@app.route("/delete/<int:cafe_id>", methods=["GET", "DELETE"])
def report_closed(cafe_id):
    cafe_wanted = Cafe.query.get(cafe_id)
    api_key = "top-secret-key"
    key = request.args.get("key")
    if key == api_key:
        if cafe_wanted:
            db.session.delete(cafe_wanted)
            db.session.commit()
            return jsonify({"success": "Successfully deleted"})
        else:
            return jsonify({"error": {
                "Not found": "Sorry, a cafe with that id was not found in the database"
            }}), 404

    elif not key or key != api_key:
        return jsonify({"Forbidden": {
            "Key error": "please enter a valid API key"
        }}), 403


## HTTP GET - Read Record

## HTTP POST - Create Record

## HTTP PUT/PATCH - Update Record

## HTTP DELETE - Delete Record


if __name__ == '__main__':
    app.run(debug=True)
