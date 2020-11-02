import sshtunnel
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
Bootstrap(app)

# for running locally
# tunnel = sshtunnel.SSHTunnelForwarder(
#     ('ssh.pythonanywhere.com'), ssh_username='ahh1539', ssh_password='fvTSYgh$HzB7J23',
#     remote_bind_address=('ahh1539.mysql.pythonanywhere-services.com', 3306)
# )
# tunnel.start()
# app.config[
#     'SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://ahh1539:g3gd@XEbiU7H7Ri@127.0.0.1:{}/ahh1539$pyanywhere_tigerplace'.format(
#     tunnel.local_bind_port)

# uncomment before pushing to master
SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
    username="ahh1539",
    password="g3gd@XEbiU7H7Ri",
    hostname="ahh1539.mysql.pythonanywhere-services.com",
    databasename="ahh1539$pyanywhere_tigerplace",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI


app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = 'mysite/static/images/'
app.secret_key = 'super secret key'
db = SQLAlchemy(app)

from mysite import views
