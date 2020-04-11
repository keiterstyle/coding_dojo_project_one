from flask import Flask, render_template, redirect, request, session, flash, get_flashed_messages, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy 
from flask_migrate import Migrate
from sqlalchemy.sql import func 
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import re
import os
import glob


UPLOAD_FOLDER = './static/uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.secret_key="blarble24481zkk34"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///injury_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER 


bcrypt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    belt_rank = db.Column(db.String(10))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    @classmethod
    def add_new_user(cls, user_data):
        hashed_password = bcrypt.generate_password_hash(user_data['password'])
        new_user = cls(
            first_name = user_data['first_name'], 
            last_name = user_data['last_name'], 
            email = user_data['email'], 
            belt_rank = user_data['belt_rank'], 
            password = hashed_password
            )
        db.session.add(new_user)
        print("Adding new user.")
        print(new_user)
        db.session.commit()
        return new_user

    @classmethod
    def validate_user(cls, user_data): # user_data is the form submission
        is_valid = True
        if len(user_data["first_name"]) < 1:
            is_valid = False
            flash("Enter your first name.", "reg_error")
        if len(user_data["last_name"]) < 1:
            is_valid = False
            flash("Enter your last name.", "reg_error")
        if not EMAIL_REGEX.match(user_data["email"]):
            is_valid = False
            flash("Enter a valid email.", "reg_error" )
        if len(user_data["belt_rank"]) < 1:
            is_valid = False
            flash("Enter a valid belt rank.", "reg_error")
        if len(user_data["password"]) < 8:
            is_valid = False
            flash("Your password should be at least 8 characters long.", "reg_error")
        if user_data["password"] != user_data["cpassword"]:
            is_valid = False
            flash("Your passwords do not match.", "reg_error")
        return is_valid

class Injury(db.Model):    
    __tablename__ = "injuries"
    id = db.Column(db.Integer, primary_key=True)
    injury_location = db.Column(db.String(55))
    injury_type = db.Column(db.String(55))
    pain_level = db.Column(db.String(55))
    pic = db.Column(db.String(55))
    injury_comment = db.Column(db.String(155))
    athlete_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    athlete = db.relationship('User', foreign_keys=[athlete_id], backref="injuries", cascade = "all")
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

@app.route('/add_new_injury', methods=["POST"])
def add_new_injury(): 
    file = request.files['upload']
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)
    new_injury = Injury(
        injury_location = request.form['injury_location'],
        injury_type = request.form['injury_type'],
        pain_level = request.form['pain_level'],
        pic = filepath,
        injury_comment = request.form['injury_comment'],
        athlete_id = session['cur_user']
    )      
    print("Adding a new injury to the database:")
    print(new_injury)
    db.session.add(new_injury)
    db.session.commit()
    return redirect("/home")  
        
         # request.form() - in this method, we use request.form to get the injury_location/type/pain_level and the injury image. Once we get with request.form(), we create an injury object and insert it into the db. Once we insert into db, we get session using cur_user, since it's a 1tM relationship we just want to add the injury to that user. Last, we return response (can be anything - redirect back to /home to view the users injury) return to this for review purposes.

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/photolog')
def photolog():
    if 'cur_user' not in session:
        return redirect("/")
    else:
        users_list = User.query.all()
        return render_template("/photolog.html", all_users = users_list)

@app.route('/gallery')
def gallery():
    if 'cur_user' not in session:
        return redirect("/")
    else:
        user = User.query.get(session["cur_user"])
        print(user.injuries)
        return render_template("/gallery.html", user = user)

@app.route('/')
def index():
    return render_template("login_reg.html")

@app.route('/register', methods=["POST"])
def register_new_user():
    validation_check = User.validate_user(request.form)
    if not validation_check:
        return redirect("/")
    else:
        new_user = User.add_new_user(request.form)
        session["cur_user"] = new_user.id # changed user_id to cur_user 3.9 1:20pm
        return redirect("/home")

@app.route('/login', methods=["POST"])
def validate_login():
    user = User.query.filter_by(email=request.form['lemail']).all()
    is_valid = True if len(user)==1 and bcrypt.check_password_hash(user[0].password, request.form['lpassword']) else False 
    if is_valid:
        session['cur_user'] = user[0].id 
        return redirect("/home")
    else:
        flash("Invalid Login Credentials", "log_error")
        return redirect("/")

@app.route('/home')
def home():
    if 'cur_user' not in session:
        return redirect("/")
    else:
        user = User.query.get(session["cur_user"])
        print(user.injuries)
        return render_template("/home.html", user = user)
    
@app.route('/all_injuries')
def all_injuries():
    if 'cur_user' not in session:
        return redirect("/")
    else:
        injuries_list = Injury.query.all()
        return render_template("/all_injuries.html", all_injuries = injuries_list)

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
