from flask import (
    abort,
    Flask,
    redirect,
    request,
    render_template,
    session
    )
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import re
from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# configure app name
app = Flask(__name__)

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///taskhero.db"

# initialize the app with the extension
db.init_app(app)

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)

    def __repr__(self):
        return f"<User {self.id}>"
    
    
with app.app_context():
    db.create_all()

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not email or not password or not confirm_password:
            abort(400, "Missing Fields")

        user = User.query.filter_by(email=email).first()
        if user:
            abort(400, "You have registered before")

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            abort(400, "Invalid email")

        if password != confirm_password:
            abort(400, "Passwords do not match")

        password_hash = generate_password_hash(password, method="scrypt", salt_length=16)

        last_user_id = get_last_user_id()

        username = f"Productive User {last_user_id + 1}"

        new_user = User(username=username, email=email, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()

        return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # clear session id: forget any previous user
    session.clear()

    # TODO write login logic
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        if not email or not password:
            abort(400, "Missing Fields")

        user = User.query.filter_by(email=email).first()

        if not user:
            abort(400, "You have not registered")
        
        # Ensure username exists and password is correct
        if not check_password_hash(user.password_hash, password):
            abort(400, description="Invalid password")

        # Remember which user has logged in
        session["user_id"] = user.id

        return redirect("/")

    else:
        return render_template("login.html")
    

@app.route("/")
def index():
    return "Welcome to the index page"


def get_last_user_id():
    last_user_id = db.session.query(func.max(User.id)).scalar()
    if last_user_id is None:
        return 0
    else:
        return last_user_id
    

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}