from flask import Flask, render_template, redirect, url_for, session,  g, request
from database import get_db, close_db
from forms import RegisterForm, Login, SubmitReviews, PromoCode, Pizza, CheckOut, ReplyReviews, AdminLogin, EditMenu
from flask_session import Session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import datetime
import random


app = Flask(__name__)
app.teardown_appcontext(close_db)
app.config["SECRET_KEY"] = "yap_yap_yap_meow"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.before_request
def load_logged_in_user():
    g.user = session.get("user_id", None)



def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if g.user is None:
            return redirect(url_for("login", next=request.url))
        return view(*args, **kwargs)
    return wrapped_view

#admin required wrapper
def admin_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        db = get_db()
        user = db.execute("SELECT is_admin FROM customers WHERE id = ?", (session["user_id"],)).fetchone()
        if not user or user["is_admin"] != 1:
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return wrap


# reusable function 
def greetingCustomer():
    welcome = ""
    if "user_id" in session:
        customer_id = session["user_id"]
        db = get_db()
        logged_customer = db.execute(" SELECT * FROM customers WHERE id = ? ;" , (customer_id,)).fetchone() 
        if logged_customer: 
            welcome = [ f"Welcome back {logged_customer['first_name']}",  
                        f"Nice seeing you again {logged_customer['first_name']}", 
                        f"Forgot to make dinner again huh? Not surprised {logged_customer['first_name']}",  
                        f"You still came back despite your review ... {logged_customer['first_name']}",
                        f"Not you again ... welcome back {logged_customer['first_name']}", 
                        f"You actually came back again? Hey {logged_customer['first_name']}", 
                        f"You better delete that negative review {logged_customer['first_name']}"
                    ]
            return random.choice(welcome)
    return None 
    
#welcoming the admin 


#if condition for ordering depending on the user state
@app.route("/order_now")
def order_now():
    if "user_id" in session: 
        return redirect(url_for("index"))
    else: 
        return redirect(url_for("login"))

#if condition for ordering depending on the user state
@app.route("/admin_in")
@admin_required
def admin_in():
    if "user_id" not in session: 
        return redirect(url_for("admin_login"))
    db = get_db()
    user = db.execute("SELECT is_admin FROM customers WHERE id = ?", (session["user_id"],)).fetchone()
    if user and user["is_admin"] == 1:
        return redirect(url_for("admin"))
    else: 
        return redirect(url_for("admin_login"))




#home 
@app.route("/" , methods=["GET", "POST"])
def index():
    welcome = greetingCustomer()
    message =  session.get('message')

    db = get_db()
    pizza = db.execute(""" SELECT * FROM pizzas;""").fetchall()

    return render_template("index.html",
                            pizza=pizza, 
                            welcome=welcome,
                            message=message, 
                        )

# pizzas menu that views all pizzas (filtering the pizzas based on the price)
"""
@app.route("/filter_pizza")
def pizzas():
    db = get_db()
    Filter = db.execute(" SELECT base_price 
                            FROM pizzas
                            ORDER BY base_price DESC; 
                            ").fetchall()
    return render_template("pizzas.html", pizza=pizza)
"""


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()

    if form.validate_on_submit():
        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = form.password.data
        password2 = form.password2.data
        phone_number = form.phone_number.data
        address = form.address.data

        db = get_db()
        conflict =  db.execute("SELECT * FROM customers WHERE email = ?", (email, )).fetchone()
        if conflict is not None:
            form.email.errors.append("Email already exists")
        else:
            db.execute("""INSERT INTO customers (first_name, last_name, email,password, phone_number, address)
                        VALUES (?,?,?,?,?,?) ;
                    """, (first_name, last_name, email,generate_password_hash(password), phone_number, address))
            db.commit()

            customer = db.execute("SELECT * FROM customers WHERE email = ?", (email, )).fetchone()
            session["user_id"] = customer["id"]
            if "user_id" in session: 
                return redirect(url_for("index"))
            else: 
                None

    return render_template("register.html",form=form)



@app.route("/login", methods=["GET", "POST"])
def login():
    form = Login()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        db = get_db()
        matching_email = db.execute("SELECT * FROM customers WHERE email = ?",(email,)).fetchone()

        if matching_email is None:
            form.email.errors.append("Email not found")

        elif not check_password_hash(matching_email["password"], password):
            form.password.errors.append("Incorrect password")
        else:
            session.clear()
            session["user_id"] = matching_email["id"]
            next_page = request.args.get("next")
            if not next_page:
                next_page = url_for("index")
            return redirect(next_page) 
    return render_template("login.html", form=form)



