"""Blogly application."""
""" First create db before running app.py"""

from flask import Flask, request, redirect, render_template
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag

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

    users = User.query.order_by(User.last_name, User.first_name).all()
    tags = Tag.query.all()
    posts = Post.query.all()

    return render_template("list.html", users=users, tags=tags, posts=posts)


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

####################################################################################
# Posts route

@app.route("/users/<int:user_id>/posts/new", methods=["GET"])
def show_post_form(user_id):
    """shos the form to make a post"""

    user = User.query.get_or_404(user_id)
    tags = Tag.query.all()
    return render_template("new_post.html", user=user, tags=tags)


@app.route("/users/<int:user_id>/posts/new", methods=["POST"])
def post_form(user_id):
    """Handles the add form and redirects to user detail page"""

    user = User.query.get_or_404(user_id)
    tag_ids = [int(num) for num in request.form.getlist("tags")]
    tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

    new_post = Post(title=request.form['title'],
                    content=request.form['content'],
                    user=user, tags=tags)
    
    db.session.add(new_post)
    db.session.commit()

    return redirect(f"/{user_id}")



@app.route("/posts/<int:post_id>")
def show_post(post_id):
    """shows users post"""

    post = Post.query.get_or_404(post_id)
    return render_template("post.html", post=post)


@app.route("/posts/<int:post_id>/edit")
def show_edit_post_form(post_id):
    """shows form to edit a post"""

    post = Post.query.get_or_404(post_id)
    tags = Tag.query.all()
    return render_template("edit_post.html", post=post, tags=tags)


@app.route("/posts/<int:post_id>/edit", methods=['GET', 'POST'])
def update_post(post_id):
    """handles for submission for updating an existing post"""

    post = Post.query.get_or_404(post_id)
    post.title = request.form['title']
    post.content = request.form['content']

    tag_ids = [int(num) for num in request.form.getlist("tags")]
    post.tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()

    db.session.add(post)
    db.session.commit()

    return redirect(f"/{post.user_id}")

@app.route('/posts/<int:post_id>/delete')
def posts_destroy(post_id):
    """deletes an existing post"""

    post = Post.query.get_or_404(post_id)

    db.session.delete(post)
    db.session.commit()
    

    return redirect(f"/{post.user_id}")

####################################################################
# Tag Route
@app.route('/tags')
def tags_index():
    """Show a page with info on all tags"""

    tags = Tag.query.all()
    return render_template('tag_index.html', tags=tags)


@app.route('/tags/new')
def tags_new_form():
    """Shows form to create a new tag"""

    posts = Post.query.all()

    return render_template('new_tag.html', posts=posts)


@app.route("/tags/new", methods=["POST"])
def tags_new():
    """Handle form submission for creating a new tag"""

    post_ids = [int(num) for num in request.form.getlist("posts")]
    posts = Post.query.filter(Post.id.in_(post_ids)).all()
    new_tag = Tag(name=request.form['name'], posts=posts)

    db.session.add(new_tag)
    db.session.commit()

    return redirect("/tags")



@app.route('/tags/<int:tag_id>')
def tags_show(tag_id):
    """Show page with info on a certain tag"""

    tag = Tag.query.get_or_404(tag_id)
    return render_template('tags_show.html', tag=tag)


@app.route('/tags/<int:tag_id>/edit')
def tags_edit_form(tag_id):
    """Show a form to edit an existing tag"""

    tag = Tag.query.get_or_404(tag_id)
    posts = Post.query.all()
    return render_template('tags_edit.html', tag=tag, posts=posts)


@app.route('/tags/<int:tag_id>/edit', methods=["POST"])
def tags_edit(tag_id):
    """Handle form submission for updating an existing tag"""

    tag = Tag.query.get_or_404(tag_id)
    tag.name = request.form['name']
    post_ids = [int(num) for num in request.form.getlist("posts")]
    tag.posts = Post.query.filter(Post.id.in_(post_ids)).all()

    db.session.add(tag)
    db.session.commit()

    return redirect("/tags")

@app.route('/tags/<int:tag_id>/delete', methods=["POST"])
def tags_destroy(tag_id):
    """Handle form submission for deleting an existing tag"""

    tag = Tag.query.get_or_404(tag_id)
    db.session.delete(tag)
    db.session.commit()

    return redirect("/tags")
