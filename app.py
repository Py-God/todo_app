from datetime import datetime, timedelta
from flask import (
    abort,
    Flask,
    redirect,
    request,
    render_template,
    session
    )
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from helper import login_required
import re
from sqlalchemy import desc, func, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from werkzeug.security import generate_password_hash, check_password_hash

class Base(DeclarativeBase):
    pass

naming_convention = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(column_0_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
db = SQLAlchemy(metadata=MetaData(naming_convention=naming_convention))

# configure app name
app = Flask(__name__)

# configure the SQLite database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///taskhero.db"

# initialize the app with the extension
db.init_app(app)

migrate = Migrate(app, db, render_as_batch=True)

class User(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)
    email: Mapped[str] = mapped_column(unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(nullable=False)
    task = db.relationship('Task', backref='user', cascade='all, delete, delete-orphan')

    def __repr__(self):
        return f"<User {self.id}>"
    

class Task(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(unique=True, nullable=False)
    time: Mapped[str] = mapped_column(nullable=False)
    date: Mapped[str] = mapped_column(nullable=False)
    status: Mapped[bool] = mapped_column(nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"<Task {self.id}>"
    
    
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


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    session.clear()

    return redirect("/login")
    

@app.route("/")
@login_required
def index():
    tasks = db.session.execute(db.select(Task).order_by(desc(Task.id))).scalars()

    return render_template("index.html", tasks=tasks)


@app.route("/add_task", methods=["GET", "POST"])
@login_required
def add_task():
    if request.method == "POST":
        task_name = request.form.get("task_name")

        if not task_name:
            abort(400, "Invalid Task Name")

        time = datetime.strftime(datetime.now(), "%I:%M %p")
        date = datetime.strftime(datetime.now(), "%Y-%m-%d")

        new_task = Task(name=task_name, time=time, date=date, status=False, user_id=session["user_id"])
        db.session.add(new_task)
        db.session.commit()

        return redirect("/")

    else:
        return render_template("add_task.html")
    

@app.route("/edit_task", methods=["GET", "POST"])
@login_required
def edit_task():
    if request.method == "POST":
        ...
    else:
        ...


@app.route("/delete_task", methods=["GET", "POST"])
@login_required
def delete_task():
    if request.method == "POST":
        id = request.form.get("id")
        task = db.one_or_404(db.select(Task).filter_by(id=id))

        db.session.delete(task)
        db.session.commit()

        return redirect("/")
    else:
        abort(404, "Delete task page not found")


def get_last_user_id():
    last_user_id = db.session.query(func.max(User.id)).scalar()
    if last_user_id is None:
        return 0
    else:
        return last_user_id
    

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}