-- Insert Administrator User
INSERT INTO users (
    id,
    first_name,
    last_name,
    email,
    password,
    is_admin,
    created_at,
    updated_at
) VALUES (
    '36c9050e-ddd3-4c3b-9731-9f487208bbc1',
    'Admin',
    'HBnB',
    'admin@hbnb.io',
    '$2b$12$9vGWMiEr9vRui1JALEimwuNKteHN/rpz3U3STPUlH.kfVnMyp08/.',
    TRUE,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- Insert Initial Amenities
INSERT INTO amenities (id, name, created_at, updated_at) VALUES 
    ('d45f6863-7ab0-44d7-adcd-e05d9518c14b', 'WiFi', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('32d49bab-723d-4ecd-899c-8b089a62fb74', 'Swimming Pool', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
    ('b765fbf4-3450-485b-ba84-2682c0d23258', 'Air Conditioning', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP);
