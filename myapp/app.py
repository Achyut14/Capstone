from flask import Flask, render_template, flash, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from myapp.models import db, connect_db, CreateUsers
from myapp.forms import AddUsers, Login, SearchForm
from functools import wraps
from myapp.config import Config  # Import the Config class
from dotenv import load_dotenv  # Import load_dotenv to load environment variables
import os

# Load environment variables from a .env file in the root directory
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

def create_app():
    """Factory function to create and configure the Flask application."""
    app = Flask(__name__)

    # Configure application settings from the Config class
    app.config.from_object(Config)
    app.app_context().push()

    # Connect to the database and create all tables if they don't exist
    connect_db(app)
    with app.app_context():
        db.create_all()

    # Define routes inside create_app so they have access to 'app'
    
    @app.route('/')
    def home_page():
        """Render the home page."""
        return render_template("index.html")

    @app.route("/create/account", methods=["GET", "POST"])
    def create_account():
        """Create a new user account."""
        form = AddUsers()  # Instantiate the form for adding users
        if form.is_submitted():
            if form.validate():
                # Generate a hashed password for security
                hashed_password = generate_password_hash(form.create_password.data, method='pbkdf2:sha256:15000')
                new_user = CreateUsers(
                    firstname=form.first_name.data,
                    lastname=form.last_name.data,
                    email=form.email.data,
                    username=form.username.data,
                    password=hashed_password
                )
                try:
                    # Add new user to the database
                    db.session.add(new_user)
                    db.session.commit()
                    flash("Account created successfully! You can now log in.", 'success')
                    return redirect(url_for('login'))
                except Exception as e:
                    # Rollback in case of error
                    db.session.rollback()
                    flash(f"Error creating account: {str(e)}", 'danger')
            else:
                # Handle form validation errors
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f"Error in {field}: {error}", 'danger')
        return render_template('create_acc_form.html', form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Handle user login."""
        form = Login()  # Instantiate the login form
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            user = CreateUsers.query.filter_by(username=username).first()  # Query user by username
            if user and check_password_hash(user.password, password):  # Check if user exists and password matches
                # Set session variables for the logged-in user
                session['logged_in'] = True
                session['user_id'] = user.id
                session['first_name'] = user.firstname
                session['last_name'] = user.lastname
                flash("Logged in successfully!")
                return redirect(url_for('your_account'))
            else:
                flash("Incorrect username or password!", 'danger')
        return render_template('login_form.html', form=form)

    def login_required(f):
        """Decorator to protect routes that require authentication."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'logged_in' not in session:
                flash("Please log in to access this page.", 'warning')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function

    @app.route('/login/account')
    @login_required
    def your_account():
        """Display the user's account details."""
        form = SearchForm()  # Instantiate the search form
        return render_template("your_account.html", form=form, first_name=session.get('first_name', ''), last_name=session.get('last_name', ''))

    @app.route("/logout")
    @login_required
    def logout():
        """Log out the user."""
        session.clear()  # Clear the session
        flash("Logged out successfully!", "info")
        return redirect(url_for('login'))

    @app.route('/search/results', methods=['GET', 'POST'])
    @login_required
    def search_results():
        """Search for articles using an external API."""
        if request.method == 'POST':
            data = request.json  # Get JSON data from the request
            query = data.get('query')
        else:
            query = request.args.get('query')  # Get query parameter from URL
        # Construct the URL with the search query and API key
        url = f'https://newsapi.org/v2/everything?q={query}&apiKey={app.config["API_KEY"]}'
        response = requests.get(url)  # Make a GET request to the external API
        return jsonify(response.json())  # Return the response as JSON

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