# logout 
@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("index"))



#used pizza and add to cart in the same route by using databases 
@app.route("/pizza/<int:pizza_id>", methods=["GET", "POST"])
def pizza(pizza_id):
    welcome = greetingCustomer()
    #getting the pizza part
    db = get_db()
    pizza = db.execute("SELECT * FROM pizzas WHERE pizza_id = ?;" ,( pizza_id ,)).fetchone()

    # adding to the cart part 
    form = Pizza()
    if form.validate_on_submit():
        if "user_id" not in session:
            return redirect(url_for("login"))
        customer_id = session["user_id"]


        # get the order_id or create it if you do not have it
        # if the order table is empty
        size = form.size.data
        size_price = pizza["base_price"]

        price_multiplier = 2.5
        if size == "Small (~8inch)":
            size_price = size_price + price_multiplier * 0
        elif size == "Medium (~14inch)":
            size_price = size_price + price_multiplier 
        else:
            size_price = size_price + price_multiplier * 2


                # get orders to see if its empty or there is something inside
        orders = db.execute("""SELECT * FROM orders  
                               WHERE customer_id = ? 
                               AND status = 'pending';""", (customer_id,)).fetchone()
        
        if orders is None: 
            db.execute("INSERT INTO orders (customer_id) VALUES (?) ", (customer_id,))
            db.commit()
            orders = db.execute(""" SELECT * FROM orders  
                                    WHERE customer_id = ? 
                                    AND status = 'pending';""" ,(customer_id,)).fetchone()
        # else update the orders table and increment it so it adds the next item
        order_id = orders["order_id"]

        pizza_exists = db.execute("""   SELECT * FROM order_details
                                        WHERE pizza_id = ? 
                                        AND order_id = ?
                                        AND size = ?
                                 ;""", (pizza_id ,order_id, size)).fetchone()
        
        if pizza_exists: 
            db.execute(""" UPDATE order_details
                            SET quantity = quantity + 1
                            WHERE pizza_id = ?
                            AND size = ?
                            AND order_id = ?; 
                       """ ,( pizza_id , size, order_id ))
        else: 
            db.execute(""" INSERT INTO order_details (order_id, pizza_id, quantity, size_price, size)
                           VALUES ( ? ,?, 1, ?, ?)
                       """, (order_id , pizza_id, size_price, size))
        db.commit()
        return redirect(url_for("cart"))
    return render_template("pizza.html", form=form, welcome=welcome, pizza=pizza) 


@app.route("/cart")
@login_required
def cart(): 
    order_id = 0
    welcome = greetingCustomer()
    customer_id = session["user_id"]
    db = get_db()
    orders = db.execute(""" SELECT 
                            od.quantity AS quantity, 
                            od.size_price AS size_price, 
                            od.order_id, 
                            od.size,
                            od.pizza_id, 
                            p.pizza_name AS pizza_name, 
                            p.base_price AS base_price,
                            p.pizza_id
                            FROM order_details AS od
                            JOIN pizzas AS p ON p.pizza_id = od.pizza_id 
                            JOIN orders AS o ON o.order_id = od.order_id
                            WHERE o.customer_id = ?
                            AND status = 'pending' """, (customer_id,)).fetchall()
    subtotal = 0
    total_price = 0
    for order in orders:
        order_id = order["order_id"]
        subtotal = order["size_price"]
        quantity = order["quantity"]
        total_price += subtotal * quantity 
    total_price = round(total_price,2)

    return render_template("cart.html", orders=orders, welcome=welcome, total_price=total_price, order_id=order_id)




