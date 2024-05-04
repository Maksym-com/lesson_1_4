import datetime, hashlib

from flask import Blueprint, render_template, redirect, url_for, flash, request
from sqlalchemy import select
from flask_login import login_user

from app.models import User
from app.database import Session
from app.forms import RegistrationForm, LoginForm

bp = Blueprint('user', __name__)

def hash_password(password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    return hashed_password

@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        name = form.name.data
        surname = form.surname.data
        email = form.email.data
        password = form.password.data
        age = form.age.data
        with Session() as session:
            if session.query(User).filter(User.email == email).first():
                flash(f'Користувач з такою електронною адресою вже зареєстрований. Cпробуйте увійти.')
                return redirect(url_for('user.register'))
            else:
                hashed_password = hash_password(password)
                print(hashed_password)
                new_user = User(name=name, last_name=surname, email=email, password=hashed_password, age=age, date_joined=datetime.datetime.now())
                session.add(new_user)
                session.commit()
                flash("Ви успішно зарєструвались.")
                login_user(new_user)
                return redirect(url_for('default.index'))


    return render_template("user_reg.html", form=form)

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        login = form.login.data
        password = form.password.data
        with Session() as session:
            query = select(User).where(User.email == login or User.username == login)
            user = session.scalars(query).one()
            print(user)
            if user:
                if user.password == hash_password(password):
                    login_user(user)
                    return redirect(url_for("default.index"))

                else:
                    flash("Перевірте пароль.")
                    return redirect(url_for("user.login"))

            else:
                flash("Такого користувача не існує. Перевірте електронну адресу.")
                return redirect(url_for("user.login"))
    return render_template("user_log.html", form=form)
