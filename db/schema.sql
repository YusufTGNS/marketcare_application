-- MarketCare icin temel SQLite semasi.
-- init_db.py eksik kolonlari calisma aninda tamamlar.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  role TEXT NOT NULL CHECK (role IN ('admin','personnel')),
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  last_login_at TEXT NULL
);

CREATE TABLE IF NOT EXISTS products (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL UNIQUE,
  barcode_value TEXT NOT NULL UNIQUE,
  unit_price REAL NOT NULL,
  vat_rate REAL NOT NULL DEFAULT 20,
  expiration_date TEXT NULL,
  image_path TEXT NULL,
  icon_path TEXT NULL,
  stock_qty INTEGER NOT NULL DEFAULT 0,
  critical_threshold INTEGER NOT NULL DEFAULT 10,
  is_active INTEGER NOT NULL DEFAULT 1,
  created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS stock_movements (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  product_id INTEGER NOT NULL,
  delta_qty INTEGER NOT NULL,
  movement_type TEXT NOT NULL CHECK (movement_type IN ('in','out')),
  qty_before INTEGER NOT NULL,
  qty_after INTEGER NOT NULL,
  note TEXT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  user_id INTEGER NOT NULL,
  FOREIGN KEY (product_id) REFERENCES products(id),
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS sales (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sale_no TEXT NOT NULL UNIQUE,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  created_by_user_id INTEGER NOT NULL,
  customer_name TEXT NULL,
  payment_type TEXT NULL,
  total_amount REAL NOT NULL,
  tax_amount REAL NOT NULL DEFAULT 0,
  grand_total REAL NOT NULL,
  pdf_slip_path TEXT NULL,
  pdf_invoice_path TEXT NULL,
  FOREIGN KEY (created_by_user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS sale_items (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sale_id INTEGER NOT NULL,
  product_id INTEGER NOT NULL,
  qty INTEGER NOT NULL,
  unit_price REAL NOT NULL,
  vat_rate REAL NOT NULL DEFAULT 20,
  tax_amount REAL NOT NULL DEFAULT 0,
  line_total REAL NOT NULL,
  FOREIGN KEY (sale_id) REFERENCES sales(id),
  FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Sik kullanilan sorgular icin indeksler
CREATE INDEX IF NOT EXISTS idx_products_barcode ON products(barcode_value);
CREATE INDEX IF NOT EXISTS idx_stock_movements_product ON stock_movements(product_id, created_at);
CREATE INDEX IF NOT EXISTS idx_sales_created_by ON sales(created_by_user_id, created_at);
CREATE INDEX IF NOT EXISTS idx_sale_items_sale ON sale_items(sale_id);
