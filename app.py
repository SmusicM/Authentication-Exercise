from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User,Feedback
from forms import UserForm,LoginForm,FeedbackForm
from sqlalchemy.exc import IntegrityError


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///auth_exercise"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


connect_db(app)

toolbar = DebugToolbarExtension(app)



with app.app_context():
    db.create_all()

@app.route('/')
def home_page():
    
    return redirect('/register')

@app.route('/users/<username>')
def secret(username):
    if "username" not in session:
        flash("please login first!", "danger")
        return redirect('/register')
    #users = User.query.get_or_404(username)
    
    #works for not other users letting vieew acc
    #if session['username']!=username:
    #    flash("you are not authorized to view this users page",'danger')
    #    session.pop('username',False)
    #    return redirect("/login")
        
    users = User.query.filter_by(username=username).first()
    if not users:
        flash("user not found",'info')
        return redirect('/login')
    feedback = Feedback.query.filter_by(username=username).all()
    #session['username'] =users.username
    #if "username" not in session:
    #    flash("please login first!", "danger")
    #    return redirect('/register')
    return render_template("secret.html",users=users,feedback=feedback)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username,password,email,first_name,last_name)
        db.session.add(new_user)
        db.session.commit()
        session['username'] = new_user.username
        flash("congrats on creating account",'success')
        return redirect(f'/users/{username}')
    return render_template("register.html",form=form)


@app.route('/login',methods=(['GET','POST']))
def login():
     form = LoginForm()
     if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
       
        user = User.authenticate(username,password)
        
        if user:
            flash(f"you successfully logged in {user.username}",'success')
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['invalid username or password']
        
     return render_template('login.html',form=form)

@app.route('/logout')
def logout():
    session.pop('username')
    flash("See you next time!",'info')
    return redirect('/login')

@app.route('/users/<username>/delete',methods=['POST'])
def delete_user(username):
    
    if 'username' not in session:
        flash("please login","danger")
        return redirect('/login')
    
    if session.get('username')!=username:
        flash("you are not authorized to delete another users page",'danger')
        
        return redirect("/login")

    user = User.query.get_or_404(username)
    
    
    Feedback.query.filter_by(username=username).delete()
    db.session.delete(user)
    db.session.commit()
    session.pop('username')
    flash('User successfully deleted, we will miss you!','info')
    return redirect('/register')
    

@app.route('/users/<username>/feedback/add',methods=['GET','POST'])
def add_feedback(username):
    
    if "username" not in session:
        flash("please login first!", "danger")
        return redirect('/')
    #user= User.query.get_or_404(username)
    user= User.query.filter_by(username=username).first_or_404()
    form = FeedbackForm()
    #session['username'] = user.username
    if session['username']!=user.username:
        flash("you are not authorized to add feedback for other users",'danger')
        return redirect('/')
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_feedback = Feedback(title=title,
                                content=content,username=session['username'])
        db.session.add(new_feedback)
        db.session.commit()

        flash("Feedback created!",'success')
        return redirect(f'/users/{user.username}')
   
    return render_template("add_feedback.html",form=form,user=user)


@app.route('/feedback/<int:id>/update',methods=["GET","POST"])
def update_feedback(id):
    if "username" not in session:
        flash("please login first!", "danger")
        return redirect('/login')
    
    
    feedback = Feedback.query.get_or_404(id)

    if session['username']!=feedback.username:
        flash("You are not authorized to update other users post",'danger')
        return redirect('/login')


    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        if title:
            feedback.title = title
        if content:
            feedback.content = content
        db.session.commit()
        flash("Feed back was updated successfully",'info')
        return redirect(f'/users/{feedback.username}')
    return render_template("edit_feedback.html",form=form,feedback=feedback)



@app.route('/feedback/<int:id>/delete',methods=["POST"])
def delete_feedback(id):
    if "username" not in session:
        flash("please login first!", "danger")
        return redirect('/login')
    
    
    feedback = Feedback.query.get_or_404(id)

    if session['username']!=feedback.username:
        flash("You are not authorized to delete other users post",'danger')
        return redirect('/login')
    if feedback.username == session['username']:
        db.session.delete(feedback)
        db.session.commit()
        flash("Feedback successfully deleted",'info')
        return redirect(f'/users/{feedback.username}')
    

@app.route("/feedback")
def all_feedback():
    if "username" not in session:
        flash("please login first!", "danger")
        return redirect('/login')
    feedback = Feedback.query.all()
    return render_template("feedback.html",feedback=feedback)
