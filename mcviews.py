#!/usr/bin/env python3

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from mcmodel import Base, User, Media
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import random
import hashlib
from flask import session as login_session

app = Flask(__name__)

session = ""

constants = {
    "formats" :  ("vinyl", "cd", "cassette", "other"),
    "genres" :  ("blues", "classical", "country", "data", "folk", "jazz", "newage", "reggae", "rock", "soundtrack", "misc"),
    "types" :  ("album", "ep", "lp", "mixtape", "single")
}


# connect to DB (call session.close at end of views)
def connectDB():
    global session
    engine = create_engine("sqlite:///mcollector.sqlite3")
    Base.metadata.bind = engine

    DBSession = sessionmaker(bind=engine)
    session = DBSession()


# returns list of tuples containing collection names for nav column
def getNames():
    connectDB()
    collections = session.query(User.id, User.first_name, User.last_name).all()
    session.close()
    fullnames = []
    for row in collections:
        x = row[0], row[1] + " " + row[2]
        fullnames.append(x)
    return fullnames


# return user row
def getUser(user_id):
    connectDB()
    query = session.query(User).filter(User.id == user_id).scalar()
    session.close()
    return query


# get user meta data
def getUsermeta(user_id):
    user = getUser(user_id)
    usermeta = {
        "id" :  user.id,
        "fullname" :  user.first_name + " " + user.last_name,
        "description" :  user.description
    }
    return usermeta


# get full name of logged in user
def getAuthdUser():
    if login_session["username"]:
        connectDB()
        query = session.query(User.id).filter(User.email==login_session["username"]).scalar()
        session.close()
        usermeta = getUsermeta(query)
        return usermeta
    else:
        return None


# home page, shows list of collections and latest entries
@app.route("/")
def landingPage():
    fullnames = getNames()
    landinglist = []
    connectDB()
    # get 5 biggest collections
    query = session.query(User.id, User.first_name, User.last_name, func.count(Media.id)).outerjoin(Media).group_by(User.id).order_by(func.count(Media.id).desc()).limit(5)
    session.close()
    topfive = []
    for row in query:
        x = {
            "id" : row[0],
            "fullname" : row[1] + " " + row[2],
            "count" : row[3]
        }
        topfive.append(x)
    # loggedin = getAuthdUser()
    return render_template("home.html", fullnames=fullnames, topfive=topfive)


# show individual collection
@app.route("/collections/<int:user_id>")
def showCollection(user_id):
    fullnames = getNames()
    usermeta = getUsermeta(user_id)
    print(usermeta)

    connectDB()
    query = session.query(Media).filter(Media.user_id == user_id).all()
    session.close()
    media = []
    for row in query:
        x = {
            "id" :  row.id,
            "artist" :  row.artist,
            "title" :  row.title,
            "genre" :  row.genre,
            "type" :  row.type,
            "medium" :  row.medium,
            "user_id" :  row.user_id
        }
        media.append(x)
        # loggedin = getAuthdUser()
    return render_template("collections.html", fullnames=fullnames, user=usermeta, media=media)


# edit collection description
@app.route("/collections/<int:user_id>/description/edit", methods=["GET", "POST"])
def editCollection(user_id):
    if request.method == "GET":
        fullnames = getNames()
        user = getUser(user_id)
        usermeta = {
            "id" :  user.id,
            "fullname" :  user.first_name + " " + user.last_name,
            "description" :  user.description
        }
        return render_template("editdescription.html", fullnames=fullnames, user=usermeta)
    if request.method == "POST":
        fullnames = getNames()
        user = getUser(user_id)
        form = request.form
        if user and form["description"] != "":
            user.description = form["description"]
            session.add(user)
            session.commit()
            session.close()
            flash("*** Description successfully edited ***")
            return showCollection(user_id)
        else:
            flash("*** Error: description not edited ***")
            return showCollection(user_id)


# delete all media entries inside collection
@app.route("/collections/<int:id>/clear", methods=["GET", "POST"])
def emptyCollection(id):
    if request.method == "GET":
        return "Delete all media in collection confirmation page: id={}".format(id)
    if request.method == "POST":
        return "Delete all media in collection: id={}".format(id)


# show media detail page
@app.route("/collections/<int:user_id>/media/<int:media_id>")
def showMedia(user_id, media_id):
    return "Media item page: user_id={} - media_id={}".format(user_id, media_id)