# placing order/ check out route for checking out the pizza order.
@app.route("/place_order/<int:order_id>"  , methods=["GET", "POST"])
@login_required
def place_order(order_id): 
    welcome = greetingCustomer()
    customer_id = session["user_id"]
    db = get_db()

    #credit number code 
    orders = db.execute(""" SELECT 
                            od.quantity AS quantity, 
                            od.size_price AS size_price, 
                            od.order_id, 
                            od.size,
                            od.pizza_id, 
                            p.pizza_name AS pizza_name, 
                            p.base_price AS base_price,
                            p.pizza_id
                            FROM order_details AS od
                            JOIN pizzas AS p ON p.pizza_id = od.pizza_id 
                            JOIN orders AS o ON o.order_id = od.order_id
                            WHERE o.customer_id = ?
                            AND status = 'pending' """, (customer_id,)).fetchall()


    total_price = 0
    for order in orders:
        order_id = order["order_id"]
        subtotal = order["size_price"]
        quantity = order["quantity"]            
        total_price += subtotal * quantity 
    total_price = round(total_price,2)

    # promo_code calculation 
    promo_discount = None
    promo_code = session.get('promo_code')
    if promo_code: 
        discount = 0.85
        total_price = round(total_price * discount,2)
        promo_discount =  f"Promo code successfully applied"

        session.pop('promo_code')

    form = CheckOut()
    if form.validate_on_submit():
        code = form.code.data
        security_number = form.security_number.data
        db.execute("""UPDATE orders SET status = 'done'  WHERE customer_id = ? AND order_id = ?  """,(customer_id,order_id))
        db.commit()

        message = ["Your order have been successfully placed! ", 
                    "Your pizza is on the way!", 
                    "Order is confirmed!",
                    "Order successfully placed.We are on the way! ", 
                    " Your pizza will be ready at your door steps in 15minutes!"]
        session['message'] =  random.choice(message)
        return redirect(url_for("index"))

    return render_template("place_order.html", 
                            orders=orders,
                            promo_code = promo_code, 
                            welcome=welcome, 
                            form=form, 
                            total_price=total_price)
# promo code route 
# promo_code route 
@app.route("/promoCode", methods=["GET", "POST"])
@login_required
def promoCode():
    welcome = greetingCustomer()
    form = PromoCode(order_id)
    if form.validate_on_submit():
        code = form.code.data
        db = get_db()
        promo_code = db.execute("SELECT * FROM PromoCode WHERE code = ?", (code,)).fetchone()
        
        if promo_code is None:
            form.code.errors.append("Promo Code not valid")
        else:
            #saving promo in sessions to use it again in my cart calculations (big brain)
            session['promo_code'] = promo_code['code']

            return redirect(url_for("place_order, order_id=order_id"))
    return render_template("promoCode.html", form=form, welcome=welcome)





# cart history --- STILL BROKEN --- (FIXED)

@app.route("/order_history")
@login_required
def order_history():
    welcome = greetingCustomer()
    deleted_order = session.pop('deleted_order', None)

    customer_id = session["user_id"]
    db = get_db()
    orders = db.execute(""" SELECT 
                            od.quantity AS quantity, 
                            od.size_price AS size_price, 
                            od.order_id, 
                            od.size,
                            o.order_date,
                            od.pizza_id, 
                            p.pizza_name AS pizza_name, 
                            p.base_price AS base_price,
                            p.pizza_id
                            FROM order_details AS od
                            JOIN pizzas AS p ON p.pizza_id = od.pizza_id 
                            JOIN orders AS o ON o.order_id = od.order_id
                            WHERE o.customer_id = ?
                            AND status = 'done'
                            ORDER BY o.order_date DESC; """, (customer_id,)).fetchall()


    total_price = 0
    for order in orders:
        order_id = order["order_id"]
        subtotal = order["size_price"]
        quantity = order["quantity"]            
        total_price += subtotal * quantity 
    total_price = round(total_price,2)




    return render_template("order_history.html",
                            orders=orders,  
                            welcome=welcome, 
                            deleted_order=deleted_order,
                            total_price=total_price)


# do a sub query
# incrementing the items in the cart 
@app.route("/add_item/<int:order_id>/<int:pizza_id>/<size>")
@login_required
def add_item(order_id,pizza_id, size):
        db = get_db()
        
        db.execute("""  UPDATE order_details  
                        SET quantity = quantity + 1
                        WHERE order_id = ? AND pizza_id = ? AND size = ?
                    """, (order_id,pizza_id, size))
        db.commit()

        return redirect(url_for("cart"))


# decrementing the items in the cart 
@app.route("/delete_item/<int:order_id>/<int:pizza_id>/<size>")
@login_required
def delete_item(order_id, pizza_id, size):
    pizza
    customer_id = session["user_id"]
    db = get_db()
    db.execute("""  UPDATE order_details  
                        SET quantity = quantity - 1
                        WHERE order_id = ? AND pizza_id = ? AND size = ?
                        AND quantity > 0; 
                    """, (order_id,pizza_id, size))
    db.commit()
    return redirect(url_for("cart"))




