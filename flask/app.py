
from flask import Flask, render_template, flash, request, jsonify, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from models import db, connect_db, CreateUsers
from forms import AddUsers, Login, SearchForm
from functools import wraps
from config import API_KEY
app = Flask(__name__)

#Configure application settings
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///capstone'
app.app_context().push()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

#Connect to the database and create all tables if they don't exist
connect_db(app)
with app.app_context():
    db.create_all()

#Render the home page
@app.route('/')
def home_page():
    return render_template("index.html")

@app.route("/create/account", methods=["GET", "POST"])
def create_account():
    form = AddUsers()  

    if form.is_submitted():
        if form.validate():
            #Generate a hashed password for security
            hashed_password = generate_password_hash(form.create_password.data, method='pbkdf2:sha256:15000')
            
            #Create a new user instance
            new_user = CreateUsers(
                firstname=form.first_name.data,
                lastname=form.last_name.data,
                email=form.email.data,
                username=form.username.data,
                password=hashed_password
            )
            
            # Add error handling for database operations
            try:
                db.session.add(new_user)  # Add the new user to the session
                db.session.commit()  # Commit the changes to the database
                
                flash("Account created successfully! You can now log in.", 'success')
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback() #Roll back the session in case of an error
                flash(f"Error creating account: {str(e)}", 'danger')

        else:
            # If form did not validate, flash the error messages
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

        if user:
            print("User exists in database: ", user.username)
            
            #Successfull login
            if check_password_hash(user.password, password):
                session['logged_in'] = True
                session['user_id'] = user.id
                session['first_name'] = user.firstname  # set first name to session
                session['last_name'] = user.lastname    # set last name to session
                flash("Logged in successfully!")
                return redirect(url_for('your_account'))
            else:
                flash("Incorrect password!", 'danger')
        else:
            flash("User not found!", 'danger')
        
        return redirect(url_for('login'))
    return render_template('login_form.html', form=form)


def login_required(f):
    #Decorator to protect routes that require authentication
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
    #Account details page
    form = SearchForm()
    first_name = session.get('first_name', '')
    last_name = session.get('last_name', '')
    return render_template("your_account.html", form=form, first_name=first_name, last_name=last_name)

@app.route('/debug-session')
@login_required
def debug_session():
    #A debug route to display session details
    return jsonify(dict(session))

@app.route("/logout")
@login_required
def logout():
    # Clear all keys from the session
    session.clear()
    flash("Logged out successfully!", "info") 
    return redirect(url_for('login'))


@app.route('/search/results', methods=['GET', 'POST'])
@login_required
def search_results():
    if request.method=='POST':
        data = request.json
        query = data.get('query')

    else:
        query=request.args.get('query')
    
    # Construct the URL with the search query and API key
    url = f'https://newsapi.org/v2/everything?q={query}&apiKey={API_KEY}'

    # Make the GET request to the NewsAPI
    response = requests.get(url)
    data = response.json()
    

    # Return the data as a JSON response
    return jsonify(data)


if __name__ == '__main__':
    app.run(debug=True)

