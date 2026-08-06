from flask_wtf import FlaskForm
from wtforms import DecimalField, SubmitField,StringField, RadioField, IntegerField, DateField, PasswordField, EmailField, TextAreaField
from wtforms.validators import InputRequired, NumberRange, EqualTo

"""
class Home(FlaskForm):
        name = StringField("Name:", validators=[InputRequired()])
        email = EmailField("Email:", validators=[InputRequired()])
        phone_number = StringField("Phone Number:", validators=[InputRequired()])
        address = StringField("Address:", validators=[InputRequired()])
        submit = SubmitField("Submit")
"""

class RegisterForm(FlaskForm):
        first_name= StringField("*First Name:", validators=[InputRequired()])
        last_name= StringField("*Last Name:", validators=[InputRequired()])
        email = EmailField("*Email:", validators=[InputRequired()])
        password = PasswordField("*Password", validators=[InputRequired()] )
        password2 = PasswordField("*Confirm Password:", 
                        validators=[InputRequired(), EqualTo("password") ]) 
        phone_number = StringField("Phone Number:")
        address = StringField("*Address:", validators=[InputRequired()])
        submit = SubmitField("Register")

class Login(FlaskForm):
        email = EmailField("Email:", validators=[InputRequired()])
        password = PasswordField("Password", validators=[InputRequired()] )
        submit = SubmitField("Login")


class Pizza(FlaskForm):
        size = RadioField(
                choices = ["Small (~8inch)", "Medium (~14inch)", "Large (~16inch)"], validators=[InputRequired()])
        submit =  SubmitField("Add to cart")

class FilterPizza(FlaskForm):
        Filter = RadioField(
                choices = ["price (Highest to cheapest)"])
        submit =  SubmitField("filter")

# reviews 
class SubmitReviews(FlaskForm):
        review = TextAreaField("Add a review:")
        rating = RadioField(
                choices = ["★","★★","★★★","★★★★","★★★★★"])
        submit = SubmitField("Submit Review")


class ReplyReviews(FlaskForm):
        reply = TextAreaField("Add a review:")
        submit = SubmitField("reply")


class PromoCode(FlaskForm):
        code = StringField("Enter a Valid Promo Code (15% off):")
        submit = SubmitField("redeem code")



class CheckOut(FlaskForm):
        security_number = PasswordField("Enter your credit security number:", validators=[InputRequired()])
        code = PasswordField("Enter your credit number:", validators=[InputRequired()])
        submit = SubmitField("Check Out")

class AdminLogin(FlaskForm):
        email = EmailField("Email:", validators=[InputRequired()])
        password = PasswordField("Password", validators=[InputRequired()] )
        submit = SubmitField("Login")



class EditMenu(FlaskForm):
        pizza_name = StringField("Pizza Name:", validators=[InputRequired()])
        base_price = DecimalField("Base_price:", validators=[InputRequired()])
        description = TextAreaField("Description:", validators=[InputRequired()])
        submit = SubmitField("Update pizza")