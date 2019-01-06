#!/usr/bin/env python3

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker
from mcmodel import Base, User, Media
from flask import Flask, render_template, request, redirect, url_for, flash
from flask import jsonify
import random
import string
import hashlib
from flask import session as login_session

import httplib2
from google.oauth2 import id_token
from google.auth.transport import requests
import json

app = Flask(__name__)

session = ""

constants = {
    "formats": ("vinyl", "cd", "cassette", "other"),
    "genres": ("blues", "classical", "country", "data", "folk", "jazz",
               "newage", "reggae", "rock", "soundtrack", "misc"),
    "types": ("album", "ep", "lp", "mixtape", "single")
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


# check if user already exists by search for email/username
def userExists(email, auth_type="mc"):
    connectDB()
    query = session.query(User).filter(User.email == email,
                                       User.auth_type == auth_type).scalar()
    session.close()
    return query


# get user meta data
def getUsermeta(user_id):
    user = getUser(user_id)
    usermeta = {
        "id": user.id,
        "fullname": user.first_name + " " + user.last_name,
        "description": user.description
    }
    return usermeta


# check for record write access
def checkWrite(user_id):
    user = getUser(user_id)
    if login_session.get("logged_in"):
        if login_session["username"] == user.email and \
          login_session["auth_type"] == user.auth_type:
            return True
    else:
        return False


# ------------------------------ ROUTES ------------------------------


# home page, shows list of collections and latest entries
# fullnames is used to populate nav column
@app.route("/")
def landingPage():
    fullnames = getNames()
    landinglist = []
    connectDB()
    # get 5 biggest collections
    query = session.query(
        User.id,
        User.first_name,
        User.last_name,
        func.count(Media.id)).outerjoin(Media). \
        group_by(User.id).order_by(func.count(Media.id).desc()).limit(5)
    session.close()
    topfive = []
    for row in query:
        x = {
            "id": row[0],
            "fullname": row[1] + " " + row[2],
            "count": row[3]
        }
        topfive.append(x)
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
            "id": row.id,
            "artist": row.artist,
            "title": row.title,
            "genre": row.genre,
            "type": row.type,
            "medium": row.medium,
            "user_id": row.user_id
        }
        media.append(x)
    return render_template("collections.html", fullnames=fullnames,
                           user=usermeta, media=media)


# edit collection description
@app.route("/collections/<int:user_id>/description/edit",
           methods=["GET", "POST"])
def editCollection(user_id):
    if checkWrite(user_id):
        if request.method == "GET":
            fullnames = getNames()
            user = getUser(user_id)
            usermeta = {
                "id": user.id,
                "fullname": user.first_name + " " + user.last_name,
                "description": user.description
            }
            return render_template("editdescription.html",
                                   fullnames=fullnames, user=usermeta)
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
    else:
        flash("*** You can not edit collection you do not own ***")
        return redirect(url_for("loginPage"))


# delete all media entries inside collection
@app.route("/collections/<int:id>/clear", methods=["GET", "POST"])
def emptyCollection(id):
    if request.method == "GET":
        return "Delete all media in collection confirmation page: id={}" \
            .format(id)
    if request.method == "POST":
        return "Delete all media in collection: id={}".format(id)


# show media detail page
@app.route("/collections/<int:user_id>/media/<int:media_id>")
def showMedia(user_id, media_id):
    return "Media item page: user_id={} - media_id={}" \
        .format(user_id, media_id)


# edit media detail page
@app.route("/collections/<int:user_id>/media/<int:media_id>/edit",
           methods=["GET", "POST"])
def editMedia(user_id, media_id):
    if checkWrite(user_id):
        if request.method == "GET":
            fullnames = getNames()
            user = getUser(user_id)
            usermeta = {
                "id": user.id,
                "fullname": user.first_name + " " + user.last_name,
                "description": user.description
            }
            # get media detail
            connectDB()
            query = session.query(Media).filter(Media.user_id == user_id,
                                                Media.id == media_id).scalar()
            session.close()
            return render_template("editmedia.html", fullnames=fullnames,
                                   user=usermeta, media=query,
                                   constants=constants)
        if request.method == "POST":
            form = request.form
            # get media item object
            if len(form) > 4 and form["artist"] != "" and form["title"]:
                connectDB()
                query = session.query(Media).filter(
                    Media.user_id == user_id, Media.id == media_id).scalar()
                # check if form submission contains a change
                if (
                    query.artist != form["artist"] or
                    query.title != form["title"] or
                    query.genre != form["genre"] or
                    query.type != form["type"] or
                    query.medium != form["format"]
                ):
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
    else:
        flash("*** You can not edit collection you do not own ***")
        return redirect(url_for("loginPage"))


