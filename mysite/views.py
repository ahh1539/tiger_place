import os
from datetime import timedelta

from flask import render_template, redirect, url_for, request, session
from werkzeug.security import check_password_hash, generate_password_hash

from mysite import app
from mysite.db import User, Item, db


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('index'))
    error = None
    # print('tunnel: ', tunnel, ' db: ', db)
    if request.method == 'POST':
        user = User.query.filter(User.email == request.form['username']).all()
        if user and check_password_hash(user[0].password, request.form['password']):
            session.permanent = True
            app.permanent_session_lifetime = timedelta(minutes=30)
            session['user_id'] = user[0].user_id
            session['user_name'] = user[0].full_name
            print(session['user_name'], session['user_id'])
            return redirect(url_for('index'))
        error = "Invalid Credentials"
    return render_template("login.html", error=error)


@app.route('/')
def splash_page():
    return render_template("splash-page.html")


@app.route('/signup_confirmation', methods=['POST'])
def signup_confirmation():
    email = request.form['email']
    password = request.form['password']
    phone_number = request.form['phone_number']
    full_name = request.form['full_name']
    if 'rit.edu' in email:
        user = User(email=email, password=generate_password_hash(password), full_name=full_name,
                    phone_number=phone_number)
        db.session.add(user)
        db.session.commit()
        return render_template("sign-up-confirm.html")
    return 'Cannot make an account for you at this time'


@app.route('/about')
def about():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return render_template("about.html")


@app.route('/home', methods=['POST', 'GET'])
def index():
    if not session.get('user_id'):
        return redirect(url_for('login'))

    items = Item.query.all()
    if request.method == 'POST':  # if sent a post request via the search bar
        search_input = str(request.form['search_input'])
        items = Item.query.filter(Item.name.like('%{}%'.format(search_input)))
        return render_template("index.html", res=items, user_id=session.get('user_id'), user_name=session['user_name'])

    return render_template("index.html", res=items, user_id=session.get('user_id'), user_name=session['user_name'])


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/signup')
def signup():
    return render_template("signup.html")


@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return render_template("sell.html")


@app.route('/sell_item', methods=['GET', 'POST'])
def sell_item():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        file_name = None
        item_name = request.form['Item_Name']
        price = request.form['Price']
        description = request.form['Description']

        if 'pic' not in request.files:
            print('there is no file1 in form!')
        else:
            file1 = request.files['pic']
            print(app.config['UPLOAD_FOLDER'], 'heheheheh', file1.filename, request.files)
            path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
            file1.save(path)
            fileName = file1.filename
            print(path)

        item = Item(name=item_name, price=price, description=description, user_id=session.get('user_id'),
                    img_path=file_name)
        db.session.add(item)
        db.session.commit()
        return render_template("created.html")


@app.route('/expanded-card/<item_id>', methods=['GET', 'POST'])
def expanded_card(item_id):
    item = None
    if not session.get('user_id'):
        return redirect(url_for('login'))
    if item_id:
        item = Item.query.filter(Item.item_id == item_id).one()
        user = User.query.filter(User.user_id == item.user_id).one()
        suggested_items = Item.query.filter(Item.item_id != item_id).limit(3).all()
        return render_template("card-expanded.html", item=item, user=user, current_usr=session.get('user_id'),
                               suggested_items=suggested_items)


@app.route('/delete-item/<item_id>', methods=['GET', 'POST'])
def delete_item(item_id):
    item = Item.query.filter(Item.item_id == item_id).one()
    if session.get('user_id') == item.user_id:
        os.remove(app.config['UPLOAD_FOLDER'] + '{}'.format(item.img_path))
        db.session.delete(item)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return redirect(url_for('expanded-card'))


@app.route('/profile/<user_id>', methods=['GET', 'POST'])
def profile_page(user_id):
    if int(session.get('user_id')) == int(user_id):
        user = User.query.filter(User.user_id == user_id).first()
        user_items = Item.query.filter(Item.user_id == user.user_id)
        return render_template("profile_page.html", user=user, items=user_items)
    else:
        return redirect(url_for('index'))

