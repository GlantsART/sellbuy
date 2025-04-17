from flask import Flask, redirect, render_template, request, abort
from data import db_session
from data.users import User
from data.offers import Offers
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from form.login_form import LoginForm
from form.user import RegisterForm
from form.OffersForm import OfferForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ArTem_GlaNTs2008'
login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db_session.global_init("db/database.db")

    app.run(port=8080, host='127.0.0.1', debug=True)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/main')
def main_page():
    db_sess = db_session.create_session()
    all_offers = list(set(db_sess.query(Offers).filter(Offers.is_sold == 0)))
    return render_template('main.html', title='Главная страница', offers=all_offers)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    db_sess = db_session.create_session()
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
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
    db_sess = db_session.create_session()
    form = LoginForm()
    if form.validate_on_submit():
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


@app.route('/my_offers')
def my_offers_page():
    db_sess = db_session.create_session()
    offers = db_sess.query(Offers).filter(Offers.user == current_user)
    return render_template('my_offers.html', title='Мои предложения', offers=offers)


@app.route('/add_offer', methods=['GET', 'POST'])
def add_offer():
    form = OfferForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        offers = Offers()
        offers.name_offer = form.name_offer.data
        offers.discription = form.discription.data
        offers.price = form.price.data
        offers.topic = form.topic.data
        offers.place = form.place.data
        current_user.offers.append(offers)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/my_offers')
    return render_template('add_offers.html', title='Добавление предложения', form=form)


@app.route('/change_offers/<int:id>', methods=['GET', 'POST'])
@login_required
def change_offer(id):
    form = OfferForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        offers = db_sess.query(Offers).filter(Offers.id == id, Offers.user == current_user).first()
        if offers:
            form.name_offer.data = offers.name_offer
            form.discription.data = offers.discription
            form.price.data = offers.price
            form.topic.data = offers.topic
            form.place.data = offers.place
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        offers = db_sess.query(Offers).filter(Offers.id == id, Offers.user == current_user).first()
        if offers:
            offers.name_offer = form.name_offer.data
            offers.discription = form.discription.data
            offers.price = form.price.data
            offers.topic = form.topic.data
            offers.place = form.place.data
            db_sess.commit()
            return redirect('/my_offers')
        else:
            abort(404)
    return render_template('add_offers.html', title='Редактирование предложения', form=form)


@app.route('/search', methods=['POST', 'GET'])
def search():
    if request.method == 'GET':
        db_sess = db_session.create_session()
        topics = list(set(db_sess.query(Offers.topic).filter(Offers.is_sold == 0)))
        return render_template('search.html', title='Поиск предложений', topics=topics)
    elif request.method == 'POST':
        search_name = request.form['text_area']
        if search_name != '':
            db_sess = db_session.create_session()
            offers = list(db_sess.query(Offers).filter(Offers.name_offer.contains(search_name)), Offers.is_sold == 0)
            print()
            if offers:
                return render_template('searched_offers.html', title='Отобранные предложения', offers=offers)
            else:
                return render_template('no_offers.html', title='Отобранные предложения')
        else:
            return render_template('no_offers.html', title='Отобранные предложения')


@app.route('/offer_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def offer_delete(id):
    db_sess = db_session.create_session()
    offer = db_sess.query(Offers).filter(Offers.id == id, Offers.user == current_user).first()
    if offer:
        db_sess.delete(offer)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/my_offers')


@app.route('/offer_sold/<int:id>', methods=['GET', 'POST'])
@login_required
def offer_sold(id):
    db_sess = db_session.create_session()
    offer = db_sess.query(Offers).filter(Offers.id == id, Offers.user == current_user).first()
    if offer:
        offer.is_sold = True
        db_sess.commit()
    else:
        abort(404)
    return redirect('/my_offers')


@app.route('/offer_not_sold/<int:id>', methods=['GET', 'POST'])
@login_required
def offers_not_sold(id):
    db_sess = db_session.create_session()
    offer = db_sess.query(Offers).filter(Offers.id == id, Offers.user == current_user).first()
    if offer:
        offer.is_sold = False
        db_sess.commit()
    else:
        abort(404)
    return redirect('/my_offers')


if __name__ == '__main__':
    main()
