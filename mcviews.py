#!/usr/bin/env python3

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from database_setup import Base, Restaurant, MenuItem
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
    # return "Home, it's working, yay!"
    return render_template("index.html")

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
