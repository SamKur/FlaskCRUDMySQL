from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql
import re

# Initialize the Flask app
app = Flask(__name__)
app.secret_key = "your_secret_key"

# MySQL configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '1122',
    'db': 'flask_crud',
    'cursorclass': pymysql.cursors.DictCursor  # Ensures results are returned as dictionaries
}

# Home route (List all users)
@app.route('/')
def index():
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT * FROM users")
            users = cur.fetchall()
        return render_template('index.html', users=users)
    finally:
        connection.close()

# Function to validate name
def is_valid_name(name):
    return name and name.replace(" ", "").isalpha()

# Function to validate email
def is_valid_email(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

# Function to validate age
def is_valid_age(age):
    return age.isdigit() and 0 <= int(age) <= 120

# Route to render add user form and process the user addition
@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        age = request.form['age']
        
        errors = []  # List to hold error messages
        
        # Validation checks
        if not is_valid_name(name):
            errors.append('Invalid name. Please enter a valid name.')
        
        if not is_valid_email(email):
            errors.append('Invalid email address. Please enter a valid email.')

        if not is_valid_age(age):
            errors.append('Invalid age. Please enter a valid age between 0 and 120.')

        if errors:
            return render_template('add_user.html', errors=errors, name=name, email=email, age=age)

        connection = pymysql.connect(**db_config)
        try:
            with connection.cursor() as cur:
                cur.execute("INSERT INTO users (name, email, age) VALUES (%s, %s, %s)", (name, email, age))
            connection.commit()
            flash('User added successfully!')
            return redirect(url_for('index'))
        except pymysql.err.IntegrityError:
            flash('Email already exists. Please use a different email.')
        finally:
            connection.close()
        
    return render_template('add_user.html')

# Route to edit a user (dynamic route)
@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit_user(id):
    connection = pymysql.connect(**db_config)
    try:
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            age = request.form['age']
            
            errors = []  # List to hold error messages
            
            # Validation checks
            if not is_valid_name(name):
                errors.append('Invalid name. Please enter a valid name.')
            
            if not is_valid_email(email):
                errors.append('Invalid email address. Please enter a valid email.')

            if not is_valid_age(age):
                errors.append('Invalid age. Please enter a valid age between 0 and 120.')

            if errors:
                # Fetch the existing user data to prefill the form
                with connection.cursor() as cur:
                    cur.execute("SELECT * FROM users WHERE id = %s", [id])
                    user = cur.fetchone()
                return render_template('edit.html', user=user, errors=errors)

            try:
                with connection.cursor() as cur:
                    cur.execute("""
                        UPDATE users
                        SET name = %s, email = %s, age = %s
                        WHERE id = %s
                    """, (name, email, age, id))
                connection.commit()
                flash('User updated successfully!')
                return redirect(url_for('index'))
            except pymysql.err.IntegrityError:
                flash('Email already exists. Please use a different email.')
                # Fetch the existing user data to prefill the form
                with connection.cursor() as cur:
                    cur.execute("SELECT * FROM users WHERE id = %s", [id])
                    user = cur.fetchone()
                return render_template('edit.html', user=user, errors=['Email already exists. Please use a different email.'])

        # Fetch existing user data
        with connection.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", [id])
            user = cur.fetchone()
        return render_template('edit.html', user=user)
    finally:
        connection.close()

# Route to delete a user
@app.route('/delete/<id>', methods=['POST'])
def delete_user(id):
    connection = pymysql.connect(**db_config)
    try:
        with connection.cursor() as cur:
            cur.execute("DELETE FROM users WHERE id = %s", [id])
        connection.commit()
        flash('User deleted successfully!')
    finally:
        connection.close()
    return redirect(url_for('index'))

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
