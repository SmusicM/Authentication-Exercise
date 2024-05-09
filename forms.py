from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,EmailField
from wtforms.validators import InputRequired,DataRequired,Length

class UserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    email = EmailField("Email",validators=[DataRequired(),Length(max=50)])
    first_name = StringField("firstName",validators=[InputRequired(),Length(min=2,max=30)])
    last_name = StringField("LastName",validators=[InputRequired(),Length(min=2,max=30)])

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[DataRequired()])

class FeedbackForm(FlaskForm):
    
    title = StringField("Title",
                        validators=[InputRequired(),Length(min=2,max=100)])
    content =  StringField("Content",
                        validators=[InputRequired(),Length(min=2,max=1000)])
    