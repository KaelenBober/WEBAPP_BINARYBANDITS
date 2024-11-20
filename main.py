from flask import Flask, flash, redirect, render_template, request, session, url_for
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
        return redirect(url_for('game'))

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

@app.route('/game')
def game():
    user_id = session.get('user_id')
    selected_character_id = session.get('selected_character_id')

    if user_id is None or selected_character_id is None:
        flash("Please log in and select a character to play.", "error")
        return redirect(url_for('login'))  # Redirect to login if user is not logged in or no character is selected

    character = Character.query.get(selected_character_id)

    if character and character.user_id == user_id:
        # Pass the character data to the template, including character_type for dynamic image
        return render_template('game_page.html', character=character, character_type=session.get('character_type'))

    flash("Invalid character data. Please select a valid character.", "error")
    return redirect(url_for('character_creation'))

@app.route('/tatooine')
def tatooine():
    return render_template('tatooine_page.html')

@app.route('/hoth')
def hoth():
    return render_template('hoth_page.html')


if __name__ == '__main__':
    app.run(debug=True)
