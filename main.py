from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dummy user database (replace with real database logic)
users_db = {"testuser": "password123"}

@app.route('/')
def index():
    return render_template('title_screen.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username exists and the password matches
        if username in users_db and users_db[username] == password:
            return redirect(url_for('game'))  # Redirect to the game page on success
        else:
            return render_template('login_page.html', error="Invalid username or password")

    return render_template('login_page.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username already exists
        if username in users_db:
            return "Username already exists. Please choose another one."

        # Add the new user (in a real app, you would add it to a database)
        users_db[username] = password
        return redirect(url_for('login'))  # Redirect to login after successful registration

    return render_template('register.html')

@app.route('/game')
def game():
    return render_template('game_page.html')

if __name__ == '__main__':
    app.run(debug=True)