# delete cart 
@app.route("/delete_cart/<int:order_id>", methods=["GET", "POST"])
@login_required
def delete_cart(order_id):
    customer_id = session["user_id"]
    db = get_db()
    if order_id == 0:
        return redirect(url_for("index"))

    db.execute("DELETE FROM order_details WHERE  order_id = ?" ,( order_id, ))
    db.execute("DELETE FROM orders WHERE order_id = ?" ,( order_id, ))

    db.commit()
    return redirect(url_for("index"))


# customer deleting their own review ONLY 
@app.route("/delete_order_history/<int:order_id>")
@login_required
def delete_order_history(order_id):
    customer_id = session["user_id"]
    db = get_db()
    db.execute(" DELETE FROM order_details WHERE order_id = ?" ,( order_id, ))
    db.execute ("DELETE FROM orders WHERE order_id = ? AND customer_id = ?",(order_id, customer_id))
    db.commit()
    session['deleted_order'] = "Order history has been successfully deleted"
    return redirect(url_for("order_history"))








# Reviews routes 

#viewing the reviews 
@app.route("/view_reviews")
def view_reviews():
    welcome = greetingCustomer()
    message =  session.pop('message', None)
    deleted_message = session.pop('deleted_message', None)


    db = get_db()
    reviews = db.execute("""SELECT reviews.*, 
                            customers.first_name, 
                            customers.last_name, 
                            customers.email
                            FROM reviews 
                            JOIN customers ON reviews.customer_id = customers.id
                            ORDER BY reviews.created_at DESC;
                        """).fetchall()

    return render_template("view_reviews.html", 
                            reviews=reviews, 
                            welcome=welcome, 
                            message=message, 
                            deleted_message=deleted_message,
                        ) 



# customer submitting the review 
@app.route("/submit_reviews", methods=["GET", "POST"])
@login_required
def submit_reviews():
    welcome = greetingCustomer()
    form = SubmitReviews()
    if form.validate_on_submit():
        review = form.review.data
        rating = form.rating.data
        customer_id = session["user_id"]
        db = get_db()
        db.execute("""INSERT INTO reviews (review, rating, customer_id)
                        VALUES (?,?,?) ;
                    """, (review,rating,customer_id))
        db.commit()
        return redirect(url_for("view_reviews"))
    return render_template("reviews.html", form=form, welcome=welcome) 


# replying back to customers 
@app.route("/reply_reviews/<int:review_id>", methods=["GET", "POST"])
@login_required
def reply_reviews(review_id):
    customer_id = session["user_id"]
    welcome = greetingCustomer()
    form = ReplyReviews()

    if form.validate_on_submit():
        reply = form.reply.data
        if reply is None:
            form.reply.errors.append("Reply can not be empty")
            return redirect(url_for("view_reviews"))
        else: 
            db = get_db()
            reply =  db.execute("""INSERT INTO review_reply (reply, review_id, customer_id)
                                    VALUES (?,?,?);
                                """,(reply,review_id, customer_id))
            db.commit()
        session['reply'] = "Reply successfully posts!" 
    return redirect(url_for("view_reviews"))


# customer deleting their own review ONLY 
@app.route("/delete_review/<int:review_id>")
@login_required
def delete_review(review_id):
    customer_id = session["user_id"]
    db = get_db()
    delete = db.execute(""" DELETE FROM reviews 
                            WHERE review_id = ? 
                            AND customer_id = ?""" ,( review_id, customer_id ))
    db.commit()
    session['deleted_message'] = "Review successfully deleted"
    return redirect(url_for("view_reviews"))


#customer editing their own reviews ONLY 
@app.route("/edit_review/<int:review_id>", methods=["GET", "POST"])
@login_required
def edit_review(review_id):
    welcome = greetingCustomer()
    form = SubmitReviews()
    db = get_db()
    customer_id = session["user_id"]

    review = db.execute("SELECT * FROM reviews WHERE review_id = ? AND customer_id = ?",(review_id, customer_id)).fetchone()
    if not review:
        return redirect(url_for("view_reviews"))
    if form.validate_on_submit():
        new_review = form.review.data
        new_rating = form.rating.data
        db.execute("""  UPDATE reviews
                        SET review = ? , rating = ?
                        WHERE review_id = ? 
                        AND customer_id = ?""" ,( new_review,new_rating, review_id, customer_id ))
        db.commit()
        session['message'] = "Review successfully edited"
        return redirect(url_for("view_reviews"))
    form.review.data = review['review']
    form.rating.data = review['rating']
    return render_template("edit_review.html", form=form, review=review, welcome=welcome)


