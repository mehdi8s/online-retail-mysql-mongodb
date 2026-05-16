DROP TABLE IF EXISTS bench_lines;

CREATE TABLE bench_lines (
    id BIGINT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    invoice_no VARCHAR(30) NOT NULL,
    stock_code VARCHAR(20) NOT NULL,
    quantity INT NOT NULL,
    invoice_date DATETIME NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    customer_id INT NOT NULL,
    country VARCHAR(100) NOT NULL,
    INDEX idx_invoice_no (invoice_no),
    INDEX idx_customer_id (customer_id),
    INDEX idx_invoice_date (invoice_date),
    INDEX idx_unit_price (unit_price)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
