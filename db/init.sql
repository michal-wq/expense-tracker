CREATE TABLE expenses (
    id UUID PRIMARY KEY,
    amount NUMERIC NOT NULL,
    category TEXT NOT NULL,
    date DATE NOT NULL
);
