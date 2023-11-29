"""Blogly application."""
""" First create db before running app.py"""

from flask import Flask, request, redirect, render_template
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


app.config['SECRET_KEY'] = "SECRET!"
debug = DebugToolbarExtension(app)

app.app_context().push()
connect_db(app)


@app.route("/")
def home():
    """redirects to users."""

    
    return redirect("/users")

@app.route("/users")
def show_users():
    """shows list of all users"""

    users = User.query.all()
    return render_template("list.html", users=users)


@app.route("/<int:user_id>")
def show_user(user_id):
    """Show info on a single User."""

    user = User.query.get_or_404(user_id)
    return render_template("detail.html", user=user)


@app.route("/users/new", methods=["GET"])
def new_user_form():
    """shows form to create new user"""

    return render_template("new.html")

@app.route("/users/new", methods=["POST"])
def new_user():
    """Handle submission form to create a new user"""

    new_user = User(
        first_name=request.form.get('first_name', False),
        last_name=request.form.get('last_name', False),
        image_url=request.form.get('image_url', False) or None)

    db.session.add(new_user)
    db.session.commit()


    return redirect("/users")


@app.route("/users/<int:user_id>/delete", methods=["POST"])
def delete_user(user_id):
    """Deletes the user"""

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()

    return redirect("/users")


@app.route("/users/<int:user_id>/edit")
def edit_user_form(user_id):
    """shows the form to edit a users info"""

    user = User.query.get_or_404(user_id)
    
    return render_template("edit.html", user=user)


@app.route("/users/<int:user_id>/edit", methods=["POST"])
def edit_user(user_id):
    """edits the users info"""

    user = User.query.get_or_404(user_id)
    user.first_name = request.form['first_name']
    user.last_name = request.form['last_name']
    user.image_url = request.form['image_url']

    db.session.add(user)
    db.session.commit()

    return redirect("/users")



