#!/usr/bin/env python3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mcmodel import Base, User, Media
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify

app = Flask(__name__)

session = ""

# connect to DB (call session.close at end of views)
def connectDB():
    global session
    engine = create_engine("sqlite:///mcollector.sqlite3")
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    session = DBSession()

# home page, shows list of collections and latest entries
@app.route("/")
def landingPage():
    connectDB()
    collections = session.query(User.id, User.first_name, User.last_name).all()
    session.close()
    fullnames = []
    for row in collections:
        x = row[0], row[1] + " " + row[2]
        fullnames.append(x)
    print(fullnames)
    return render_template("home.html", fullnames=fullnames)

# show individual collection
@app.route("/collections/<int:id>")
def showCollection(id):
    return "Single collection page: id={}".format(id)

# edit collection description
@app.route("/collections/<int:id>/edit", methods=["GET", "POST"])
def editCollection(id):
    if request.method == "GET":
        return "Edit collection description page: id={}".format(id)
    if request.method == "POST":
        return "POST:  Edit collection description page: id={}".format(id)

# delete all media entries inside collection
@app.route("/collections/<int:id>/clear", methods=["DELETE"])
def emptyCollection(id):
    if request.method == "DELETE":
        return "Delete all media in collection: id={}".format(id)

# show media detail page
@app.route("/collections/<int:user_id>/media/<int:media_id>")
def showMedia(user_id, media_id):
    return "Media item page: user_id={} - media_id={}".format(user_id, media_id)

# edit media detail page
@app.route("/collections/<int:user_id>/media/<int:media_id>/edit", methods=["GET", "POST"])
def editMedia(user_id, media_id):
    if request.method == "GET":
        return "Edit media page: user_id={} - media_id={}".format(user_id, media_id)
    if request.method == "POST":
        return "POST:  Edit media page: user_id={} - media_id={}".format(user_id, media_id)

# delete media item from collection
@app.route("/collections/<int:user_id>/media/<int:media_id>/delete", methods=["DELETE"])
def deleteMedia(user_id, media_id):
    if request.method == "DELETE":
        return "Delete media entry: user_id={} - media_id={}".format(user_id, media_id)

@app.route("/login")
def loginPage():
    return "login page"

@app.route("/registration")
def registrationPage():
    return "registration page"

@app.route("/logout")
def logoutPage():
    return "logout page"


if __name__ == "__main__":
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host="0.0.0.0", port=8000)
