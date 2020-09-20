from flask import Flask, render_template, request, redirect, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime
import sqlite3
from login_required import login_required
from os import path
# Configurations
# Flask Configurations
app = Flask(__name__)
ROOT = path.dirname(path.realpath(__file__))

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key ="roflhahasomuchfun"



# Database Configurations
connect = sqlite3.connect(path.join(ROOT, "sse.db"))
db = connect.cursor()

def listify (obj):
    """makes the output of the database SELECT as a list contains a dictionary"""
    keys = []
    lis = []
    for i, n in enumerate(db.description):
        keys.append(n[0])
    for item in obj:
        lis.append({keys[i]: item[i] for i in range(len(item))})
    return lis

# def lookfor (lis_in):
#     lis = []
#     lis_in = listify(lis_in)
#     for l in lis_in:
#         for val in l.values():
#             lis.append(val)
#     return lis


# Routes
@app.route("/")
# @login_required
def index():
    return render_template("index.html")


@app.route("/register", methods =["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        repassword = request.form.get("repassword")
        if username == "":
            return render_template("register.html", message = "Please enter your username")
        if len(username) < 5:
            return render_template("register.html", message = "Username cannot be less than 5 characters")
        user_data_list =  listify(db.execute("SELECT user_id, username, hash FROM users WHERE username =:username", {"username":username}))
        if len(user_data_list) != 0:
            return render_template("register.html", message = "Username already exist!")
        if password == "":
            return render_template("register.html", message = "Please enter your password", username = username)
        if len(password) < 6:
            return render_template("register.html", message = "password cannot be less than 6 characters", username = username)
        if repassword == "":
            return render_template("register.html", message = "Please enter your password confirmation", username = username)
        if repassword != password:
            return render_template("register.html", message = "passwords does not match", username = username)
        db.execute("INSERT INTO users (username, hash) VALUES(:username, :password)", {"username":username, "password": generate_password_hash(password)})
        connect.commit()
        user_data_list =  listify(db.execute("SELECT user_id, username FROM users WHERE username =:username", {"username":username}))
        session["user_id"] = user_data_list[0]["user_id"]
        session["user_username"] = user_data_list[0]["username"]
        session["state"] = False
        session["tag"] = False
        session["chat_id"] = False
        session["chatter_id"] = ""
        session["message"] = ""
        session["theme"] = listify(db.execute("SELECT theme FROM users WHERE user_id = :user_id", {"user_id":session["user_id"]}))[0]["theme"]

        connect.commit()
        return redirect("/home")

@app.route("/login", methods =["GET","POST"])
def login():
    [session.pop(key) for key in list(session.keys()) if key != 'theme']
    if request.method == "GET":
        return render_template("login.html")
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "":
            return render_template("login.html", message = "Please enter your username")
        if password == "":
            return render_template("login.html", message = "Please enter your password", username = username)
        user_data_list =  listify(db.execute("SELECT user_id, username, hash FROM users WHERE username =:username", {"username":username}))
        if len(user_data_list) == 0:
            return render_template("login.html", message = "username is not found")
        if not check_password_hash(user_data_list[0]["hash"], password) :
            return render_template("login.html", message = "wrong password",username = username)
        session["user_id"] = user_data_list[0]["user_id"]
        session["user_username"] = user_data_list[0]["username"]
        session["state"] = False
        session["tag"] = False
        session["chat_id"] = False
        session["chatter_id"] = ""
        session["message"] = ""
        session["theme"] = listify(db.execute("SELECT theme FROM users WHERE user_id = :user_id", {"user_id":session["user_id"]}))[0]["theme"]
        connect.commit()
        return redirect("/home")


@app.route("/logout")
@login_required
def logout():
    [session.pop(key) for key in list(session.keys()) if key != 'theme']
    return redirect("/")


tags = ["Books", "Lecture Notes", "Lab Instruments", "Clothes", "Videos", "Devices"]

@app.route("/post",  methods =["POST"])
@login_required
def post():
        post_text = request.form.get("post")
        tag = request.form.get("tag")
        if post_text == "":
            session["message"] = "Please Enter your post"
            return redirect("/home")
        if len(post_text) < 10:
            session["message"] = "The post can not be less than 10 characters"
            return redirect("/home")
        if tag == None:
            session["message"] = "Please choose the tag"
            return redirect("/home")
        db.execute("INSERT INTO posts (post, poster, date, tag) VALUES (:post, :poster, :date, :tag)", {"post" : post_text, "poster" : session["user_id"], "date":datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "tag":tag})
        connect.commit()
        return redirect("/home")


@app.route("/home", methods = ["POST", "GET"])
@login_required
def home():
    state = 0
    tag = "All"
    if session["state"]:
        state = session["state"]
    if session["tag"]:
        tag = session["tag"]
    if request.method == "GET":
        print(session["theme"])
        if tag == "All" and state == "All":
            post_data_list =  listify(db.execute("SELECT post_id, post, poster, username, date, tag, state FROM posts JOIN users ON posts.poster = users.user_id ORDER BY date DESC"))
        elif tag == "All":
            post_data_list =  listify(db.execute("SELECT post_id, post, poster, username, date, tag, state FROM posts JOIN users ON posts.poster = users.user_id WHERE state = :state ORDER BY date DESC", {"state":state}))
        elif state == "All":
            post_data_list =  listify(db.execute("SELECT post_id, post, poster, username, date, tag, state FROM posts JOIN users ON posts.poster = users.user_id WHERE tag = :tag ORDER BY date DESC", {"tag":tag}))
        else:
            post_data_list =  listify(db.execute("SELECT post_id, post, poster, username, date, tag, state FROM posts JOIN users ON posts.poster = users.user_id WHERE state = :state AND tag = :tag ORDER BY date DESC", {"state":state, "tag":tag}))
        username = listify(db.execute("SELECT username FROM users WHERE user_id = :user_id" ,{"user_id":session["user_id"]}))[0]["username"]
        connect.commit()
        return render_template("home.html", username = username, user_id = session['user_id'],  post_list = post_data_list, tags = tags, selected_tag = tag, selected_state = state, message = session["message"])
    else:
        session["tag"] = request.form.get("tag")
        session["state"] = request.form.get("state")
        return redirect("/home")

@app.route("/take", methods = ["POST"])
@login_required
def take():
    post_id = request.form.get("take_btn")
    db.execute("UPDATE posts SET receiver = :receiver, state = 1 WHERE post_id = :post_id", {"receiver": session["user_id"], "post_id":post_id})
    post_users = listify(db.execute("SELECT poster, receiver FROM posts where post_id = :post_id",{"post_id":post_id}))
    chat_users = listify(db.execute("SELECT * FROM chats WHERE chat_poster = :session_id OR chat_receiver = :session_id", {"session_id": session["user_id"]}))
    if len(chat_users) > 0:
        if post_users[0]["poster"] == chat_users[0]["chat_poster"] and post_users[0]["receiver"] == chat_users[0]["chat_receiver"]:
            return redirect("/home")
        if post_users[0]["poster"] == chat_users[0]["chat_receiver"] and post_users[0]["receiver"] == chat_users[0]["chat_poster"]:
            return redirect("/home  ")
    db.execute("INSERT INTO chats (chat_poster, chat_receiver) VALUES(:chat_poster, :chat_receiver)", {"chat_poster": post_users[0]["poster"], "chat_receiver":post_users[0]["receiver"]})
    connect.commit()
    return redirect("/home")

@app.route("/chats", methods = ["GET", "POST"])
@login_required
def chats():
    if request.method == "GET":
        session["chatter_name"] = ""
        if session["chat_id"] == False:
            session["chat_id"] = ""
        msgs = listify(db.execute("SELECT * FROM msgs WHERE itschat = :itschat ORDER BY date DESC", {"itschat": session["chat_id"]}))
        session["chats"] = listify(db.execute("SELECT * FROM chats WHERE chat_poster = :session_id OR chat_receiver = :session_id", {"session_id": session["user_id"]}))
        others_id = []
        others_name = []
        for chat in session["chats"]:
            if chat["chat_poster"] != session["user_id"] and chat["chat_poster"] not in others_id:
                others_id.append(chat["chat_poster"])
            if chat["chat_receiver"] != session["user_id"] and chat["chat_receiver"] not in others_id:
                others_id.append(chat["chat_receiver"])
        for other_id in others_id:
            others_name.append(listify(db.execute("SELECT username FROM users WHERE user_id = :user_id", {"user_id":other_id}))[0]["username"])
        return render_template("chats.html", chats = session["chats"], others_name= others_name, chatter_name = session["chatter_name"], msgs = msgs, user_id = session["user_id"])
    else:
        session["chatter_name"] = request.form.get("chat-btn")
        print(session["chatter_name"])
        session["chatter_id"] = listify(db.execute("SELECT user_id FROM users WHERE username == :chatter_name", {"chatter_name": session["chatter_name"]}))[0]["user_id"]
        session["chat_id"] = [ch for ch in session["chats"] if (ch["chat_poster"] == session["chatter_id"]) or (ch["chat_receiver"] == session["chatter_id"])][0]["chat_id"]
        return redirect("/chats")


@app.route("/msgs", methods = ["POST"])
@login_required
def msgs():
        msg = request.form.get("msg")
        if msg == "":
            msg = "."
        db.execute("INSERT INTO msgs (sender_id,  receiver_id, itschat, date, msgtxt) VALUES(:sender_id, :receiver_id, :itschat, :date, :msgtxt)", {"sender_id": session["user_id"], "receiver_id": session["chatter_id"], "itschat": session["chat_id"], "date":datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "msgtxt": msg})
        connect.commit()
        return redirect("/chats")


@app.route("/theme", methods = ["POST"])
@login_required
def themefn():
    theme = request.form.get("change")
    if theme == "dark":
        theme = 1
    elif theme == "light":
        theme = 0
    session["theme"] = theme
    db.execute("UPDATE users SET theme = :theme WHERE user_id = :user_id",{"theme":theme, "user_id":session["user_id"]})
    connect.commit()
    return redirect (request.referrer)

@app.errorhandler(404)
def error(e):
    return render_template ("error.html"), 404

@app.errorhandler(500)
def error(e):
    return render_template ("error.html"), 500