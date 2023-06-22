import json
import os

import requests
from PIL import Image

from flask import Flask, render_template, redirect, url_for, request
from flask_login import UserMixin
from flask_login import LoginManager, current_user, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.sqlite3'
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager()
# Added this line fixed the issue.
login_manager.init_app(app)
login_manager.login_view = 'users.login'


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


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


@app.route('/')
@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        user_exists = User.query.filter_by(email=email).first()
        print(user_exists)
        if user_exists:
            return '<h1>User already exists</h1>'
        else:
            user = User(email=email, username=username, password=password)
            user.create_user()
            return redirect(url_for('login'))
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('shesvla.html', title='Login')


@app.route('/main', methods=['POST', 'GET'])
def mtavari():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))

    # meals.json is a file that contains a list of meals
    # meals.json is located in the same directory as main.py
    meals_from_json = json.load(open('meals.json', 'r'))

    # resize imaages to 700x467
    # for meal in meals_from_json:
    #     image_url = meal['image']
    #     image_name = image_url.split('/')[-1]
    #     save_path = os.path.join('static/img/meals', image_name)
    #
    #     # Download the image
    #     response = requests.get(image_url)
    #     response.raise_for_status()
    #     # Save the image to the specified path
    #     with open(save_path, 'wb') as f:
    #         f.write(response.content)
    #
    #     # Open and resize the image
    #     image = Image.open(save_path)
    #     resized_image = image.resize((700, 467), Image.ANTIALIAS)
    #
    #     # Save the resized image to the same path
    #     resized_image.save(save_path)


    return render_template('main.html', title='Mtavari', meals=meals_from_json)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            if user_exists.password == password:
                login_user(user_exists)
                return redirect(url_for('mtavari'))
            else:
                return '<h1>Password is incorrect</h1>'
        else:
            return '<h1>User does not exist</h1>'
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('Login.html', title='Login')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
