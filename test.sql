SELECT * FROM pizzas;

SELECT * FROM reviews; 
SELECT * FROM customers;

SELECT * FROM promoCode; 

SELECT * FROM customers; 

SELECT reviews.*, customers.first_name, customers.last_name, customers.email
FROM reviews 
JOIN customers ON reviews.customer_id = customers.id
ORDER BY reviews.created_at DESC; 


SELECT * FROM orders;

SELECT base_price 
FROM pizzas
ORDER BY base_price DESC; 



SELECT orders.*, pizzas.pizza_name as name, 
      SUM(pizzas.base_price * orders.quantity)as total_price
FROM orders 
JOIN pizzas ON orders.pizza_id = pizzas.pizza_id
WHERE pizzas.pizza_name = "Pepperoni Passion"; 

SELECT * FROM customers;



-- @app.route("/check_out")
-- def check_out():
--     welcome = greetingCustomer()
--     customer_id = session["user_id"]
--     db = get_db()
--     cart = db.execute("""SELECT orders.*, customers.* , pizzas.pizza_name, pizzas.base_price
--                          FROM orders 
--                          JOIN customers ON orders.customer_id = customers.id
--                          JOIN pizzas ON orders.pizza_id = pizzas.pizza_id
--                       """).fetchall()
--     return render_template("check_out.html", cart=cart, welcome=welcome) 
-- 

SELECT * FROM reviews LIMIT 1;

SELECT * FROM customers;

SELECT * FROM pizzas;






SELECT reviews.likes,
reviews.customer_id, 
customers.id
FROM reviews
JOIN customers ON reviews.customer_id = customers.id
WHERE reviews.likes = 13


DROP TABLE IF EXISTS admin;

CREATE TABLE admin(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL, 
    phone_number TEXT NOT NULL,
    address TEXT NOT NULL
);

INSERT INTO admin
VALUES ('Derek', 'Bridge', 'derekbridge@123.com', '1234', '029-0938-3094', '85 SpringRoll Street'); 

SELECT * FROM admin; 

SELECT * FROM pizzas;
#
SELECT cart FROM orders;
SELECT * FROM customers; 


SELECT DISTINCT 
orders.*,
customers.*, 
pizzas.*
FROM orders 
JOIN customers ON orders.customer_id = customers.id
JOIN pizzas ON orders.order_id = pizzas.pizza_id
WHERE orders.customer_id = 1; 




ALTER TABLE order_details ADD size TEXT NOT NULL DEFAULT '' ; 
ALTER TABLE order_details RENAME COLUMN total_price TO size_price; 


SELECT * FROM orders
WHERE customer_id = 1;


SELECT * FROM customers;


SELECT * FROM order_details;

DROP TABLE IF EXISTS customers;
CREATE TABLE customers(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL,
    password TEXT NOT NULL, 
    phone_number TEXT NOT NULL,
    address TEXT NOT NULL,
    is_admin INTEGER DEFAULT 0  
);

ALTER TABLE customers ADD COLUMN is_admin INTEGER DEFAULT 0;
UPDATE customers SET is_admin = 1 WHERE id = 2;

SELECT * FROM customers;
UPDATE customers SET is_admin = 1 WHERE email = 'derekbridge123@gmail.com';