# add new media item
@app.route("/collections/<int:user_id>/media/new", methods=["GET", "POST"])
def newMedia(user_id):
    if checkWrite(user_id):
        if request.method == "GET":
            fullnames = getNames()
            user = getUser(user_id)
            usermeta = {
                "id": user.id,
                "fullname": user.first_name + " " + user.last_name,
                "description": user.description
            }
            # return "New media item page user_id: {}".format(user_id)
            return render_template("newmedia.html", fullnames=fullnames,
                                   user=usermeta, constants=constants)
        elif request.method == "POST":
            form = request.form
            # check that all params entered
            if len(form) > 4 and form["artist"] != "" and form["title"]:
                add = Media(
                    user_id=user_id,
                    artist=form["artist"],
                    title=form["title"],
                    genre=form["genre"],
                    type=form["type"],
                    medium=form["format"]
                )
                connectDB()
                session.add(add)
                session.commit()
                session.close()
                flash("*** New media item successfully added ***")
            else:
                flash("*** One or more fields not entered ***")
            return showCollection(user_id)
    else:
        flash("*** You can not edit collection you do not own ***")
        return redirect(url_for("loginPage"))


# delete media item from collection
@app.route("/collections/<int:user_id>/media/<int:media_id>/delete",
           methods=["GET", "POST"])
def deleteMedia(user_id, media_id):
    if checkWrite(user_id):
        if request.method == "GET":
            fullnames = getNames()
            user = getUser(user_id)
            usermeta = {
                "id": user.id,
                "fullname": user.first_name + " " + user.last_name,
                "description": user.description
            }
            connectDB()
            query = session.query(Media).filter(Media.user_id == user_id,
                                                Media.id == media_id).scalar()
            session.close()
            return render_template("deletemedia.html", fullnames=fullnames,
                                   user=usermeta, media=query)

        if request.method == "POST":
            connectDB()
            query = session.query(Media).filter(Media.user_id == user_id,
                                                Media.id == media_id).scalar()
            if query:
                session.delete(query)
                session.commit()
                flash("*** Media item successfully deleted ***")
            session.close()
            return showCollection(user_id)
    else:
        flash("*** You can not edit collection you do not own ***")
        return redirect(url_for("loginPage"))


@app.route("/auth/login", methods=["GET", "POST"])
def loginPage():
    if not login_session.get("logged_in"):
        if request.method == "GET":
            fullnames = getNames()

            # Create anti-forgery state token
            state = ''.join(random.choice(string.ascii_uppercase
                                          + string.digits)
                            for x in range(32))
            login_session['state'] = state

            return render_template("login.html", fullnames=fullnames,
                                   state=state)
        elif request.method == "POST":
            form = request.form
            if form["email"] is not "" and form["password"] is not "":
                # get user obj with email
                connectDB()
                query = session.query(User).filter(
                    User.email == form["email"]).scalar()
                session.close()
                if query:
                    # get salt, hash inputed password, check against db
                    salted = form["password"] + query.password_salt
                    hashed = hashlib.sha256(str.encode(salted)).hexdigest()
                    if hashed == query.password_hash:
                        login_session["username"] = query.email
                        login_session["logged_in"] = True
                        login_session["auth_type"] = "mc"
                return showCollection(query.id)
            else:
                flash("** Missing user or password ***")
                return loginPage()
    else:
        connectDB()
        query = session.query(User.id).filter(
            User.email == login_session["username"],
            User.auth_type == login_session["auth_type"]).scalar()
        session.close()
        return showCollection(query)


# register native mc account
@app.route("/register", methods=["GET", "POST"])
def registerPage():
    if request.method == "GET":
        fullnames = getNames()
        return render_template("register.html", fullnames=fullnames)
    elif request.method == "POST":
        form = request.form
        if not userExists(form["email"]):
            if (
                form["firstname"] is not "" or
                form["lastname"] is not "" or
                form["email"] is not "" or
                form["password"] is not "" or
                form["description"] is not ""
            ):
                # generate 16 char password salt
                chars = string.ascii_letters + string.digits
                salt = "".join(random.choice(chars) for i in range(16))
                # add salt to end of password
                salted = form["password"] + salt
                hashed = hashlib.sha256(str.encode(salted)).hexdigest()
                newuser = User(
                    auth_type="mc",
                    first_name=form["firstname"],
                    last_name=form["lastname"],
                    email=form["email"],
                    password_hash=hashed,
                    password_salt=salt,
                    description=form["description"]
                )
                connectDB()
                session.add(newuser)
                session.commit()
                query = session.query(User.id).filter(
                    User.email == form["email"],
                    User.auth_type == "mc").scalar()
                session.close()
                # login on account creation
                login_session["username"] = form["email"]
                login_session["logged_in"] = True
                login_session["auth_type"] = "mc"
                return showCollection(query)
            else:
                flash("** Missing form data ***")
                return landingPage()
        else:
            flash("** Email address already registered ***")
            return landingPage()


