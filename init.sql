-- Drop existing tables if they exist (in reverse order due to foreign keys)
DROP TABLE IF EXISTS activity CASCADE;
DROP TABLE IF EXISTS tickets CASCADE;
DROP TABLE IF EXISTS events CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Drop existing types
DROP TYPE IF EXISTS ticket_status CASCADE;
DROP TYPE IF EXISTS ticket_type CASCADE;
DROP TYPE IF EXISTS event_status CASCADE;
DROP TYPE IF EXISTS event_category CASCADE;
DROP TYPE IF EXISTS user_role CASCADE;

-- Create ENUM types for PostgreSQL
CREATE TYPE user_role AS ENUM ('attendee', 'organizer');
CREATE TYPE event_category AS ENUM ('conference', 'music', 'networking', 'workshop', 'sports', 'exhibition', 'seminar', 'festival', 'other');
CREATE TYPE event_status AS ENUM ('active', 'completed', 'cancelled');
CREATE TYPE ticket_type AS ENUM ('general', 'vip', 'premium');
CREATE TYPE ticket_status AS ENUM ('pending', 'registered', 'rejected', 'refunded');

-- Create Users table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role user_role NOT NULL DEFAULT 'attendee',
    phone VARCHAR(20),
    organization VARCHAR(255), -- For organizers
    bio TEXT,
    ratings INTEGER[] DEFAULT '{}', -- For organizer ratings
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Events table with simpler structure for dashboard
CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    organizer_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category event_category NOT NULL DEFAULT 'other',
    datetime TIMESTAMP NOT NULL, -- Single date field for simplicity
    location VARCHAR(500) NOT NULL,
    venue_name VARCHAR(255),
    max_capacity INT NOT NULL DEFAULT 100,
    current_registrations INT DEFAULT 0,
    general_price DECIMAL(10, 2) DEFAULT 0.00,
    vip_price DECIMAL(10, 2) DEFAULT 0.00,
    premium_price DECIMAL(10, 2) DEFAULT 0.00,
    status event_status NOT NULL DEFAULT 'active',
    image_url VARCHAR(500),
    requirements TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraint
    CONSTRAINT fk_organizer 
        FOREIGN KEY (organizer_id) REFERENCES users(user_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    
    -- Check constraints
    CONSTRAINT chk_capacity 
        CHECK (max_capacity > 0 AND current_registrations >= 0 AND current_registrations <= max_capacity),
    CONSTRAINT chk_prices 
        CHECK (general_price >= 0 AND vip_price >= 0 AND premium_price >= 0)
);