# reply to a review 
#likes 






# customer viewing their own review history ONLY 
@app.route("/review_history")
@login_required
def review_history():
    welcome = greetingCustomer()
    customer_id = session["user_id"]
    db = get_db()
    history = db.execute("""SELECT reviews.*, 
                            customers.first_name, 
                            customers.last_name, 
                            customers.email
                            FROM reviews 
                            JOIN customers ON reviews.customer_id = customers.id
                            WHERE reviews.customer_id = ? 
                            ORDER BY reviews.created_at DESC;
                        """,(customer_id ,)).fetchall()
    return render_template("review_history.html",  history=history, welcome=welcome)




# account route 
@app.route("/view_account")
@login_required
def view_account():
    welcome = greetingCustomer()
    customer_id = session["user_id"]
    db = get_db()
    account = db.execute("""SELECT * FROM customers WHERE id = ?;""",(customer_id,)).fetchall()
    return render_template("view_account.html", account=account, welcome=welcome) 

#editing the account 
@app.route("/edit_account", methods=["GET", "POST"])
@login_required
def edit_account():
    welcome = greetingCustomer()
    form = RegisterForm()
    db = get_db()
    customer_id = session["user_id"]
    account = db.execute("""SELECT * FROM customers WHERE id = ?;""",(customer_id,)).fetchone()
    if not account:
        return redirect(url_for("view_account"))

    if form.validate_on_submit():
        new_first_name = form.first_name.data
        new_last_name = form.last_name.data
        new_email = form.email.data
        new_password = form.password.data
        new_phone_number = form.phone_number.data
        new_address = form.address.data
        db.execute("""UPDATE customers
                     SET first_name = ? , 
                     last_name = ?, 
                     email = ?, 
                     password = ?, 
                     phone_number = ?,
                     address = ? 
                     WHERE id = ? 
                    """ ,( new_first_name, new_last_name, new_email,generate_password_hash(new_password), new_phone_number, new_address, customer_id ))
        db.commit()
        return redirect(url_for("view_account"))
    form.first_name.data = account['first_name']
    form.last_name.data = account['last_name']
    form.email.data = account['email']
    form.password.data = account['password']
    form.address.data = account['address']
    return render_template("edit_account.html", form=form, account=account, welcome=welcome)


# delete the account 
@app.route("/delete_account")
@login_required
def delete_account():
    customer_id = session["user_id"]
    db = get_db()
    db.execute("""DELETE FROM customers
                  WHERE id = ? 
                """ ,( customer_id ,))
    db.commit()
    return redirect(url_for("index"))


@app.route("/credits")
def credits():
    return render_template("credits.html")





@app.route("/admin")
@login_required
def admin():
    return render_template("admin_index.html")


# admin log in
@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    form = AdminLogin()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        db = get_db()

        admin = db.execute("SELECT id, email, password FROM customers WHERE email = ? AND is_admin = 1;",(email,)).fetchone()

        if admin is None:
            form.email.errors.append("Only admin")
        elif not check_password_hash(admin["password"], password):
            form.password.errors.append("Incorrect password")
        else:
            session.clear()
            session["user_id"] = admin["id"]
            return redirect(url_for("admin"))
    return render_template("admin_login.html", form=form)

# account route 
@app.route("/view_customer_accounts")
@admin_required
def view_customer_accounts():
    ban_account = session.pop('ban_account', None)
    db = get_db()
    customers_account = db.execute("""SELECT * FROM customers WHERE is_admin = 0 ;""",).fetchall()
    return render_template("view_customer_accounts.html", customers_account=customers_account, ban_account=ban_account) 