@app.route("/auth/logout")
def logoutPage():
    # remove the username from the session if it's there
    if login_session.get("logged_in"):
        u = login_session["username"]
        login_session.pop("username", None)
        login_session.pop("logged_in", None)
        login_session.pop("auth_type", None)
        flash("*** Logged out as {} ***".format(u))
    else:
        flash("*** Error: no login session ***")
    return landingPage()


# return specific collection in json format
@app.route("/api/collections/<int:user_id>")
def jsonCollection(user_id):
    connectDB()
    query = session.query(Media).filter(Media.user_id == user_id).all()
    session.close()
    return jsonify(Collection=[i.serialize for i in query])


# return specific media item from collection in json format
@app.route("/api/collections/<int:user_id>/media/<int:media_id>")
def jsonMedia(user_id, media_id):
    connectDB()
    query = session.query(Media).filter(
        Media.user_id == user_id, Media.id == media_id).scalar()
    session.close()
    return jsonify(Media=query.serialize)


# process google oauth2 response
# https://developers.google.com/identity/sign-in/web/server-side-flow
@app.route("/oauth2/google", methods=["POST"])
def oauthGoogle():
    if request.method == "POST":
        state = login_session["state"]

        # (Receive token by HTTPS POST)
        # google code https://developers.google.com/identity/sign-in/web/backend-auth

        try:
            # Specify the CLIENT_ID of the app that accesses the backend:
            CLIENT_ID = "738961851559-op16iihovld1kir48n3mrqc6640i49ll.apps.googleusercontent.com"
            token = request.form['idtoken']
            idinfo = id_token.verify_oauth2_token(
                token, requests.Request(), CLIENT_ID)

            # Or, if multiple clients access the backend server:
            # idinfo = id_token.verify_oauth2_token(token, requests.Request())
            # if idinfo['aud'] not in [CLIENT_ID_1, CLIENT_ID_2, CLIENT_ID_3]:
            #     raise ValueError('Could not verify audience.')

            if idinfo['iss'] not in [
                    'accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            # If auth request is from a G Suite domain:
            # if idinfo['hd'] != GSUITE_DOMAIN_NAME:
            #     raise ValueError('Wrong hosted domain.')

            # ID token is valid. Get the user's Google Account ID from the
            # decoded token.
            userid = idinfo['sub']

            print(idinfo)

            # create native account, sub goes in  auth_token
            if not userExists(idinfo["email"], "gl"):
                newuser = User(
                    auth_type="gl",
                    first_name=idinfo["given_name"],
                    last_name=idinfo["family_name"],
                    email=idinfo["email"],
                    picture=idinfo["picture"],
                    auth_token=idinfo["sub"]
                )
                connectDB()
                session.add(newuser)
                session.commit()
                session.close()
            login_session["username"] = idinfo["email"]
            login_session["logged_in"] = True
            login_session["auth_type"] = "gl"
            connectDB()
            query = session.query(User.id).filter(
                User.email == idinfo["email"], User.auth_type == "gl").scalar()
            session.close()
            return showCollection(query)
        except ValueError:
            return "Invalid token"


# process facebook oauth2 response
# https://developers.facebook.com/docs/facebook-login/web
@app.route("/oauth2/facebook", methods=["POST"])
def oauthFacebook():
    if request.method == "POST":
        fbinfo = json.loads(request.form['fbinfo'])
        print(fbinfo['first_name'])
        print(fbinfo['last_name'])
        print(fbinfo['email'])
        print(json.loads(fbinfo['accessToken']))
        # create native account, sub goes in User.auth_token
        if not userExists(fbinfo["email"], "fb"):
            newuser = User(
                auth_type="fb",
                first_name=fbinfo["first_name"],
                last_name=fbinfo["last_name"],
                email=fbinfo["email"],
                auth_token=json.loads(fbinfo["accessToken"])["accessToken"]
            )
            connectDB()
            session.add(newuser)
            session.commit()
            session.close()
        login_session["username"] = fbinfo["email"]
        login_session["logged_in"] = True
        login_session["auth_type"] = "fb"
        connectDB()
        query = session.query(User.id).filter(
            User.email == fbinfo["email"], User.auth_type == "fb").scalar()
        session.close()
        return showCollection(query)


if __name__ == "__main__":
    app.secret_key = "super_secret_key"
    app.debug = True
    # app.run(host="0.0.0.0", port=8000)
    app.run(host='0.0.0.0', port=8000, ssl_context=('cert.pem', 'key.pem'))
