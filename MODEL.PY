import psycopg2
import time

class Model:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                dbname='art-marketplace-platform',
                user='postgres',
                password='1234',
                host='localhost',
                port=5432
            )
            self.create_tables()
        except Exception as e:
            print(f"Error connecting to the database: {e}")

    def create_tables(self):
        try:
            with self.conn.cursor() as c:
                c.execute('''
                    CREATE TABLE IF NOT EXISTS category (
                        category_id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL
                    );
                ''')

                c.execute('''
                    CREATE TABLE IF NOT EXISTS seller (
                        seller_id SERIAL PRIMARY KEY,
                        name VARCHAR(255) NOT NULL,
                        number INTEGER NOT NULL
                    );
                ''')

                c.execute('''
                    CREATE TABLE IF NOT EXISTS product (
                        product_id SERIAL PRIMARY KEY,
                        name VARCHAR(20) NOT NULL,
                        category_id INTEGER NOT NULL,
                        seller_id INTEGER NOT NULL,
                        CONSTRAINT p2c FOREIGN KEY (category_id) REFERENCES category (category_id),
                        CONSTRAINT p2s FOREIGN KEY (seller_id) REFERENCES seller (seller_id)
                    );
                ''')
                self.conn.commit()
        except Exception as e:
            print(f"Error creating tables: {e}")

    def add_category(self, name):
        try:
            with self.conn.cursor() as c:
                c.execute('INSERT INTO category (name) VALUES (%s)', (name,))
                self.conn.commit()
        except Exception as e:
            print(f"Error adding category: {e}")

    def update_category(self, category_id, name):
        try:
            with self.conn.cursor() as c:
                c.execute('UPDATE category SET name=%s WHERE category_id=%s', (name, category_id))
                self.conn.commit()
        except Exception as e:
            print(f"Error updating category: {e}")

    def delete_category(self, category_id):
        try:
            with self.conn.cursor() as c:
                c.execute('DELETE FROM category WHERE category_id=%s', (category_id,))
                self.conn.commit()
        except Exception as e:
            print(f"Error deleting category: {e}")

    def get_all_categories(self):
        try:
            with self.conn.cursor() as c:
                c.execute('SELECT * FROM category')
                return c.fetchall()
        except Exception as e:
            print(f"Error retrieving categories: {e}")
            return []

    def add_seller(self, name, number):
        try:
            with self.conn.cursor() as c:
                c.execute('INSERT INTO seller (name, number) VALUES (%s, %s)', (name, number))
                self.conn.commit()
        except Exception as e:
            print(f"Error adding seller: {e}")

    def update_seller(self, seller_id, name, number):
        try:
            with self.conn.cursor() as c:
                c.execute('UPDATE seller SET name=%s, number=%s WHERE seller_id=%s', (name, number, seller_id))
                self.conn.commit()
        except Exception as e:
            print(f"Error updating seller: {e}")

    def delete_seller(self, seller_id):
        try:
            with self.conn.cursor() as c:
                c.execute('DELETE FROM seller WHERE seller_id=%s', (seller_id,))
                self.conn.commit()
        except Exception as e:
            print(f"Error deleting seller: {e}")

    def get_all_sellers(self):
        try:
            with self.conn.cursor() as c:
                c.execute('SELECT * FROM seller')
                return c.fetchall()
        except Exception as e:
            print(f"Error retrieving sellers: {e}")
            return []

    def add_product(self, name, category_id, seller_id):
        try:
            with self.conn.cursor() as c:
                c.execute(
                    'INSERT INTO product (name, category_id, seller_id) VALUES (%s, %s, %s)',
                    (name, category_id, seller_id)
                )
                self.conn.commit()
        except Exception as e:
            print(f"Error adding product: {e}")

    def update_product(self, product_id, name, category_id, seller_id):
        try:
            with self.conn.cursor() as c:
                c.execute(
                    'UPDATE product SET name=%s, category_id=%s, seller_id=%s WHERE product_id=%s',
                    (name, category_id, seller_id, product_id)
                )
                self.conn.commit()
        except Exception as e:
            print(f"Error updating product: {e}")

    def delete_product(self, product_id):
        try:
            with self.conn.cursor() as c:
                c.execute('DELETE FROM product WHERE product_id=%s', (product_id,))
                self.conn.commit()
        except Exception as e:
            print(f"Error deleting product: {e}")

    def get_all_products(self):
        try:
            with self.conn.cursor() as c:
                c.execute('SELECT * FROM product')
                return c.fetchall()
        except Exception as e:
            print(f"Error retrieving products: {e}")
            return []
    
    def generate_sample_data(self):
        try:
            with self.conn.cursor() as c:
                # Generate sample categories
                c.execute('''
                    INSERT INTO category (name)
                    SELECT 'Category ' || i
                    FROM generate_series(1, 10) AS i
                    ON CONFLICT DO NOTHING;
                ''')

                # Generate sample sellers
                c.execute('''
                    INSERT INTO seller (name, number)
                    SELECT 'Seller ' || i, (1000000000 + i)
                    FROM generate_series(1, 10) AS i
                    ON CONFLICT DO NOTHING;
                ''')

                # Generate sample products with valid foreign keys
                c.execute('''
                    INSERT INTO product (name, category_id, seller_id)
                    SELECT 'Product ' || i, 
                           (SELECT category_id FROM category ORDER BY RANDOM() LIMIT 1),
                           (SELECT seller_id FROM seller ORDER BY RANDOM() LIMIT 1)
                    FROM generate_series(1, 20) AS i
                    ON CONFLICT DO NOTHING;
                ''')

                self.conn.commit()
        except Exception as e:
            print(f"Error generating sample data: {e}")
    
    def query_top_categories(self, min_products):
        try:
            start_time = time.time()
            with self.conn.cursor() as c:
                c.execute('''
                    SELECT category.name, COUNT(product.product_id) AS product_count
                    FROM category
                    JOIN product ON category.category_id = product.category_id
                    GROUP BY category.name
                    HAVING COUNT(product.product_id) >= %s
                    ORDER BY product_count DESC;
                ''', (min_products,))
                results = c.fetchall()
            execution_time = (time.time() - start_time) * 1000
            return results, execution_time
        except Exception as e:
            print(f"Error executing query: {e}")
            return [], 0

    def query_seller_products(self, seller_id):
        try:
            start_time = time.time()
            with self.conn.cursor() as c:
                c.execute('''
                    SELECT seller.name, product.name
                    FROM seller
                    JOIN product ON seller.seller_id = product.seller_id
                    WHERE seller.seller_id = %s
                    ORDER BY product.name;
                ''', (seller_id,))
                results = c.fetchall()
            execution_time = (time.time() - start_time) * 1000
            return results, execution_time
        except Exception as e:
            print(f"Error executing query: {e}")
            return [], 0

    def query_category_seller_summary(self):
        try:
            start_time = time.time()
            with self.conn.cursor() as c:
                c.execute('''
                    SELECT category.name AS category_name, seller.name AS seller_name, COUNT(product.product_id) AS product_count
                    FROM category
                    JOIN product ON category.category_id = product.category_id
                    JOIN seller ON seller.seller_id = product.seller_id
                    GROUP BY category.name, seller.name
                    ORDER BY category_name, seller_name;
                ''')
                results = c.fetchall()
            execution_time = (time.time() - start_time) * 1000
            return results, execution_time
        except Exception as e:
            print(f"Error executing query: {e}")
            return [], 0
