from flask import Flask, render_template, flash, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from myapp.models import db, connect_db, CreateUsers
from myapp.forms import AddUsers, Login, SearchForm
from functools import wraps
from myapp.config import API_KEY 

def create_app():
    app = Flask(__name__)

    # Configure application settings
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///capstone'
    app.app_context().push()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True
    app.config['SECRET_KEY'] = 'your_secret_key_here'
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

    # Connect to the database and create all tables if they don't exist
    connect_db(app)
    with app.app_context():
        db.create_all()

    # Define routes inside create_app so they have access to 'app'
    @app.route('/')
    def home_page():
        return render_template("index.html")

    @app.route("/create/account", methods=["GET", "POST"])
    def create_account():
        form = AddUsers()
        if form.is_submitted():
            if form.validate():
                hashed_password = generate_password_hash(form.create_password.data, method='pbkdf2:sha256:15000')
                new_user = CreateUsers(
                    firstname=form.first_name.data,
                    lastname=form.last_name.data,
                    email=form.email.data,
                    username=form.username.data,
                    password=hashed_password
                )
                try:
                    db.session.add(new_user)
                    db.session.commit()
                    flash("Account created successfully! You can now log in.", 'success')
                    return redirect(url_for('login'))
                except Exception as e:
                    db.session.rollback()
                    flash(f"Error creating account: {str(e)}", 'danger')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        flash(f"Error in {field}: {error}", 'danger')
        return render_template('create_acc_form.html', form=form)

    @app.route("/login", methods=["GET", "POST"])
    def login():
        form = Login()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            user = CreateUsers.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
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
        form = SearchForm()
        return render_template("your_account.html", form=form, first_name=session.get('first_name', ''), last_name=session.get('last_name', ''))

    @app.route("/logout")
    @login_required
    def logout():
        session.clear()
        flash("Logged out successfully!", "info")
        return redirect(url_for('login'))

    @app.route('/search/results', methods=['GET', 'POST'])
    @login_required
    def search_results():
        if request.method == 'POST':
            data = request.json
            query = data.get('query')
        else:
            query = request.args.get('query')
        url = f'https://newsapi.org/v2/everything?q={query}&apiKey={API_KEY}'
        response = requests.get(url)
        return jsonify(response.json())

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
