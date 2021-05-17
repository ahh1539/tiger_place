import sshtunnel
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
test_env = bool(lines[7].strip('\n'))
secret_key = lines[8].strip('\n')
img_upload_path = lines[9].strip('\n')
f.close()

print(username, ssh_password, db_password, db_name, hostname, connection_port, ssh_connection_string, test_env, secret_key, img_upload_path)

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
    username=username,
    password="g3gd@XEbiU7H7Ri",
    hostname="ahh1539.mysql.pythonanywhere-services.com",
    databasename="ahh1539$pyanywhere_tigerplace",
)
app.config["SQLALCHEMY_DATABASE_URI"] = SQLALCHEMY_DATABASE_URI


app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['UPLOAD_FOLDER'] = 'mysite/static/'
app.secret_key = 'super secret key'
db = SQLAlchemy(app)

from mysite import views