# edit media detail page
@app.route("/collections/<int:user_id>/media/<int:media_id>/edit", methods=["GET", "POST"])
def editMedia(user_id, media_id):
    if request.method == "GET":
        fullnames = getNames()
        user = getUser(user_id)
        usermeta = {
            "id" :  user.id,
            "fullname" :  user.first_name + " " + user.last_name,
            "description" :  user.description
        }
        # get media detail
        connectDB()
        query = session.query(Media).filter(Media.user_id==user_id, Media.id==media_id).scalar()
        session.close()
        return render_template("editmedia.html", fullnames=fullnames, user=usermeta, media=query, constants=constants)
    if request.method == "POST":
        form = request.form
        # get media item object
        if len(form) > 4 and form["artist"] != "" and form["title"]:
            connectDB()
            query = session.query(Media).filter(Media.user_id==user_id, Media.id==media_id).scalar()
            # check if form submission contains a change
            if query.artist != form["artist"] or query.title != form["title"] or query.genre != form["genre"] or query.type != form["type"] or query.medium != form["format"]:
                query.artist = form["artist"]
                query.title = form["title"]
                query.genre = form["genre"]
                query.type = form["type"]
                query.medium = form["format"]
                session.add(query)
                session.commit()
            session.close()
            flash("*** Media item successfully edited***")
            return showCollection(user_id)
        else:
            flash("*** Could not edit. One or more inputs empty ***")
            return showCollection(user_id)


# add new media item
@app.route("/collections/<int:user_id>/media/new", methods=["GET", "POST"])
def newMedia(user_id):
    if request.method == "GET":
        fullnames = getNames()
        user = getUser(user_id)
        usermeta = {
            "id" :  user.id,
            "fullname" :  user.first_name + " " + user.last_name,
            "description" :  user.description
        }
        # return "New media item page user_id: {}".format(user_id)
        return render_template("newmedia.html", fullnames=fullnames, user=usermeta, constants=constants)
    elif request.method == "POST":
        form = request.form
        # check that all params entered
        if len(form) > 4 and form["artist"] != "" and form["title"]:
            add = Media(
                user_id = user_id,
                artist = form["artist"],
                title = form["title"],
                genre = form["genre"],
                type = form["type"],
                medium = form["format"]
            )
            connectDB()
            session.add(add)
            session.commit()
            session.close()
            flash("*** New media item successfully added ***")
        else:
            flash("*** One or more fields not entered ***")
        return showCollection(user_id)


# delete media item from collection
@app.route("/collections/<int:user_id>/media/<int:media_id>/delete", methods=["GET", "POST"])
def deleteMedia(user_id, media_id):
    if request.method == "GET":
        fullnames = getNames()
        user = getUser(user_id)
        usermeta = {
            "id" :  user.id,
            "fullname" :  user.first_name + " " + user.last_name,
            "description" :  user.description
        }
        connectDB()
        query = session.query(Media).filter(Media.user_id==user_id, Media.id==media_id).scalar()
        session.close()
        return render_template("deletemedia.html", fullnames=fullnames, user=usermeta, media=query)

    if request.method == "POST":
        connectDB()
        query = session.query(Media).filter(Media.user_id==user_id, Media.id==media_id).scalar()
        if query:
            session.delete(query)
            session.commit()
            flash("*** Media item successfully deleted ***")
        session.close()
        return showCollection(user_id)


@app.route("/auth/login", methods=["GET", "POST"])
def loginPage():
    if request.method == "GET":
        fullnames = getNames()

        # # Create anti-forgery state token
        # state = ''.join(random.choice(string.ascii_uppercase + string.digits)
        #                 for x in xrange(32))
        # login_session['state'] = state
        # loggedin = getAuthdUser()
        return render_template("login.html", fullnames=fullnames)
    elif request.method == "POST":
        form = request.form
        if form["email"] is not "" and form["password"] is not "":
            print(form["email"])
            print(form["password"])
            # get user obj with email
            connectDB()
            query = session.query(User).filter(User.email==form["email"]).scalar()
            session.close()
            if query:
                # get salt, hash inputed password, check against db
                salted = form["password"] + query.password_salt
                hashed = hashlib.sha256(str.encode(salted)).hexdigest()
                if hashed == query.password_hash:
                    login_session["username"] = query.email
                    print("LOGIN SUCCESSFULL")
                    print(login_session)
                else:
                    print("ACCESS DENIED")
            return "POST: login page, {}  {}  {}".format(form["email"], form["password"], len(form))
        else:
            return "missing user or passowrd"


@app.route("/auth/registration")
def registrationPage():
    return "registration page"


@app.route("/auth/logout")
def logoutPage():
    # remove the username from the session if it's there
    login_session.pop('username', None)
    return "logout page"


if __name__ == "__main__":
    app.secret_key = "super_secret_key"
    app.debug = True
    app.run(host="0.0.0.0", port=8000)
