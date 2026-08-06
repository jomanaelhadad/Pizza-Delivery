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



-- reviews tables 
DROP TABLE IF EXISTS reviews;
CREATE TABLE reviews(
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    rating INTEGER NOT NULL, 
    review TEXT NOT NULL, 
    likes INTEGER DEFAULT 0, 
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);


DROP TABLE IF EXISTS review_likes;
CREATE TABLE review_likes(
	review_id INTEGER NOT NULL, 
    customer_id INTEGER NOT NULL,
    
    PRIMARY KEY(review_id, customer_id),
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (review_id) REFERENCES reviews(review_id) 
);


DROP TABLE IF EXISTS reviews_reply;
CREATE TABLE reviews_reply(
    reply_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    review_id INTEGER NOT NULL, 
    reply TEXT NOT NULL,  
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (customer_id) REFERENCES customers(id),
    FOREIGN KEY (review_id) REFERENCES reviews(review_id)
);



-- orders table 
DROP TABLE IF EXISTS order_details; 
DROP TABLE IF EXISTS orders;

CREATE TABLE orders(
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    status TEXT DEFAULT 'pending',

    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

CREATE TABLE order_details(
    pizza_id INTEGER NOT NULL,
    order_id INTEGER NOT NULL, 
    quantity INTEGER NOT NULL,
    size_price REAl NOT NULL,
    size TEXT NOT NULL, 

    PRIMARY KEY (pizza_id, order_id, size),
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (pizza_id) REFERENCES pizzas(pizza_id)
); 


DROP TABLE IF EXISTS pizzas;
CREATE TABLE pizzas(
    pizza_id INTEGER PRIMARY KEY AUTOINCREMENT,
    pizza_name TEXT NOT NULL, 
    description TEXT NOT NULL, 
    images TEXT NOT NULL,  
    base_price REAL NOT NULL
);




-- promo code 
DROP TABLE IF EXISTS promoCode;
CREATE TABLE promoCode(
    code_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL, 
    FOREIGN KEY (code_id) REFERENCES customers(id)
);



-- inserting into the db

INSERT INTO pizzas(pizza_name, base_price, description, images )
VALUES  ('Classic Margherita', 8.99, 'Classic homemade tomato sauce with fresh mozzarella and handpicked basil leaves', 'margherita.jpg'), 
        ('Pepperoni Passion', 10.99, 'Classic homemade tomato sauce with spicy beef pepperoni slices', 'pepperoni.jpg'),
        ('Hawaiian Heat', 11.99, 'Classic Hawaiian pizza with a twist of extra heat', 'hawaiian.jpg'),
        ('Veggie Venture', 9.99, 'Veggie dream of Mushrooms, pesto sauce, onions, peppers and fresh basil leaves', 'veggie.jpg'), 
        ('Meat Lovers' , 12.99, 'Quality deli meats including smoked pepperoni and turkey ', 'meat.jpg'),
        ('Sicilian', 12.99, 'Extra crispy bottom pizza made with traditional tomato sauce, onions, anchovies using caciocavallo and breadcrumbs ', 'sicilian.jpg'),
        ('BBQ Chicken', 12.99, 'Smoked BBQ chicken stripes with a slight spicy BBQ glaze topped with fresh mozzarella cheese', 'chicken.jpg'),
        ('Four Cheese', 13.99, 'Our 4 season cheese special of caciocavallo, mozzarella,parmesan and blue cheese ', 'FourCheese.jpg'),
        ('Neapolitan', 13.99, 'Our classic italian pizza with handpicked basils and soft thin dough', 'neapolitan.jpg'),
        ('Diavola', 12.99, 'Our Signiture hand stretched, stone-backed pizza topped with creamy mozzarella and sweet tomato sauce', 'diavola.jpg'),
        ('Tuna Thunder', 12.99, 'Fresh tuna with spicy seafood pizza sauce and fresh mozzarella cheese', 'tuna.jpg'),
        ('Classic Seafood', 13.99, 'Our classic seafood special with freshly handpicked prawns, smoked salmon and salty spicy anchovies ', 'seafood.jpg');
        
INSERT INTO promoCode(code)
VALUES ('Wombats124'),
       ('BabyWombat_67');


