import random
import json
from flask import Flask, render_template, request, redirect, url_for, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'super_secret_key'

# Initialize LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Sample User Data - You would store this in a real database
users_db = {}

# Load items and locations data from JSON
def load_items():
    with open('data/items.json') as file:
        return json.load(file)

ITEMS = load_items()

# Load abilities from items.json
def load_abilities():
    return ITEMS['abilities']

# User Class (For Flask-Login)
class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password  # Hashed password

# Create a user loader function for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    # In a real application, you'd load from a database
    return users_db.get(user_id)

# Title screen route
@app.route('/')
def index():
    return render_template('index.html')

# Login page route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user exists in the users_db
        user = users_db.get(username)
        if user and check_password_hash(user.password, password):
            # If password matches, log the user in
            login_user(user)
            return redirect(url_for('create_character'))
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

# Register page route (for creating new users)
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        # In a real application, you would save this to a database
        if username not in users_db:
            user = User(id=username, username=username, password=hashed_password)
            users_db[username] = user
            login_user(user)  # Log the user in after registration
            return redirect(url_for('create_character'))
        else:
            return render_template('register.html', error="Username already exists")

    return render_template('register.html')

# Character creation page
@app.route('/create_character', methods=['GET', 'POST'])
@login_required  # Ensure the user is logged in before accessing this page
def create_character():
    if request.method == 'POST':
        name = request.form['name']
        abilities = request.form.getlist('abilities')

        # Initialize character in session
        session['character'] = {
            'name': name,
            'abilities': abilities,
            'health': 100,
            'coins': 0,
            'inventory': ITEMS["starting_items"]
        }

        return redirect(url_for('select_abilities'))
    return render_template('create_character.html', abilities=ITEMS["abilities"])

# Abilities selection page
@app.route('/select_abilities', methods=['GET', 'POST'])
@login_required
def select_abilities():
    abilities = load_abilities()
    if request.method == 'POST':
        selected_abilities = request.form.getlist('abilities')
        if len(selected_abilities) > 3:
            return render_template('select_abilities.html', abilities=abilities, error="You can only select 3 abilities.")
        # Update abilities in session
        session['character']['abilities'] = selected_abilities
        return redirect(url_for('explore'))
    return render_template('select_abilities.html', abilities=abilities)

# Route: Explore Locations
@app.route('/explore')
@login_required
def explore():
    character = session.get('character')
    if character is None:
        return redirect(url_for('index'))
    return render_template('explore.html', character=character, locations=ITEMS["locations"])

# Route: Event in a Location
@app.route('/event/<location_name>')
@login_required
def event(location_name):
    character = session.get('character')
    if character is None:
        return redirect(url_for('index'))

    location = next((loc for loc in ITEMS["locations"] if loc["name"] == location_name), None)
    if location is None:
        return redirect(url_for('explore'))

    event = random.choice(location['events'])
    if event['type'] == 'combat':
        return redirect(url_for('fight', location_name=location_name, event_name=event['name']))
    elif event['type'] == 'reward':
        character['coins'] += event['reward']
        session['character'] = character
        return render_template('event.html', event=event, character=character, location_name=location_name)

# Route: Fight in Event
@app.route('/fight')
@login_required
def fight():
    character = session.get('character')
    event_name = request.args.get('event_name')
    location_name = request.args.get('location_name')

    if character is None or not event_name or not location_name:
        return redirect(url_for('index'))

    # Combat logic
    damage = random.randint(10, 30)
    character['health'] -= damage
    session['character'] = character

    if character['health'] <= 0:
        return redirect(url_for('game_over'))

    event = {
        'name': event_name,
        'type': 'combat',
        'damage': damage
    }
    return render_template('event.html', event=event, character=character, location_name=location_name)

# Route: Shop
@app.route('/shop')
@login_required
def shop():
    character = session.get('character')
    if character is None:
        return redirect(url_for('index'))
    return render_template('shop.html', character=character, items=ITEMS['shop_items'])

# Route: Purchase Item
@app.route('/purchase/<item_name>')
@login_required
def purchase(item_name):
    character = session.get('character')
    if character is None:
        return redirect(url_for('index'))

    item = next((item for item in ITEMS['shop_items'] if item['name'] == item_name), None)
    if item and character['coins'] >= item['price']:
        character['coins'] -= item['price']
        character['inventory'].append(item)
        session['character'] = character
        return redirect(url_for('shop'))

    return redirect(url_for('shop'))

# Route: Game Over
@app.route('/game_over')
def game_over():
    return render_template('game_over.html')

# Route: Logout
@app.route('/logout')
@login_required
def logout():
    logout_user()  # Log the user out
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
