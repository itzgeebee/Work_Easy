from pprint import pprint
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import *
from wtforms.validators import DataRequired, URL
from flask import Flask, jsonify, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
import os



app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY")
app.config['SECRET_KEY'] = "some_secret"

##Connect to Database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URL", 'sqlite:///cafes.db')

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
            dictionary[column.name] = getattr(self, column.name)
        return dictionary

        # Method 2. Altenatively use Dictionary Comprehension to do the same thing.
        # return {column.name: getattr(self, column.name) for column in self.__table__.columns}
# db.create_all()


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
        if request.form["submit_btn"] == "search_det":
            search_input = request.form.get("search")
            print(search_input)
            page = request.args.get("page", 1, type=int)
            all_cafes = db.session.query(Cafe).filter(
                Cafe.name.like(f"{search_input}%") | Cafe.location.like(f"{search_input}%")).paginate(per_page=10,
                                                                                                      page=page)
        else:

            location_input = request.form.get("location")
            socket_input = request.form.get("sockets") == "on"
            wifi_input = request.form.get("wifi") == "on"
            call_input = request.form.get("calls") == "on"
            toilet_input = request.form.get("toilet") == "on"

            print(location_input, socket_input, wifi_input, call_input, toilet_input)
            page = request.args.get("page", 1, type=int)
            all_cafes = Cafe.query.filter_by(location=location_input, has_sockets=socket_input,
                                             has_wifi=wifi_input, has_toilet=toilet_input,
                                             can_take_calls=call_input
                                             ).paginate(per_page=10, page=page)

    else:
        page = request.args.get("page", 1, type=int)
        all_cafes = Cafe.query.paginate(per_page=10, page=page)

    caf_list = []
    for i in all_cafes.items:
        caf = i.to_dict()
        caf_list.append(caf)

    all_cafes_json = jsonify(cafes=caf_list).json
    pprint(all_cafes_json)
    return render_template("index.html", cafes=all_cafes_json, pages=all_cafes)


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

    return render_template("add.html", form=form)


@app.route("/update-cafe", methods=["GET", "POST"])
def update_cafe():
    cafe_id = request.args.get("cafe_id")
    cafe = Cafe.query.get(cafe_id)
    edit_form = AddCafeForm(
        title=cafe.name,
        location=cafe.location,
        img_url=cafe.img_url,
        map_url=cafe.map_url,
        seats=cafe.seats,
        coffee=cafe.coffee_price,
        has_toilet=cafe.has_toilet,
        has_sockets=cafe.has_sockets,
        can_take_calls=cafe.can_take_calls
    )
    if edit_form.validate_on_submit():
        cafe.name = edit_form.title.data
        cafe.location = edit_form.location.data
        cafe.img_url = edit_form.img_url.data
        cafe.map_url = edit_form.map_url.data
        cafe.seats = edit_form.seats.data
        cafe.coffee_price = edit_form.coffee.data
        cafe.has_toilet = bool(edit_form.has_toilet.data)
        cafe.has_wifi = bool(edit_form.has_wifi.data)
        cafe.has_sockets = bool(edit_form.has_sockets.data)
        cafe.can_take_calls = bool(edit_form.can_take_calls.data)

        db.session.commit()
        return redirect(url_for("home"))

    return render_template("update-cafe.html", form=edit_form)


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


if __name__ == '__main__':
    app.run(debug=True)
