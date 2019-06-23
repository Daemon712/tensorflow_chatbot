from flask_wtf import FlaskForm
from werkzeug.urls import url_parse
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask_login import UserMixin, logout_user
from app import login, app
from flask import redirect, flash, url_for, request, render_template
from flask_login import current_user, login_user


class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class Admin(UserMixin):
    def __init__(self):
        self.id = 'admin'
        self.password = '123456'

    def check_credentials(self, name, password):
        return name == self.id and password == self.password


@login.user_loader
def load_user(id):
    return Admin() if id == 'admin' else None


@app.errorhandler(401)
def page_not_found(e):
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Admin()
        if not user.check_credentials(name=form.username.data, password=form.password.data):
            flash('Неверный логин пользователя или пароль')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('dashboard'))
    return render_template('login.html',form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))