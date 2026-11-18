-- Hosted MAUDE slice for the Invalid Bot demo.
-- One row is one device-event report. There is no total-runs column.
-- is_invalid_type is true only when a product_problem maps to an invalid type.
-- The 2% run-level promise is not a column and is not estimable from this table.

CREATE TABLE IF NOT EXISTS maude_report (
    mdr_report_key TEXT NOT NULL,
    product_code TEXT NOT NULL,
    date_received DATE NOT NULL,
    date_of_event DATE,
    event_type TEXT NOT NULL DEFAULT '',
    manufacturer_name TEXT NOT NULL,
    manufacturer_raw TEXT NOT NULL DEFAULT '',
    brand_name TEXT NOT NULL DEFAULT '',
    generic_name TEXT NOT NULL DEFAULT '',
    model_number TEXT NOT NULL DEFAULT '',
    catalog_number TEXT NOT NULL DEFAULT '',
    lot_number TEXT NOT NULL DEFAULT '',
    device_operator TEXT NOT NULL DEFAULT '',
    is_invalid_type BOOLEAN NOT NULL,
    invalid_code TEXT NOT NULL DEFAULT '',
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (mdr_report_key, product_code)
);

CREATE TABLE IF NOT EXISTS maude_problem (
    mdr_report_key TEXT NOT NULL,
    product_code TEXT NOT NULL,
    product_problem TEXT NOT NULL,
    invalid_code TEXT NOT NULL DEFAULT '',
    PRIMARY KEY (mdr_report_key, product_code, product_problem),
    FOREIGN KEY (mdr_report_key, product_code)
        REFERENCES maude_report (mdr_report_key, product_code)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS load_manifest (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    extracted_at TIMESTAMPTZ,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    api_calls INTEGER NOT NULL,
    report_count INTEGER NOT NULL,
    product_codes TEXT NOT NULL,
    window_start DATE NOT NULL,
    window_end DATE NOT NULL,
    denominator TEXT NOT NULL,
    cache_dir TEXT NOT NULL DEFAULT '',
    note TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS maude_report_code_date_idx
    ON maude_report (product_code, date_received);

CREATE INDEX IF NOT EXISTS maude_report_manufacturer_idx
    ON maude_report (manufacturer_name);

CREATE INDEX IF NOT EXISTS maude_report_invalid_idx
    ON maude_report (product_code, is_invalid_type);