#admin viewing customer's order history 
# account route 
@app.route("/customers_order_history")
@admin_required
def customers_order_history():
    db = get_db()
    orders = db.execute(""" SELECT 
                            od.quantity AS quantity, 
                            od.size_price AS size_price, 
                            od.order_id, 
                            od.size,
                            o.order_date,
                            od.pizza_id,
                            c.first_name,
                            c.last_name, 
                            c.id,
                            c.is_admin, 
                            p.pizza_name AS pizza_name, 
                            p.base_price AS base_price,
                            p.pizza_id
                            FROM order_details AS od
                            JOIN pizzas AS p ON p.pizza_id = od.pizza_id 
                            JOIN orders AS o ON o.order_id = od.order_id
                            JOIN customers AS c on c.id = o.customer_id
                            WHERE c.is_admin = 0
                            AND status = 'done'
                            ORDER BY o.order_date DESC; """).fetchall()


    total_price = 0
    for order in orders:
        order_id = order["order_id"]
        subtotal = order["size_price"]
        quantity = order["quantity"]            
        total_price += subtotal * quantity 
    total_price = round(total_price,2)
    return render_template("customer_order_history.html", orders=orders, total_price=total_price) 


#admin banning/deleting customer account because he is mean :(
# delete the account 
@app.route("/ban_account/<int:customer_id>")
@admin_required
def ban_account(customer_id):
    db = get_db()
    db.execute("""DELETE FROM customers
                  WHERE is_admin = 0
                  AND id = ?
                """ ,( customer_id ,))
    db.commit()
    session['ban_account'] = "customer successfully banned!"
    return redirect(url_for("view_customer_accounts"))

# admin viewing reviews 
@app.route("/admin_view_reviews")
@admin_required
def admin_view_reviews():
    deleted_message = session.pop('deleted_message', None)
    db = get_db()
    reviews = db.execute("""SELECT reviews.*, 
                            customers.first_name, 
                            customers.last_name, 
                            customers.email
                            FROM reviews 
                            JOIN customers ON reviews.customer_id = customers.id
                            WHERE is_admin = 0
                            ORDER BY reviews.created_at DESC;
                        """).fetchall()

    return render_template("admin_view_reviews.html", 
                            reviews=reviews, 
                            deleted_message=deleted_message,
                        ) 

#admin deleting reviews 

# customer deleting their own review ONLY 
@app.route("/admin_delete_review/<int:review_id>")
@admin_required
def admin_delete_review(review_id):
    db = get_db()
    delete = db.execute(""" DELETE FROM reviews 
                            WHERE review_id = ? 
                        """ ,( review_id,))
    db.commit()
    session['deleted_message'] = "Review successfully deleted"
    return redirect(url_for("admin_view_reviews"))



# admin edit the menu because the prices are insane 
#customer editing their own reviews ONLY 

# first get the admin_menu page 
@app.route("/admin_edit_menu")
@login_required
def admin_edit_menu():
    edit_pizza = session.pop('edit_pizza', None)

    db = get_db()
    pizza = db.execute("SELECT * FROM pizzas;").fetchall()
    return render_template("admin_edit_menu.html", pizza=pizza, edit_pizza=edit_pizza)



@app.route("/update_pizza/<int:pizza_id>", methods=["GET", "POST"])
@login_required
def update_pizza(pizza_id):
    db = get_db()
    pizza = db.execute("SELECT * FROM pizzas WHERE pizza_id = ? ;", (pizza_id,)).fetchone()

    form = EditMenu()
    if form.validate_on_submit():
        pizza_name = form. pizza_name.data
        base_price = float(form.base_price.data)
        description = form.description .data
        db.execute("""  UPDATE pizzas 
                        SET pizza_name = ? , base_price = ?, description = ?
                        WHERE pizza_id = ?
                  """ ,( pizza_name ,base_price, description, pizza_id ))
        db.commit()
        session['edit_pizza'] = "Pizza successfully edited"
        return redirect(url_for("admin_edit_menu"))
    form.pizza_name.data = pizza['pizza_name']
    form.base_price.data = pizza['base_price']
    form.description.data = pizza['description']
    return render_template("update_pizza.html", form=form, pizza=pizza)

#admin pizza see details 
#the admin pizza menu is different from the normal pizza menu
@app.route("/admin_pizza/<int:pizza_id>", methods=["GET", "POST"])
def admin_pizza(pizza_id):
    db = get_db()
    pizza = db.execute("SELECT * FROM pizzas WHERE pizza_id = ?;" ,( pizza_id ,)).fetchone()
    return render_template("admin_pizza.html", pizza=pizza)
