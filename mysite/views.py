import os
import datetime

from flask import abort, render_template, redirect, url_for, request, session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

import requests
from google.oauth2 import id_token
from pip._vendor import cachecontrol
import google.auth.transport.requests

from mysite import app, flow, GOOGLE_CLIENT_ID
from mysite.db import User, Item, db


@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('user_id'):
        return redirect(url_for('index'))
    error = None
    if request.method == 'POST':
        user = User.get_by_email(request.form['username'])
        if user and check_password_hash(user.password, request.form['password']):
            session.permanent = True
            session['user_id'] = user.user_id
            session['name'] = user.full_name
            session['ia'] = user.is_admin
            print(session['name'], session['user_id'])
            # flash('You were successfully logged in')
            return redirect(url_for('index'))
        error = "Invalid Credentials"
    return render_template("login.html", error=error)


@app.route('/')
def splash_page():
    if session.get('user_id'):
        return redirect(url_for('index'))
    else:
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
    return signup(error='Cannot make an account for you at this time')


@app.route('/faq')
def faq():
    return render_template("faq.html")


@app.route('/about')
def about():
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return render_template("about.html")


@app.route('/home')
def index():
    if not session.get('user_id'):
        return redirect(url_for('login'))

    items = Item.query.filter(Item.deleted_at == None).limit(12).all()
    if request.method == 'POST':  # if sent a post request via the search bar
        search_input = str(request.form['search_input'])
        items = Item.query.filter(Item.name.like('%{}%'.format(search_input)))
        return render_template("index.html", res=items, user_id=session.get('user_id'), user_name=session.get('name'))

    return render_template("index.html", res=items, user_id=session.get('user_id'), user_name=session.get('name'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/signup')
def signup(error=None):
    return render_template("signup.html", error=error)


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
        category = request.form['Category']
        if 'pic' not in request.files:
            return 'No picture found'
        else:
            file1 = request.files['pic']
            filename = secure_filename(file1.filename)
            path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file1.save(path)
            item = Item(name=item_name, price=price, description=description, category=category, user_id=session.get('user_id'),
                        img_path=str(filename))
            db.session.add(item)
            db.session.commit()
            return render_template("created.html")


@app.route('/expanded-card/<item_id>', methods=['GET', 'POST'])
def expanded_card(item_id):
    item = None
    if not session.get('user_id'):
        return redirect(url_for('login'))
    if item_id:
        try:
            item = Item.get_by_id(item_id)
            if item.deleted_at is not None and not session.get('ia'):
                return redirect(url_for('index'))
            else:
                user = User.get_by_id(item.user_id)
                suggested_items = Item.query.filter(
                    Item.item_id != item_id).limit(3).all()
                return render_template("card-expanded.html", item=item, user=user, current_usr=session.get('user_id'),
                                       suggested_items=suggested_items, is_admin=session.get('ia', False))
        except:
            return redirect(url_for('index'))


@app.route('/delete-item/<item_id>', methods=['GET', 'POST'])
def delete_item(item_id):
    item = Item.get_by_id(item_id)
    if session.get('user_id') == item.user_id or session.get('ia') == True:
        now = datetime.datetime.utcnow()
        item.deleted_at = now.strftime('%Y-%m-%d %H:%M:%S')
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return redirect(url_for('expanded-card'))


@app.route('/admin/delete/<item_id>', methods=['GET', 'POST'])
def admin_hard_delete(item_id):
    item = Item.get_by_id(item_id)
    if session.get('ia') == True:
        os.remove(app.config['UPLOAD_FOLDER'] + '{}'.format(item.img_path))
        db.session.delete(item)
        db.session.commit()
        return redirect(url_for('index'))
    else:
        return redirect(url_for('expanded-card'))


@app.route('/profile/<user_id>', methods=['GET', 'POST'])
def profile_page(user_id):
    if int(session.get('user_id')) == int(user_id):
        deleted_items = None
        user = User.get_by_id(int(user_id))
        user_items = Item.query.filter(
            Item.user_id == user.user_id, Item.deleted_at == None).all()
        if session.get('ia'):
            deleted_items = Item.query.filter(
                Item.deleted_at != None).limit(5).all()
        return render_template("profile_page.html", user=user, items=user_items, deleted_items=deleted_items)
    else:
        return redirect(url_for('index'))


@app.route('/edit-post/<item_id>', methods=['GET', 'POST'])
def verify_update(item_id):
    if item_id:
        try:
            item_to_edit = Item.query.filter(Item.item_id == item_id, Item.user_id == session.get(
                'user_id'), Item.deleted_at == None).one()
            return render_template("edit-post.html", item_to_edit=item_to_edit, user_id=session.get('user_id'))
        except:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


@app.route('/submit-edit/<item_id>', methods=['GET', 'POST'])
def update_item(item_id):
    if not session.get('user_id'):
        return redirect(url_for('login'))
    if request.method == 'POST':
        user_id = request.form['User_Id']
        updated_item_name = request.form['Item_Name']
        updated_price = request.form['Price']
        updated_description = request.form['Description']
        updated_category = request.form['Category']
        if int(session.get('user_id')) == int(user_id):
            item_to_update = Item.query.filter(
                Item.user_id == user_id, Item.item_id == item_id).one()
            item_to_update.name = updated_item_name
            item_to_update.price = updated_price
            item_to_update.description = updated_description
            item_to_update.category = updated_category
            db.session.commit()
            return redirect(url_for('index'))
    return redirect(url_for('index'))


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html")


@app.route("/google-login")
def google_login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)


@app.route("/login/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(
        session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    session["email"] = id_info.get("email")
    user = User.get_by_email(session["email"])
    if not user:
        user = User(email=session.get("email"), password=generate_password_hash("google"), full_name=session.get("name"),
                    phone_number=None)
        db.session.add(user)
        db.session.commit()
        last_user = User.query.order_by(User.user_id.desc()).first()
        session["user_id"] = last_user.user_id
    else:
        session['ia'] = user.is_admin
        session["user_id"] = user.user_id
    return redirect(url_for('index'))
