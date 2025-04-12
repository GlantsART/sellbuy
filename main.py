from flask import Flask, redirect, render_template
from data import db_session
from data.users import User
from data.offers import Offers
from flask_login import LoginManager, login_user, logout_user, login_required
from form.login_form import LoginForm
from form.user import RegisterForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ArTem_GlaNTs2008'
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/database.db")

    app.run(port=8080, host='127.0.0.1')


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/main')
def main_page():
    return render_template('main.html', title='Главная страница')


@app.route('/all_offers')
def all_offers():
    db_sess = db_session.create_session()
    all_offers = list(set(db_sess.query(Offers).filter(Offers.is_sold == 0)))
    return render_template('all_offers_page.html', title='Все предложения', offers=all_offers)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            surname=form.surname.data,
            email=form.email.data,
            number=form.number.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        print('#########', user)
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/main')
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/main")


@app.route('/about')
def about_inf():
    return render_template('about.html', title='Инфо о сайте')


if __name__ == '__main__':
    main()
