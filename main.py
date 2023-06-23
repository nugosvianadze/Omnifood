import json

from flask import render_template, redirect, url_for, request
from flask_login import login_required
from flask_login import current_user, login_user, logout_user

from config import login_manager, app
from models import User, FavMeal


@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)


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

        user_exists = User.query.filter_by(email=email).first() or User.query.filter_by(username=username).first()
        print(user_exists)
        if user_exists:
            error = 'User already exists with this email or username'
            return render_template('shesvla.html', title='Login', error=error)
        else:
            print('here')
            user = User(email=email, username=username, password=password)
            user.create_user()
            return redirect(url_for('login'))
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    error = False
    return render_template('shesvla.html', title='Login', error=error)


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
                error = 'Password is incorrect'
                return render_template('Login.html', title='Login', error=error)
        else:
            error = 'User does not exist'
            return render_template('Login.html', title='Login', error=error)
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    error = False
    return render_template('Login.html', title='Login', error=error)


@app.route('/main', methods=['GET'])
@login_required
def mtavari():
    print(current_user.is_authenticated)
    meals_from_json = json.load(open('meals.json', 'r'))
    favorited_meals_from_db = FavMeal.query.filter_by(user_id=current_user.id).all()
    for meals in meals_from_json:
        for fav_meal in favorited_meals_from_db:
            if meals['id'] == fav_meal.meal_id:
                meals['is_favorited'] = True
                break
        else:
            meals['is_favorited'] = False
    return render_template('main.html', title='Mtavari', meals=meals_from_json)

@app.route('/add-to-fav/<int:meal_id>', methods=['POST'])
@login_required
def add_to_fav(meal_id):

    meal_exists_in_json = json.load(open('meals.json', 'r'))
    meal_exists_in_json = [meal for meal in meal_exists_in_json if meal['id'] == meal_id]
    if not meal_exists_in_json:
        return '<h1>Meal does not exist</h1>'

    meal_already_favorited = FavMeal.query.filter_by(user_id=current_user.id, meal_id=meal_id).first()
    if meal_already_favorited:
        return '<h1>Meal already favorited</h1>'
    fav_meal = FavMeal(user_id=current_user.id, meal_id=meal_id)
    fav_meal.create()
    return redirect(url_for('fav_meals'))


@app.route('/fav-meals')
@login_required
def fav_meals():
    fav_meals = FavMeal.query.filter_by(user_id=current_user.id).all()
    meals_from_json = json.load(open('meals.json', 'r'))
    fav_meals = [meal for meal in meals_from_json if meal['id'] in [fav_meal.meal_id for fav_meal in fav_meals]]

    return render_template('favourites.html', title='Fav Meals', meals=fav_meals)

@app.route('/delete_favorite/<int:meal_id>')
def delete_favorite(meal_id):
    fav_meal = FavMeal.query.filter_by(user_id=current_user.id, meal_id=meal_id).first()
    if not fav_meal:
        return '<h1>Meal does not exist in favorites</h1>'
    fav_meal.delete()
    return redirect(url_for('fav_meals'))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
