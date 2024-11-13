from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

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
    password = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

# Character model for the database
class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    character_type = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    user = db.relationship('User', backref=db.backref('characters', lazy=True))

    def __repr__(self):
        return f'<Character {self.name}, {self.character_type}>'

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
        if user and user.password == password:
            session['user_id'] = user.id  # Save user session
            return redirect(url_for('character_creation'))  # Redirect to character creation page
        else:
            return render_template('login_page.html', error="Invalid username or password")

    return render_template('login_page.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "Username already exists. Please choose another one."

        # Add the new user to the database
        new_user = User(username=username, password=password)
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
        return redirect(url_for('login'))  # Redirect to login if user is not logged in

    # Fetch the user's characters
    user = User.query.get(user_id)
    characters = user.characters  # Get all characters of the logged-in user

    if len(characters) >= 3:
        return render_template('character_creation.html', characters=characters, max_characters=True)

    if request.method == 'POST':
        # If user submits a new character
        character_name = request.form['character_name']
        character_type = request.form['character_type']

        # Create and save the new character
        new_character = Character(name=character_name, character_type=character_type, user_id=user.id)
        db.session.add(new_character)
        db.session.commit()

        return redirect(url_for('character_creation'))  # Redirect back to character creation page after character creation

    return render_template('character_creation.html', characters=characters, max_characters=False)

@app.route('/delete_character/<int:character_id>', methods=['GET'])
def delete_character(character_id):
    user_id = session.get('user_id')

    if user_id is None:
        return redirect(url_for('login'))  # Redirect to login if user is not logged in

    # Fetch the character to delete
    character_to_delete = Character.query.get(character_id)

    # Ensure the character belongs to the logged-in user
    if character_to_delete and character_to_delete.user_id == user_id:
        db.session.delete(character_to_delete)
        db.session.commit()

    return redirect(url_for('character_creation'))  # Redirect back to character creation page after deletion

@app.route('/select_character/<int:character_id>', methods=['GET'])
def select_character(character_id):
    user_id = session.get('user_id')

    if user_id is None:
        return redirect(url_for('login'))  # Redirect to login if user is not logged in

    # Fetch the selected character
    character = Character.query.get(character_id)

    # Ensure the character belongs to the logged-in user
    if character and character.user_id == user_id:
        # Save the character selection in the session
        session['selected_character_id'] = character.id
        return redirect(url_for('game'))  # Redirect to the game page

    return redirect(url_for('character_creation'))  # Redirect back to character creation if something goes wrong

@app.route('/game')
def game():
    user_id = session.get('user_id')
    selected_character_id = session.get('selected_character_id')

    if user_id is None or selected_character_id is None:
        return redirect(url_for('login'))  # Redirect to login if user is not logged in or no character is selected

    # Fetch the selected character
    character = Character.query.get(selected_character_id)

    if character and character.user_id == user_id:
        return render_template('game_page.html', character=character)  # Pass the selected character to the game page

    return redirect(url_for('character_creation'))  # Redirect to character creation if no valid character is selected

if __name__ == '__main__':
    app.run(debug=True)
