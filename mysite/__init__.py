import os
from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
import sshtunnel

app = Flask(__name__)
tunnel = sshtunnel.SSHTunnelForwarder(
        ('ssh.pythonanywhere.com'), ssh_username='ahh1539', ssh_password='fvTSYgh$HzB7J23',
        remote_bind_address=('ahh1539.mysql.pythonanywhere-services.com', 3306)
    )
tunnel.start()
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://ahh1539:g3gd@XEbiU7H7Ri@127.0.0.1:{}/ahh1539$pyanywhere_tigerplace'.format(tunnel.local_bind_port)

app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = 'mysite/static/'
app.secret_key = 'super secret key'

db = SQLAlchemy(app)



class User(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, db.Sequence('seq_reg_id', start=1, increment=1),
              primary_key=True)
    email = db.Column(db.String(100))
    password = db.Column(db.String(500))
    full_name = db.Column(db.String(100))
    phone_number = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=db.func.now())
    deleted_at = db.Column(db.DateTime)

class Item(db.Model):
    __tablename__ = 'items'
    item_id = db.Column(db.Integer, db.Sequence('seq_reg_id', start=1, increment=1),
              primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.String(100))
    description = db.Column(db.String(500))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    img_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=db.func.now())
    deleted_at = db.Column(db.DateTime)


@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    # print('tunnel: ', tunnel, ' db: ', db)
    if request.method == 'POST':
        print(request.form)
        user = User.query.filter(User.email == request.form['username']).all()
        if user and check_password_hash(user[0].password, request.form['password']):
            session['user_id'] = user[0].user_id
            return redirect(url_for('index'))
        error = "Invalid Credentials"
    return render_template("login.html", error=error)


@app.route('/signup_confirmation', methods=['POST'])
def signup_confirmation():
    email = request.form['email']
    password = request.form['password']
    phone_number = request.form['phone_number']
    full_name = request.form['full_name']
    if 'rit.edu' in email:
        user = User(email=email, password=generate_password_hash(password), full_name=full_name, phone_number=phone_number)
        db.session.add(user)
        db.session.commit()
        return render_template("sign-up-confirm.html")
    return 'Cannot make an account for you at this time'

@app.route('/about')
def about():
    if session.get('user_id'):
        pass
    else:
        return redirect(url_for('login'))
    return render_template("about.html")


@app.route('/home')
def index():
    if session.get('user_id'):
        pass
    else:
        return redirect(url_for('login'))
    items = Item.query.all()
    return render_template("index.html", res=items)


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


@app.route('/signup')
def signup():
    return render_template("signup.html")


@app.route('/sell', methods=['GET', 'POST'])
def sell():
    if session.get('user_id'):
        pass
    else:
        return redirect(url_for('login'))
    return render_template("sell.html")


@app.route('/sell_item', methods=['GET', 'POST'])
def sell_item():
    if session.get('user_id'):
        pass
    else:
        return redirect(url_for('login'))
    if request.method == 'POST':
        fileName = None
        Item_Name = request.form['Item_Name']
        Price = request.form['Price']
        Description = request.form['Description']

        if 'pic' not in request.files:
            print('there is no file1 in form!')
        else:
            file1 = request.files['pic']
            print(app.config['UPLOAD_FOLDER'], 'heheheheh', file1.filename, request.files)
            path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
            file1.save(path)
            fileName = file1.filename
            print(path)

        item = Item(name=Item_Name, price=Price, description=Description, user_id=session.get('user_id'), img_path=fileName )
        db.session.add(item)
        db.session.commit()
        return render_template("created.html")


@app.route('/expanded-card/<item_id>', methods=['GET', 'POST'])
def expanded_card(item_id):
    item = None
    if session.get('user_id'):
        pass
    else:
        return redirect(url_for('login'))
    if item_id:
        item = Item.query.filter(Item.item_id == item_id).one()
        user = User.query.filter(User.user_id == item.user_id).one()
        return render_template("card-expanded.html", item=item, user=user)



def check_signed_in():
    if session.get('user_id'):
        pass
    else:
        return redirect(url_for('login'))

