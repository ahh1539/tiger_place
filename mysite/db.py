from mysite import db


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
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)


class Item(db.Model):
    __tablename__ = 'items'
    item_id = db.Column(db.Integer, db.Sequence('seq_reg_id', start=1, increment=1),
                        primary_key=True)
    name = db.Column(db.String(100))
    price = db.Column(db.String(100))
    description = db.Column(db.String(500))
    category = db.Column(db.String(50))
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    img_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=db.func.now())
    deleted_at = db.Column(db.DateTime)
