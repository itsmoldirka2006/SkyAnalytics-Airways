CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10,2),
    stock_quantity INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    product_id INTEGER REFERENCES products(id),
    quantity INTEGER,
    total_amount DECIMAL(10,2),
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO users (username, email) VALUES 
('alice_johnson', 'alice@example.com'),
('bob_smith', 'bob@example.com'),
('carol_davis', 'carol@example.com'),
('david_wilson', 'david@example.com')
ON CONFLICT (username) DO NOTHING;

INSERT INTO products (name, price, stock_quantity) VALUES 
('Gaming Laptop', 1299.99, 15),
('Wireless Mouse', 35.50, 100),
('Mechanical Keyboard', 89.99, 45),
('Monitor 24"', 199.99, 25),
('Webcam HD', 45.75, 60)
ON CONFLICT DO NOTHING;

INSERT INTO orders (user_id, product_id, quantity, total_amount, status) VALUES 
(1, 1, 1, 1299.99, 'completed'),
(2, 2, 2, 71.00, 'completed'),
(3, 3, 1, 89.99, 'pending'),
(4, 4, 1, 199.99, 'shipped'),
(1, 5, 1, 45.75, 'completed')
ON CONFLICT DO NOTHING;

CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders(user_id);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);