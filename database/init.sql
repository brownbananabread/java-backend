-- Create users table
CREATE TABLE users (
    userId SERIAL PRIMARY KEY,
    email VARCHAR(50) UNIQUE NOT NULL,
    firstName VARCHAR(100) NOT NULL,
    lastName VARCHAR(50) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(10) CHECK (role IN ('admin', 'soleTrader', 'customer')) NOT NULL DEFAULT 'customer',
    serviceOffered VARCHAR(50) NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create listings table
CREATE TABLE listings (
    listingId SERIAL PRIMARY KEY,
    customerId INT REFERENCES users(userId),
    title VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    serviceRequired VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'active', -- active, completed
    location VARCHAR(100) NOT NULL,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create quotes table
CREATE TABLE quotes (
    quoteId SERIAL PRIMARY KEY,
    listingId INT REFERENCES listings(listingId),
    soleTraderId INT REFERENCES users(userId),
    customerId INT REFERENCES users(userId),
    description TEXT NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'pending', -- pending, accepted
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create ratings table
CREATE TABLE ratings (
    ratingId SERIAL PRIMARY KEY,
    receiverId INT REFERENCES users(userId), -- Fixed typo in column name
    senderId INT REFERENCES users(userId),
    rating INT CHECK (rating >= 1 AND rating <= 5), -- 5-star rating system
    description TEXT,
    createdAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample users first
INSERT INTO users (email, firstName, lastName, password, role, serviceOffered) VALUES
    ('john.smith@example.com', 'John', 'Smith', 'password123', 'admin', NULL),
    ('sarah.jones@example.com', 'Sarah', 'Jones', 'password456', 'customer', NULL),
    ('plumber.pro@example.com', 'Mike', 'Johnson', 'secure789', 'soleTrader', 'Plumbing'),
    ('electric.expert@example.com', 'David', 'Williams', 'secure101', 'soleTrader', 'Electrical'),
    ('carpenter.craft@example.com', 'James', 'Brown', 'secure202', 'soleTrader', 'Carpentry'),
    ('painter.perfect@example.com', 'Lisa', 'Davis', 'secure303', 'soleTrader', 'Painting'),
    ('lawn.care@example.com', 'Robert', 'Miller', 'secure404', 'soleTrader', 'Lawn Care');

-- Insert sample listings
INSERT INTO listings (customerId, title, description, serviceRequired, location) VALUES
    (1, 'Bathroom Sink Leak', 'My bathroom sink has been leaking for a few days and needs repair.', 'Plumbing', 'New York, NY'),
    (1, 'Kitchen Remodel', 'Looking for a skilled carpenter to remodel my kitchen cabinets.', 'Carpentry', 'New York, NY'),
    (2, 'House Painting', 'Need to paint the exterior of my 2-story house.', 'Painting', 'Los Angeles, CA'),
    (2, 'Electrical Outlet Installation', 'Need to install 5 new outlets in my home office.', 'Electrical', 'Los Angeles, CA'),
    (1, 'Lawn Mowing Service', 'Looking for regular lawn mowing for my 1/4 acre yard.', 'Lawn Care', 'Chicago, IL');

-- Insert sample quotes
INSERT INTO quotes (listingId, soleTraderId, customerId, description, price, date, status) VALUES
    (1, 3, 1, 'I can fix your bathroom sink leak. Will bring all necessary tools and parts.', 125.00, '2025-04-05', 'pending'),
    (2, 5, 1, 'I specialize in kitchen remodels and can help with your cabinets. Would need to see the space first.', 1500.00, '2025-04-10', 'pending'),
    (3, 6, 2, 'I offer professional painting services and can paint your house exterior. Price includes paint and supplies.', 2200.00, '2025-04-15', 'pending'),
    (4, 4, 2, 'I can install the 5 outlets in your home office. Price includes parts and labor.', 450.00, '2025-04-07', 'accepted'),
    (5, 7, 1, 'I provide weekly lawn mowing services. Price is per visit.', 45.00, '2025-04-20', 'pending');

-- Insert ratings after users have been created
INSERT INTO ratings (receiverId, senderId, rating, description) VALUES
    (3, 1, 5, 'Great service! Fixed my sink quickly.'),
    (4, 1, 4, 'Good job on the electrical work.'),
    (5, 2, 5, 'The kitchen remodel looks amazing!'),
    (6, 2, 3, 'The painting was okay, but could have been better.'),
    (7, 1, 5, 'Lawn care is always on time and well done.'),
    (3, 2, 4, 'Plumbing service was satisfactory.');