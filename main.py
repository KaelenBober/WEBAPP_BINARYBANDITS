from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash
import json

# Initialize the Flask app and configure the database URI
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # Disable unnecessary tracking
app.config['SECRET_KEY'] = 'your-secret-key'  # Required for session management
db = SQLAlchemy(app)

# User model for the database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)  # Store hashed passwords
    credits = db.Column(db.Integer, default=0)  # Default credits
    game_state = db.Column(db.Text, default=json.dumps({}))  # Store game state as JSON
    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute.")
    
    @password.setter
    def password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)
    
    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)
    
    # Helper methods to get/set game state
    def get_game_state(self):
        return json.loads(self.game_state)
    
    def set_game_state(self, state):
        self.game_state = json.dumps(state)
    
def __repr__(self):
    return f'<User {self.username}>'

# Character model for the database
class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    character_type = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    health = db.Column(db.Integer, default=100)  # Default health
    attack = db.Column(db.Integer, default=10)  # Default attack power
    defense = db.Column(db.Integer, default=5)  # Default defense

    user = db.relationship('User', backref=db.backref('characters', lazy=True))

# Create the database and tables if they don't exist
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('title_screen.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username exists and the password matches
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id  # Save user session
            return redirect(url_for('character_creation'))  # Redirect to character creation page
        else:
            flash("Invalid username or password.", "error")
            return render_template('login_page.html')

    return render_template('login_page.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists. Please choose another one.", "error")
            return render_template('register.html')

        # Add the new user to the database
        new_user = User(username=username)
        new_user.password = password
        db.session.add(new_user)
        db.session.commit()

        # Log the user in automatically
        session['user_id'] = new_user.id
        return redirect(url_for('character_creation'))  # Redirect to character creation page after registration

    return render_template('register.html')

@app.route('/character_creation', methods=['GET', 'POST'])
def character_creation():
    user_id = session.get('user_id')

    if user_id is None:
        flash("Please log in to create a character.", "error")
        return redirect(url_for('login'))  # Redirect to login if user is not logged in

    # Fetch the user's characters
    user = User.query.get(user_id)
    characters = user.characters  # Get all characters of the logged-in user

    if len(characters) >= 3:
        flash("You have reached the maximum number of characters (3).", "info")
        return render_template('character_creation.html', characters=characters, max_characters=True)

    if request.method == 'POST':
        # If user submits a new character
        character_name = request.form['character_name']
        character_type = request.form['character_type']

        if not character_name or not character_type:
            flash("Please fill out both fields to create a character.", "error")
            return redirect(url_for('character_creation'))

        # Create and save the new character
        new_character = Character(name=character_name, character_type=character_type, user_id=user.id)
        db.session.add(new_character)
        db.session.commit()

        # Store the new character in the session
        session['selected_character_id'] = new_character.id

        # Redirect to the game page after character creation
        flash(f"Character {character_name} created successfully!", "success")
        return redirect(url_for('character_creation'))

    return render_template('character_creation.html', characters=characters, max_characters=False)

@app.route('/delete_character/<int:character_id>', methods=['GET'])
def delete_character(character_id):
    user_id = session.get('user_id')

    if user_id is None:
        flash("Please log in to delete a character.", "error")
        return redirect(url_for('login'))  # Redirect to login if user is not logged in

    # Fetch the character to delete
    character_to_delete = Character.query.get(character_id)

    # Ensure the character belongs to the logged-in user
    if character_to_delete and character_to_delete.user_id == user_id:
        db.session.delete(character_to_delete)
        db.session.commit()
        flash(f"Character {character_to_delete.name} deleted successfully.", "success")
    else:
        flash("You cannot delete this character.", "error")

    return redirect(url_for('character_creation'))  # Redirect back to character creation page after deletion

@app.route('/select_character/<int:character_id>', methods=['GET'])
def select_character(character_id):
    user_id = session.get('user_id')

    if user_id is None:
        flash("Please log in to select a character.", "error")
        return redirect(url_for('login'))  # Redirect to login if user is not logged in

    # Fetch the selected character
    character = Character.query.get(character_id)

    # Ensure the character belongs to the logged-in user
    if character and character.user_id == user_id:
        # Save the character selection in the session
        session['selected_character_id'] = character.id
        session['character_type'] = character.character_type  # Save character_type to session
        flash(f"Character {character.name} selected!", "success")
        return redirect(url_for('game'))  # Redirect to the game page

    flash("Invalid character selection.", "error")
    return redirect(url_for('character_creation'))  # Redirect back to character creation if something goes wrong
    
@app.route('/minigame_reward', methods=['POST'])
def minigame_reward():
    user_id = session.get('user_id')

    if not user_id:
        return {"error": "User not logged in"}, 401

    user = User.query.get(user_id)

    if not user:
        return {"error": "User not found"}, 404

    # Retrieve the reward amount from the request
    reward_amount = request.json.get('reward', 0)

    # Update user's credits
    user.credits += reward_amount
    db.session.commit()

    return {"message": f"You've earned {reward_amount} credits!", "credits": user.credits}



@app.route('/upgrade_stats', methods=['POST'])
def upgrade_stats():
    user_id = session.get('user_id')

    if not user_id:
        return {"error": "User not logged in"}, 401

    user = User.query.get(user_id)

    if not user:
        return {"error": "User not found"}, 404

    # Get the stat and cost from the request
    stat = request.json.get('stat')
    cost = request.json.get('cost')

    # Check if the user has enough credits
    if user.credits < cost:
        return {"error": "Not enough credits"}, 400

    # Deduct credits and upgrade the stat
    user.credits -= cost
    if stat == 'health':
        user.health += 10
    elif stat == 'attack':
        user.attack += 5
    elif stat == 'defense':
        user.defense += 5

    db.session.commit()

    return {
        "message": f"Successfully upgraded {stat}!",
        "credits": user.credits
    }


@app.route('/game')
def game():
    user_id = session.get('user_id')

    if not user_id:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    user = User.query.get(user_id)
    if not user:
        return "User not found", 404

    return render_template('game_page.html', user=user)

# Save game state route
@app.route('/save_game', methods=['POST'])
def save_game():
    user_id = session.get('user_id')

    if not user_id:
        return {"error": "User not logged in"}, 401

    user = User.query.get(user_id)

    if not user:
        return {"error": "User not found"}, 404

    # Retrieve data from the client
    new_credits = request.json.get('credits', user.credits)
    new_game_state = request.json.get('game_state', user.get_game_state())

    # Update user's credits and game state
    user.credits = new_credits
    user.set_game_state(new_game_state)
    db.session.commit()

    return {"message": "Game state saved successfully"}

# Load game state route
@app.route('/load_game', methods=['GET'])
def load_game():
    user_id = session.get('user_id')

    if not user_id:
        return {"error": "User not logged in"}, 401

    user = User.query.get(user_id)

    if not user:
        return {"error": "User not found"}, 404

    return {
        "credits": user.credits,
        "game_state": user.get_game_state()
    }

@app.route('/tatooine')
def tatooine():
    return render_template('tatooine_page.html')

@app.route('/tic_tac_toe')
def tic_tac_toe():
    return render_template('tic_tac_toe.html')

@app.route('/trivia')
def crossword():
    return render_template('trivia_page.html')



@app.route('/battle')
def battle():
    # Example: Assume player_image and player_name were set during character creation
    player_image = session.get('player_image', 'default_player_image.jpg')  # Default image if not set
    player_name = session.get('player_name', 'Player')  # Default name if not set

    # Pass the player image and other info to the template
    return render_template('battle.html', player_image=player_image, player_name=player_name)


@app.route('/hoth')
def hoth():
    return render_template('hoth_page.html')

@app.route('/mustafar')
def mustafar():
    return render_template('mustafar_page.html')

if __name__ == '__main__':
    app.run(debug=True)


