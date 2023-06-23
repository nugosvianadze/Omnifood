from flask_login import UserMixin

from config import db


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(20))
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.password}')"

    def create_user(self):
        db.session.add(self)
        db.session.commit()
        return self

    @classmethod
    def get(cls, user_id):
        return cls.query.get(user_id)


class FavMeal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    meal_id = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"User('{self.user_id}', '{self.meal_id}')"

    def create(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self