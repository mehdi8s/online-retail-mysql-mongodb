DROP TABLE IF EXISTS invoice_lines;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id INT NOT NULL PRIMARY KEY,
    country VARCHAR(100) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE products (
    stock_code VARCHAR(20) NOT NULL PRIMARY KEY,
    description VARCHAR(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE invoice_lines (
    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    invoice_no VARCHAR(20) NOT NULL,
    stock_code VARCHAR(20) NOT NULL,
    quantity INT NOT NULL,
    invoice_date DATETIME NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    customer_id INT NOT NULL,
    country VARCHAR(100) NOT NULL,
    INDEX idx_invoice_no (invoice_no),
    INDEX idx_customer_id (customer_id),
    INDEX idx_invoice_date (invoice_date),
    INDEX idx_unit_price (unit_price),
    CONSTRAINT fk_lines_customer FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
    CONSTRAINT fk_lines_product FOREIGN KEY (stock_code) REFERENCES products (stock_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
