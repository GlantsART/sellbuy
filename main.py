from flask import Flask, redirect, render_template, request, abort, url_for
from data import db_session
from data.users import User
from data.offers import Offers
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from form.login_form import LoginForm
from form.user import RegisterForm
from PIL import Image
import os

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
        os.mkdir(f'static/img/{user.id}')
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    db_sess = db_session.create_session()
    form = LoginForm()
    if form.validate_on_submit():
        user = db_sess.query(User).filter(User.email == form.email.data).first()
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
    topics_name = ['животные', 'электроника', 'транспорт', 'еда', 'для дома', 'аксессуары', 'услуги',
                   'запчасти',
                   'одежда', 'недвижимость', 'Книги', 'Спорт товары']
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    if request.method == 'POST':
        topics = []
        for i in range(12):
            try:
                topics.append(request.form[f'accept{i}'])
            except:
                continue
        offers = Offers()
        offers.name_offer = request.form['name']
        offers.discription = request.form['about']
        offers.price = request.form['price']
        offers.topic = ', '.join(topics)
        offers.place = request.form['place']

        file = request.files['file']
        file_name = file.filename
        file.save(f'static/img/{user.id}/{file_name}')
        file = Image.open(f'static/img/{user.id}/{file_name}')
        file = file.resize((200, 200))
        file.save(f'static/img/{user.id}/{file_name}')
        offers.photo = f'static/img/{user.id}/{file_name}'

        current_user.offers.append(offers)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/my_offers')
    return render_template('add_offer.html', title='Добавление предложения', topics_name=topics_name)


@app.route('/torfin')
def torfin():
    return f'''<img src="{url_for('static', filename='img/torfin.png')}" alt="Картинки нет">'''


@app.route('/change_offers/<int:id>', methods=['GET', 'POST'])
@login_required
def change_offer(id):
    topics_name = ['животные', 'электроника', 'транспорт', 'еда', 'для дома', 'аксессуары', 'услуги',
                   'запчасти',
                   'одежда', 'недвижимость', 'Книги', 'Спорт товары']
    if request.method == "GET":
        db_sess = db_session.create_session()
        offers = db_sess.query(Offers).filter(Offers.id == id, Offers.user == current_user).first()
        if offers:
            offer_name = offers.name_offer
            discription = offers.discription
            price = offers.price
            topic = offers.topic.split(', ')
            place = offers.place
            return render_template('add_offer.html', title='Редактирование предложения', name_offer=offer_name,
                                   discription=discription, price=price, topic=topic, place=place,
                                   topics_name=topics_name)
        else:
            abort(404)
    if request.method == 'POST':
        db_sess = db_session.create_session()
        offers = db_sess.query(Offers).filter(Offers.id == id, Offers.user == current_user).first()
        if offers:
            topics = []
            for i in range(12):
                try:
                    topics.append(request.form[f'accept{i}'])
                except:
                    continue
            offers.name_offer = request.form['name']
            offers.discription = request.form['about']
            offers.price = request.form['price']
            offers.topic = ', '.join(topics)
            offers.place = request.form['place']
            db_sess.commit()
            return redirect('/my_offers')
        else:
            abort(404)


@app.route('/search', methods=['POST', 'GET'])
def search():
    topics_name = ['животные', 'электроника', 'транспорт', 'еда', 'для дома', 'аксессуары', 'услуги',
                   'запчасти',
                   'одежда', 'недвижимость', 'книги', 'спорт товары']
    if request.method == 'GET':
        db_sess = db_session.create_session()
        places = [str(str(elem)[2:-3]) for elem in set(db_sess.query(Offers.place).filter(Offers.is_sold == 0))]
        return render_template('search.html', title='Поиск предложений', topics_name=topics_name, place_list=places,
                               cplaces=len(places))
    elif request.method == 'POST':
        search_name = request.form['text_area']
        topics = request.form['topic']
        placea = request.form['place']
        min_price = int(request.form['min_price'])
        max_price = int(request.form['max_price'])
        db_sess = db_session.create_session()
        offers = list(db_sess.query(Offers).filter(Offers.is_sold == 0, Offers.user != current_user))
        if search_name != '':
            new_offers = []
            for item in offers:
                if search_name.lower() in item.name_offer.lower():
                    new_offers.append(item)
            offers = new_offers.copy()
            new_offers.clear()
        if topics != 'Нет':
            new_offers = []
            for item in offers:
                if topics in item.topic:
                    new_offers.append(item)
            offers = new_offers.copy()
            new_offers.clear()
        if placea != 'Нет':
            new_offers = []
            for item in offers:
                if placea in item.place:
                    new_offers.append(item)
            offers = new_offers.copy()
            new_offers.clear()
        new_offers = []
        for item in offers:
            if min_price <= int(item.price) <= max_price:
                new_offers.append(item)
            offers = new_offers.copy()

        if offers:
            return render_template('searched_offers.html', title='Предложения', offers=offers, text='Предложения')
        else:
            return render_template('no_offers.html', title='Предложения')





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


@app.route('/delete_basket/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_basket(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    lst = user.basket.split()
    lst.remove(str(id))
    user.basket = ' '.join(lst)
    db_sess.commit()
    return redirect('/basket')


@app.route('/add_basket/<int:id>', methods=['GET', 'POST'])
@login_required
def offer_basket(id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    if user and id not in [int(i) for i in user.basket.split()]:
        user.basket += str(id) + ' '
        db_sess.commit()
    return redirect('/main')


@app.route('/basket', methods=['GET', 'POST'])
@login_required
def basket():
    db_sess = db_session.create_session()
    offers_id = [int(i) for i in current_user.basket.split()]
    offers = db_sess.query(Offers).all()
    offers_basket = []
    for item in offers:
        if item.id in offers_id:
            offers_basket.append(item)
    return render_template('/searched_offers.html', title='Корзина', offers=offers_basket, text='Корзина')


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
