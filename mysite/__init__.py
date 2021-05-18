import sshtunnel
from datetime import timedelta
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
Bootstrap(app)

f=open("mysite/sensitive.txt","r")
lines=f.readlines()
username = lines[0].strip('\n')
ssh_password = lines[1].strip('\n')
db_password = lines[2].strip('\n')
db_name = lines[3].strip('\n')
hostname = lines[4].strip('\n')
connection_port = int(lines[5].strip('\n'))
ssh_connection_string = lines[6].strip('\n')
test_env = lines[7].strip('\n')
secret_key = lines[8].strip('\n')
img_upload_path = lines[9].strip('\n')

f.close()


# for running locally, need paid account
# https://help.pythonanywhere.com/pages/AccessingMySQLFromOutsidePythonAnywhere/

if test_env == 'True':
    tunnel = sshtunnel.SSHTunnelForwarder(
        (ssh_connection_string), ssh_username=username, ssh_password=ssh_password,
        remote_bind_address=(hostname, connection_port)
    )
    tunnel.start()
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://{username}:{db_password}@127.0.0.1:{local_bind_port}/{db_name}'.format(
        username=username,
        db_password=db_password,
        db_name=db_name,
        local_bind_port=tunnel.local_bind_port
    )
else:
    SQLALCHEMY_DATABASE_URI = "mysql+mysqlconnector://{username}:{password}@{hostname}/{databasename}".format(
        username=username,
        password=db_password,
        hostname=hostname,
        databasename=db_name,
    )
    app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI


app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = img_upload_path
app.secret_key = secret_key
app.permanent_session_lifetime = timedelta(minutes=30)

db = SQLAlchemy(app)

from mysite import views
