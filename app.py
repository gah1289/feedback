from flask import Flask, render_template, redirect, session, flash, request
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm
from sqlalchemy.exc import IntegrityError

app=Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False
app.config["SECRET_KEY"]="Hopper123"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"]=False

connect_db(app)

toolbar=DebugToolbarExtension(app)

@app.route('/', methods=["GET"])
def home_page():
    '''Show home page'''
    if "username" not in session:
        return redirect('/login')
    else: 
        username=session['username']
        return redirect(f'/users/{username}/feedback/add')


@app.route('/register', methods=['GET', 'POST'])
def register_page():
    '''Show a form that when submitted will register/create a user. This form should accept a username, password, email, first_name, and last_name. Process the registration form by adding a new user.'''
    form=RegisterForm()

    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        email=form.email.data
        first_name=form.first_name.data
        last_name=form.last_name.data

        new_user=User.register(username, password, email, first_name, last_name)
        db.session.add(new_user)

        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken. Please try another one.')
            return render_template('register.html', form=form)
        session['username']=new_user.username
        flash(f'Created account for {new_user.username}!', "success")
        return redirect(f'/users/{new_user.username}/feedback/add')

    return render_template('register.html', form=form)

# @app.route('/secret', methods=["GET"])
# def secret():
#     '''Return the text “You made it!”'''
#     if "username" not in session:
#         flash("Please log in first", "danger")
#         return redirect('/login')
#     else:
#         return ("You Made it!")

@app.route('/login', methods=["GET", "POST"])
def login():
    '''Show a form that when submitted will login a user. Process the login form, ensuring the user is authenticated and going to /secret if so.'''
    form = LoginForm()

    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data

        user=User.authenticate(username, password)

        if user:
            flash(f"Welcome back, {user.first_name}!", "success")
            session['username']=user.username
            return redirect(f'/users/{user.username}/feedback/add')
        else: 
            form.username.errors=['Invalid username/password']
    return render_template('login.html', form=form)

@app.route('/logout', methods=["GET"])
def logout():
    '''Clear any information from the session and redirect to /'''
    user = User.query.filter_by(username=session['username']).one()
    session.pop('username')
    flash(f"Goodbye, {user.first_name}", "secondary")
    return redirect('/')

@app.route('/users/<username>', methods=["GET"])
def user_info(username):
    '''Display a template the shows information about that user (everything except for their password). You should ensure that only logged in users can access this page.'''
    if "username" not in session:
        flash("Please log in first", "danger")
        return redirect('/login')
    else:
        user = User.query.filter_by(username=session['username']).one()
        return render_template("user.html", user=user)

@app.route('/users/<username>/delete', methods=["POST"])
def remove_user(username):
    '''Remove the user from the database and make sure to also delete all of their feedback. Clear any user information in the session and redirect to /. Make sure that only the user who is logged in can successfully delete their account'''
    if "username" not in session or username != session['username']:
        flash("Please log in first", "danger")
        return redirect('/login')
    else:
        user=User.query.get_or_404(username)
        db.session.delete(user)
        db.session.commit()
        session.pop("username")
        flash(f"Successfully deleted account.", "info")
        return redirect('/login')

@app.route('/users/<username>/feedback/add', methods=["GET","POST"])
def add_and_show_feedback(username):
    '''Display a form to add feedback Make sure that only the user who is logged in can see this form. Add a new piece of feedback and redirect to /users/<username> — Make sure that only the user who is logged in can successfully add feedback'''
    if "username" not in session or username != session['username']:
        flash("Please log in first", "danger")
        return redirect('/login')      
    form=FeedbackForm()
    all_posts=Feedback.query.all()
    user=User.query.filter_by(username=session['username']).one()
    if form.validate_on_submit():
        title=form.title.data
        content=form.content.data
        new_post=Feedback(title=title, content=content, username=username)
        db.session.add(new_post)
        db.session.commit()
        flash("Post Added!", "success")
        return redirect('/')
    return render_template('home.html', user=user, form=form, posts=all_posts)

@app.route('/feedback/<feedback_id>/update', methods=["GET", "POST"])
def edit_posts(feedback_id):
    '''Display a form to edit feedback — **Make sure that only the user who has written that feedback can see this form **'''
    post=Feedback.query.get_or_404(feedback_id)
    form=FeedbackForm(obj=post)
    if "username" not in session or post.username != session['username']:
        flash("Please log in first!", "danger")
        return redirect('/')
    if post.username == session['username']:
       
       if form.validate_on_submit():
        post.title=form.title.data
        post.content=form.content.data
        db.session.commit()
        flash("Post Updated!", "success")
        return redirect('/')
    return render_template('post.html', form=form)


@app.route('/feedback/<feedback_id>/delete', methods=["POST"])
def delete_post(feedback_id):
    '''Delete a specific piece of feedback and redirect to /users/<username> — Make sure that only the user who has written that feedback can delete it'''
    post=Feedback.query.get_or_404(feedback_id)   
    if "username" not in session or post.username != session['username']:
        flash("Please log in first!", "danger")
        return redirect('/')
    if post.username == session['username']:
        db.session.delete(post)
        db.session.commit()
        flash("Post deleted", "info")
        return redirect('/')