-- Create Tickets table with simpler status management
CREATE TABLE tickets (
    ticket_id SERIAL PRIMARY KEY,
    event_id INT NOT NULL,
    user_id INT NOT NULL, -- The attendee
    ticket_type ticket_type NOT NULL DEFAULT 'general',
    status ticket_status NOT NULL DEFAULT 'pending',
    price_paid DECIMAL(10, 2) NOT NULL,
    booking_reference VARCHAR(50) UNIQUE NOT NULL,
    payment_id VARCHAR(255), -- External payment gateway reference
    special_requests TEXT,
    quantity INT DEFAULT 1, -- For bulk purchases
    customer_name VARCHAR(200), -- Store full name for easier queries
    customer_email VARCHAR(255), -- Store email for easier queries
    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    checked_in BOOLEAN DEFAULT FALSE,
    checked_in_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints
    CONSTRAINT fk_ticket_event 
        FOREIGN KEY (event_id) REFERENCES events(event_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,
    
    CONSTRAINT fk_ticket_user 
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE RESTRICT
        ON UPDATE CASCADE
);

-- Create Activity table for logging all system activities
CREATE TABLE activity (
    activity_id SERIAL PRIMARY KEY,
    user_id INT,
    event_id INT,
    ticket_id INT,
    activity_type VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Foreign key constraints (nullable to allow system-wide activities)
    CONSTRAINT fk_activity_user 
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    
    CONSTRAINT fk_activity_event 
        FOREIGN KEY (event_id) REFERENCES events(event_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE,
    
    CONSTRAINT fk_activity_ticket 
        FOREIGN KEY (ticket_id) REFERENCES tickets(ticket_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- Sample data insertion

-- Insert 10 organizers
INSERT INTO users (first_name, last_name, email, password, role, phone, organization, bio) VALUES
('Sarah', 'Johnson', 'sarah.johnson@events.com', 'password123', 'organizer', '+61412345001', 'TechConf Organizers', 'Specialized in technology conferences and workshops'),
('Michael', 'Chen', 'michael.chen@musicevents.com', 'password123', 'organizer', '+61412345002', 'Harmony Music Events', 'Professional music event coordinator with 10+ years experience'),
('Emily', 'Rodriguez', 'emily.rodriguez@networking.com', 'password123', 'organizer', '+61412345003', 'Connect Pro', 'Business networking and professional development events'),
('David', 'Thompson', 'david.thompson@sportevents.com', 'password123', 'organizer', '+61412345004', 'Active Sports Management', 'Sports events and fitness workshops organizer'),
('Lisa', 'Anderson', 'lisa.anderson@artshows.com', 'password123', 'organizer', '+61412345005', 'Creative Arts Sydney', 'Art exhibitions and cultural events specialist'),
('James', 'Williams', 'james.williams@seminarco.com', 'password123', 'organizer', '+61412345006', 'Professional Seminars Ltd', 'Educational seminars and training sessions'),
('Maria', 'Garcia', 'maria.garcia@festivalorg.com', 'password123', 'organizer', '+61412345007', 'Festival Productions', 'Large-scale festival and outdoor event management'),
('Robert', 'Taylor', 'robert.taylor@bizexpo.com', 'password123', 'organizer', '+61412345008', 'Business Expo Group', 'Trade shows and business exhibitions'),
('Jennifer', 'Lee', 'jennifer.lee@wellnessevents.com', 'password123', 'organizer', '+61412345009', 'Wellness Sydney', 'Health and wellness workshops and retreats'),
('Christopher', 'Martin', 'chris.martin@techworkshops.com', 'password123', 'organizer', '+61412345010', 'Innovation Labs', 'Technology workshops and hackathons');

-- Insert 50 attendees
INSERT INTO users (first_name, last_name, email, password, role, phone) VALUES
('John', 'Smith', 'john.smith@email.com', 'password123', 'attendee', '+61423456001'),
('Jane', 'Doe', 'jane.doe@email.com', 'password123', 'attendee', '+61423456002'),
('Alex', 'Brown', 'alex.brown@email.com', 'password123', 'attendee', '+61423456003'),
('Emma', 'Jones', 'emma.jones@email.com', 'password123', 'attendee', '+61423456004'),
('William', 'Miller', 'william.miller@email.com', 'password123', 'attendee', '+61423456005'),
('Olivia', 'Davis', 'olivia.davis@email.com', 'password123', 'attendee', '+61423456006'),
('Noah', 'Wilson', 'noah.wilson@email.com', 'password123', 'attendee', '+61423456007'),
('Sophia', 'Moore', 'sophia.moore@email.com', 'password123', 'attendee', '+61423456008'),
('Liam', 'Taylor', 'liam.taylor@email.com', 'password123', 'attendee', '+61423456009'),
('Isabella', 'Anderson', 'isabella.anderson@email.com', 'password123', 'attendee', '+61423456010'),
('Mason', 'Thomas', 'mason.thomas@email.com', 'password123', 'attendee', '+61423456011'),
('Ava', 'Jackson', 'ava.jackson@email.com', 'password123', 'attendee', '+61423456012'),
('Ethan', 'White', 'ethan.white@email.com', 'password123', 'attendee', '+61423456013'),
('Charlotte', 'Harris', 'charlotte.harris@email.com', 'password123', 'attendee', '+61423456014'),
('Lucas', 'Martin', 'lucas.martin@email.com', 'password123', 'attendee', '+61423456015'),
('Amelia', 'Thompson', 'amelia.thompson@email.com', 'password123', 'attendee', '+61423456016'),
('Oliver', 'Garcia', 'oliver.garcia@email.com', 'password123', 'attendee', '+61423456017'),
('Mia', 'Martinez', 'mia.martinez@email.com', 'password123', 'attendee', '+61423456018'),
('Elijah', 'Robinson', 'elijah.robinson@email.com', 'password123', 'attendee', '+61423456019'),
('Harper', 'Clark', 'harper.clark@email.com', 'password123', 'attendee', '+61423456020'),
('Benjamin', 'Rodriguez', 'benjamin.rodriguez@email.com', 'password123', 'attendee', '+61423456021'),
('Evelyn', 'Lewis', 'evelyn.lewis@email.com', 'password123', 'attendee', '+61423456022'),
('James', 'Lee', 'james.lee@email.com', 'password123', 'attendee', '+61423456023'),
('Abigail', 'Walker', 'abigail.walker@email.com', 'password123', 'attendee', '+61423456024'),
('Michael', 'Hall', 'michael.hall@email.com', 'password123', 'attendee', '+61423456025'),
('Emily', 'Allen', 'emily.allen@email.com', 'password123', 'attendee', '+61423456026'),
('Daniel', 'Young', 'daniel.young@email.com', 'password123', 'attendee', '+61423456027'),
('Elizabeth', 'Hernandez', 'elizabeth.hernandez@email.com', 'password123', 'attendee', '+61423456028'),
('Matthew', 'King', 'matthew.king@email.com', 'password123', 'attendee', '+61423456029'),
('Sofia', 'Wright', 'sofia.wright@email.com', 'password123', 'attendee', '+61423456030'),
('Joseph', 'Lopez', 'joseph.lopez@email.com', 'password123', 'attendee', '+61423456031'),
('Avery', 'Hill', 'avery.hill@email.com', 'password123', 'attendee', '+61423456032'),
('David', 'Scott', 'david.scott@email.com', 'password123', 'attendee', '+61423456033'),
('Luna', 'Green', 'luna.green@email.com', 'password123', 'attendee', '+61423456034'),
('Jackson', 'Adams', 'jackson.adams@email.com', 'password123', 'attendee', '+61423456035'),
('Scarlett', 'Baker', 'scarlett.baker@email.com', 'password123', 'attendee', '+61423456036'),
('Owen', 'Gonzalez', 'owen.gonzalez@email.com', 'password123', 'attendee', '+61423456037'),
('Victoria', 'Nelson', 'victoria.nelson@email.com', 'password123', 'attendee', '+61423456038'),
('Ryan', 'Carter', 'ryan.carter@email.com', 'password123', 'attendee', '+61423456039'),
('Grace', 'Mitchell', 'grace.mitchell@email.com', 'password123', 'attendee', '+61423456040'),
('Nathan', 'Perez', 'nathan.perez@email.com', 'password123', 'attendee', '+61423456041'),
('Chloe', 'Roberts', 'chloe.roberts@email.com', 'password123', 'attendee', '+61423456042'),
('Samuel', 'Turner', 'samuel.turner@email.com', 'password123', 'attendee', '+61423456043'),
('Zoey', 'Phillips', 'zoey.phillips@email.com', 'password123', 'attendee', '+61423456044'),
('Henry', 'Campbell', 'henry.campbell@email.com', 'password123', 'attendee', '+61423456045'),
('Lily', 'Parker', 'lily.parker@email.com', 'password123', 'attendee', '+61423456046'),
('Alexander', 'Evans', 'alexander.evans@email.com', 'password123', 'attendee', '+61423456047'),
('Madison', 'Edwards', 'madison.edwards@email.com', 'password123', 'attendee', '+61423456048'),
('Sebastian', 'Collins', 'sebastian.collins@email.com', 'password123', 'attendee', '+61423456049'),
('Aria', 'Stewart', 'aria.stewart@email.com', 'password123', 'attendee', '+61423456050');

-- Insert sample events (user_id 1-10 are organizers)
INSERT INTO events (organizer_id, title, description, category, datetime, location, venue_name, max_capacity, general_price, vip_price, premium_price, status, image_url, requirements) VALUES
-- Sarah Johnson's events (organizer_id = 1)
(1, 'Tech Conference 2025', 'Annual technology conference featuring industry leaders', 'conference', '2025-07-15 09:00:00', 'Sydney Convention Centre, Darling Harbour, Sydney NSW', 'Sydney Convention Centre', 500, 89.00, 199.00, 299.00, 'active', NULL, NULL),
(1, 'AI Workshop', 'Hands-on AI and machine learning workshop', 'workshop', '2025-06-20 10:00:00', 'Sydney Tech Hub, 123 Tech Street, Sydney NSW', 'Tech Hub', 100, 149.00, 249.00, 349.00, 'active', NULL, NULL),

-- Michael Chen's events (organizer_id = 2)
(2, 'Summer Music Festival', 'Three-day outdoor music festival', 'music', '2025-08-20 18:00:00', 'Royal Botanic Gardens, Mrs Macquaries Rd, Sydney NSW', 'Royal Botanic Gardens', 2000, 120.00, 280.00, 450.00, 'active', NULL, NULL),
(2, 'Jazz Night', 'Evening of smooth jazz performances', 'music', '2025-06-28 19:00:00', 'Sydney Opera House, Bennelong Point, Sydney NSW', 'Sydney Opera House', 300, 75.00, 150.00, 250.00, 'active', NULL, NULL),

-- Emily Rodriguez's events (organizer_id = 3)
(3, 'Business Networking Night', 'Monthly networking event for professionals', 'networking', '2025-06-10 18:00:00', 'Harbour View Hotel, 100 Harbour View Rd, Sydney NSW', 'Harbour View Hotel', 200, 0.00, 75.00, 125.00, 'active', NULL, NULL),
(3, 'Startup Pitch Night', 'Entrepreneurs pitch to investors', 'networking', '2025-07-05 18:30:00', 'Innovation Hub, 456 Business St, Sydney NSW', 'Innovation Hub', 150, 25.00, 100.00, 200.00, 'active', NULL, NULL),

-- David Thompson's events (organizer_id = 4)
(4, 'Sydney Marathon', 'Annual city marathon event', 'sports', '2025-09-15 06:00:00', 'Sydney Harbour Bridge, Sydney NSW', 'Sydney CBD', 5000, 95.00, 150.00, 200.00, 'active', NULL, 'Must be 18+ to participate'),
(4, 'Beach Volleyball Tournament', 'Professional beach volleyball competition', 'sports', '2025-07-25 08:00:00', 'Bondi Beach, Sydney NSW', 'Bondi Beach', 500, 45.00, 85.00, 150.00, 'active', NULL, NULL),

-- Lisa Anderson's events (organizer_id = 5)
(5, 'Contemporary Art Exhibition', 'Modern art showcase featuring local artists', 'exhibition', '2025-06-15 10:00:00', 'Art Gallery of NSW, Art Gallery Rd, Sydney NSW', 'Art Gallery of NSW', 400, 30.00, 60.00, 100.00, 'active', NULL, NULL),
(5, 'Photography Workshop', 'Learn portrait photography techniques', 'workshop', '2025-06-22 09:00:00', 'Creative Arts Centre, 789 Art Lane, Sydney NSW', 'Creative Arts Centre', 50, 120.00, 180.00, 250.00, 'active', NULL, 'Bring your own camera'),

-- James Williams' events (organizer_id = 6)
(6, 'Leadership Seminar', 'Executive leadership development program', 'seminar', '2025-07-10 09:00:00', 'Sydney Business School, 321 Education Blvd, Sydney NSW', 'Business School', 200, 199.00, 299.00, 399.00, 'active', NULL, NULL),
(6, 'Digital Marketing Masterclass', 'Advanced digital marketing strategies', 'seminar', '2025-06-25 10:00:00', 'Marketing Hub, 654 Digital Ave, Sydney NSW', 'Marketing Hub', 100, 149.00, 249.00, 349.00, 'active', NULL, NULL),

-- Maria Garcia's events (organizer_id = 7)
(7, 'Winter Food Festival', 'Culinary celebration with local food vendors', 'festival', '2025-07-01 11:00:00', 'Hyde Park, Sydney NSW', 'Hyde Park', 3000, 25.00, 65.00, 120.00, 'active', NULL, NULL),
(7, 'Cultural Heritage Festival', 'Celebrating multicultural Sydney', 'festival', '2025-08-10 10:00:00', 'Darling Harbour, Sydney NSW', 'Darling Harbour', 5000, 0.00, 50.00, 100.00, 'active', NULL, NULL),

-- Robert Taylor's events (organizer_id = 8)
(8, 'Business Expo 2025', 'B2B trade show and exhibition', 'exhibition', '2025-09-05 09:00:00', 'Sydney Exhibition Centre, Olympic Park, Sydney NSW', 'Exhibition Centre', 1000, 45.00, 120.00, 250.00, 'active', NULL, 'Business registration required'),
(8, 'Tech Startup Showcase', 'Innovative startups display their products', 'exhibition', '2025-07-18 10:00:00', 'Tech Park, 111 Innovation Dr, Sydney NSW', 'Tech Park', 400, 35.00, 85.00, 150.00, 'active', NULL, NULL),

-- Jennifer Lee's events (organizer_id = 9)
(9, 'Wellness Retreat Weekend', 'Two-day wellness and meditation retreat', 'other', '2025-08-02 08:00:00', 'Blue Mountains Retreat Centre, Katoomba NSW', 'Mountain Retreat', 80, 299.00, 499.00, 699.00, 'active', NULL, 'Accommodation included'),
(9, 'Yoga & Mindfulness Workshop', 'Introduction to yoga and meditation', 'workshop', '2025-06-18 06:30:00', 'Bondi Pavilion, Bondi Beach, Sydney NSW', 'Bondi Pavilion', 60, 65.00, 95.00, 135.00, 'active', NULL, 'Bring yoga mat'),

-- Christopher Martin's events (organizer_id = 10)
(10, 'Hackathon Sydney 2025', '48-hour coding competition', 'other', '2025-07-12 18:00:00', 'UTS Campus, 15 Broadway, Ultimo NSW', 'UTS Great Hall', 300, 0.00, 50.00, 100.00, 'active', NULL, 'Teams of 2-4 people'),
(10, 'Cybersecurity Conference', 'Latest in cybersecurity trends and threats', 'conference', '2025-08-15 09:00:00', 'ICC Sydney, 14 Darling Dr, Sydney NSW', 'ICC Sydney', 600, 125.00, 225.00, 375.00, 'active', NULL, NULL);

-- Insert sample tickets (user_id 11-60 are attendees)
INSERT INTO tickets (event_id, user_id, ticket_type, status, price_paid, booking_reference, payment_id, customer_name, customer_email, purchase_date) VALUES
-- Tech Conference registrations
(1, 11, 'general', 'registered', 89.00, 'EVT-TC2025-001', 'pay_001', 'John Smith', 'john.smith@email.com', CURRENT_TIMESTAMP - INTERVAL '5 days'),
(1, 12, 'vip', 'registered', 199.00, 'EVT-TC2025-002', 'pay_002', 'Jane Doe', 'jane.doe@email.com', CURRENT_TIMESTAMP - INTERVAL '4 days'),
(1, 13, 'general', 'pending', 89.00, 'EVT-TC2025-003', NULL, 'Alex Brown', 'alex.brown@email.com', CURRENT_TIMESTAMP - INTERVAL '2 hours'),
(1, 14, 'premium', 'registered', 299.00, 'EVT-TC2025-004', 'pay_004', 'Emma Jones', 'emma.jones@email.com', CURRENT_TIMESTAMP - INTERVAL '3 days'),
(1, 15, 'vip', 'registered', 199.00, 'EVT-TC2025-005', 'pay_005', 'William Miller', 'william.miller@email.com', CURRENT_TIMESTAMP - INTERVAL '6 days'),

-- Summer Music Festival registrations
(3, 16, 'general', 'registered', 120.00, 'EVT-SMF2025-001', 'pay_006', 'Olivia Davis', 'olivia.davis@email.com', CURRENT_TIMESTAMP - INTERVAL '7 days'),
(3, 17, 'vip', 'registered', 280.00, 'EVT-SMF2025-002', 'pay_007', 'Noah Wilson', 'noah.wilson@email.com', CURRENT_TIMESTAMP - INTERVAL '5 days'),
(3, 18, 'premium', 'pending', 450.00, 'EVT-SMF2025-003', NULL, 'Sophia Moore', 'sophia.moore@email.com', CURRENT_TIMESTAMP - INTERVAL '1 hour'),
(3, 19, 'general', 'registered', 120.00, 'EVT-SMF2025-004', 'pay_009', 'Liam Taylor', 'liam.taylor@email.com', CURRENT_TIMESTAMP - INTERVAL '4 days'),
(3, 20, 'vip', 'registered', 280.00, 'EVT-SMF2025-005', 'pay_010', 'Isabella Anderson', 'isabella.anderson@email.com', CURRENT_TIMESTAMP - INTERVAL '3 days'),

-- Business Networking Night registrations
(5, 21, 'vip', 'registered', 75.00, 'EVT-BNN2025-001', 'pay_011', 'Mason Thomas', 'mason.thomas@email.com', CURRENT_TIMESTAMP - INTERVAL '2 days'),
(5, 22, 'premium', 'registered', 125.00, 'EVT-BNN2025-002', 'pay_012', 'Ava Jackson', 'ava.jackson@email.com', CURRENT_TIMESTAMP - INTERVAL '1 day'),
(5, 23, 'vip', 'pending', 75.00, 'EVT-BNN2025-003', NULL, 'Ethan White', 'ethan.white@email.com', CURRENT_TIMESTAMP - INTERVAL '30 minutes'),

-- AI Workshop registrations
(2, 24, 'general', 'registered', 149.00, 'EVT-AIW2025-001', 'pay_014', 'Charlotte Harris', 'charlotte.harris@email.com', CURRENT_TIMESTAMP - INTERVAL '3 days'),
(2, 25, 'vip', 'registered', 249.00, 'EVT-AIW2025-002', 'pay_015', 'Lucas Martin', 'lucas.martin@email.com', CURRENT_TIMESTAMP - INTERVAL '2 days'),
(2, 26, 'premium', 'pending', 349.00, 'EVT-AIW2025-003', NULL, 'Amelia Thompson', 'amelia.thompson@email.com', CURRENT_TIMESTAMP - INTERVAL '4 hours'),

-- Sydney Marathon registrations
(7, 27, 'general', 'registered', 95.00, 'EVT-SM2025-001', 'pay_017', 'Oliver Garcia', 'oliver.garcia@email.com', CURRENT_TIMESTAMP - INTERVAL '10 days'),
(7, 28, 'vip', 'registered', 150.00, 'EVT-SM2025-002', 'pay_018', 'Mia Martinez', 'mia.martinez@email.com', CURRENT_TIMESTAMP - INTERVAL '8 days'),
(7, 29, 'general', 'registered', 95.00, 'EVT-SM2025-003', 'pay_019', 'Elijah Robinson', 'elijah.robinson@email.com', CURRENT_TIMESTAMP - INTERVAL '7 days'),
(7, 30, 'premium', 'registered', 200.00, 'EVT-SM2025-004', 'pay_020', 'Harper Clark', 'harper.clark@email.com', CURRENT_TIMESTAMP - INTERVAL '6 days'),

-- Contemporary Art Exhibition registrations
(9, 31, 'general', 'registered', 30.00, 'EVT-CAE2025-001', 'pay_021', 'Benjamin Rodriguez', 'benjamin.rodriguez@email.com', CURRENT_TIMESTAMP - INTERVAL '2 days'),
(9, 32, 'vip', 'registered', 60.00, 'EVT-CAE2025-002', 'pay_022', 'Evelyn Lewis', 'evelyn.lewis@email.com', CURRENT_TIMESTAMP - INTERVAL '1 day'),
(9, 33, 'premium', 'pending', 100.00, 'EVT-CAE2025-003', NULL, 'James Lee', 'james.lee@email.com', CURRENT_TIMESTAMP - INTERVAL '3 hours'),

-- Leadership Seminar registrations
(11, 34, 'general', 'registered', 199.00, 'EVT-LS2025-001', 'pay_024', 'Abigail Walker', 'abigail.walker@email.com', CURRENT_TIMESTAMP - INTERVAL '5 days'),
(11, 35, 'vip', 'registered', 299.00, 'EVT-LS2025-002', 'pay_025', 'Michael Hall', 'michael.hall@email.com', CURRENT_TIMESTAMP - INTERVAL '4 days'),
(11, 36, 'premium', 'registered', 399.00, 'EVT-LS2025-003', 'pay_026', 'Emily Allen', 'emily.allen@email.com', CURRENT_TIMESTAMP - INTERVAL '3 days'),

-- Winter Food Festival registrations
(13, 37, 'general', 'registered', 25.00, 'EVT-WFF2025-001', 'pay_027', 'Daniel Young', 'daniel.young@email.com', CURRENT_TIMESTAMP - INTERVAL '1 day'),
(13, 38, 'vip', 'registered', 65.00, 'EVT-WFF2025-002', 'pay_028', 'Elizabeth Hernandez', 'elizabeth.hernandez@email.com', CURRENT_TIMESTAMP - INTERVAL '2 days'),
(13, 39, 'premium', 'registered', 120.00, 'EVT-WFF2025-003', 'pay_029', 'Matthew King', 'matthew.king@email.com', CURRENT_TIMESTAMP - INTERVAL '3 days'),
(13, 40, 'general', 'pending', 25.00, 'EVT-WFF2025-004', NULL, 'Sofia Wright', 'sofia.wright@email.com', CURRENT_TIMESTAMP - INTERVAL '1 hour'),

-- Hackathon Sydney 2025 registrations
(19, 41, 'vip', 'registered', 50.00, 'EVT-HS2025-001', 'pay_031', 'Joseph Lopez', 'joseph.lopez@email.com', CURRENT_TIMESTAMP - INTERVAL '4 days'),
(19, 42, 'premium', 'registered', 100.00, 'EVT-HS2025-002', 'pay_032', 'Avery Hill', 'avery.hill@email.com', CURRENT_TIMESTAMP - INTERVAL '3 days'),
(19, 43, 'vip', 'registered', 50.00, 'EVT-HS2025-003', 'pay_033', 'David Scott', 'david.scott@email.com', CURRENT_TIMESTAMP - INTERVAL '2 days'),
(19, 44, 'general', 'registered', 0.00, 'EVT-HS2025-004', 'pay_034', 'Luna Green', 'luna.green@email.com', CURRENT_TIMESTAMP - INTERVAL '5 days'),

-- More diverse registrations
(4, 45, 'general', 'registered', 75.00, 'EVT-JN2025-001', 'pay_035', 'Jackson Adams', 'jackson.adams@email.com', CURRENT_TIMESTAMP - INTERVAL '1 day'),
(6, 46, 'vip', 'registered', 100.00, 'EVT-SPN2025-001', 'pay_036', 'Scarlett Baker', 'scarlett.baker@email.com', CURRENT_TIMESTAMP - INTERVAL '2 days'),
(8, 47, 'general', 'registered', 45.00, 'EVT-BVT2025-001', 'pay_037', 'Owen Gonzalez', 'owen.gonzalez@email.com', CURRENT_TIMESTAMP - INTERVAL '3 days'),
(10, 48, 'premium', 'registered', 250.00, 'EVT-PW2025-001', 'pay_038', 'Victoria Nelson', 'victoria.nelson@email.com', CURRENT_TIMESTAMP - INTERVAL '1 day'),
(12, 49, 'vip', 'registered', 249.00, 'EVT-DMM2025-001', 'pay_039', 'Ryan Carter', 'ryan.carter@email.com', CURRENT_TIMESTAMP - INTERVAL '2 days'),
(14, 50, 'general', 'registered', 0.00, 'EVT-CHF2025-001', 'pay_040', 'Grace Mitchell', 'grace.mitchell@email.com', CURRENT_TIMESTAMP - INTERVAL '4 days'),
(15, 51, 'vip', 'registered', 120.00, 'EVT-BE2025-001', 'pay_041', 'Nathan Perez', 'nathan.perez@email.com', CURRENT_TIMESTAMP - INTERVAL '5 days'),
(16, 52, 'general', 'registered', 35.00, 'EVT-TSS2025-001', 'pay_042', 'Chloe Roberts', 'chloe.roberts@email.com', CURRENT_TIMESTAMP - INTERVAL '3 days'),
(17, 53, 'premium', 'registered', 699.00, 'EVT-WRW2025-001', 'pay_043', 'Samuel Turner', 'samuel.turner@email.com', CURRENT_TIMESTAMP - INTERVAL '7 days'),
(18, 54, 'general', 'registered', 65.00, 'EVT-YMW2025-001', 'pay_044', 'Zoey Phillips', 'zoey.phillips@email.com', CURRENT_TIMESTAMP - INTERVAL '1 day'),
(20, 55, 'vip', 'registered', 225.00, 'EVT-CSC2025-001', 'pay_045', 'Henry Campbell', 'henry.campbell@email.com', CURRENT_TIMESTAMP - INTERVAL '2 days'),
(1, 56, 'general', 'rejected', 89.00, 'EVT-TC2025-006', NULL, 'Lily Parker', 'lily.parker@email.com', CURRENT_TIMESTAMP - INTERVAL '1 day'),
(3, 57, 'general', 'refunded', 120.00, 'EVT-SMF2025-006', 'pay_047', 'Alexander Evans', 'alexander.evans@email.com', CURRENT_TIMESTAMP - INTERVAL '8 days'),
(5, 58, 'premium', 'registered', 125.00, 'EVT-BNN2025-004', 'pay_048', 'Madison Edwards', 'madison.edwards@email.com', CURRENT_TIMESTAMP - INTERVAL '1 day'),
(7, 59, 'general', 'pending', 95.00, 'EVT-SM2025-005', NULL, 'Sebastian Collins', 'sebastian.collins@email.com', CURRENT_TIMESTAMP - INTERVAL '45 minutes'),
(9, 60, 'vip', 'registered', 60.00, 'EVT-CAE2025-004', 'pay_050', 'Aria Stewart', 'aria.stewart@email.com', CURRENT_TIMESTAMP - INTERVAL '2 days');

-- Update current_registrations for events based on registered tickets
UPDATE events SET current_registrations = (
    SELECT COUNT(*) FROM tickets 
    WHERE tickets.event_id = events.event_id 
    AND tickets.status = 'registered'
);

-- Insert sample activity data
INSERT INTO activity (user_id, event_id, ticket_id, activity_type, description) VALUES
(1, 1, NULL, 'event_created', 'Created new event: Tech Conference 2025'),
(1, 2, NULL, 'event_created', 'Created new event: AI Workshop'),
(2, 3, NULL, 'event_created', 'Created new event: Summer Music Festival'),
(2, 4, NULL, 'event_created', 'Created new event: Jazz Night'),
(3, 5, NULL, 'event_created', 'Created new event: Business Networking Night'),
(11, 1, 1, 'ticket_booked', 'New registration for Tech Conference 2025'),
(12, 1, 2, 'ticket_booked', 'VIP registration for Tech Conference 2025'),
(1, 1, NULL, 'reminder_sent', 'Sent reminder to 4 attendees for Tech Conference 2025'),
(NULL, 1, 1, 'registration_pending', 'Tech Conference 2025 has 1 new pending registration'),
(NULL, 3, 8, 'registration_pending', 'Summer Music Festival has new premium registration pending'),
(16, 3, 6, 'ticket_booked', 'New registration for Summer Music Festival'),
(2, 3, NULL, 'event_update', 'Updated venue details for Summer Music Festival'),
(37, 13, 37, 'ticket_booked', 'New registration for Winter Food Festival'),
(7, 13, NULL, 'capacity_alert', 'Winter Food Festival reached 75% capacity'),
(NULL, 1, 56, 'registration_rejected', 'Registration rejected for Tech Conference 2025'),
(NULL, 3, 57, 'ticket_refunded', 'Ticket refunded for Summer Music Festival');