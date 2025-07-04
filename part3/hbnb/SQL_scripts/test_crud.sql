-- HBnB CRUD Operations Test Script
-- Task 10: Testing database integrity and CRUD functionality

-- ==============================================
-- SECTION 1: READ OPERATIONS (SELECT TESTS)
-- ==============================================

-- Test 1: Verify admin user exists
SELECT '=== TEST 1: Admin User Verification ===' AS test_name;
SELECT * FROM users WHERE email = 'admin@hbnb.io';

-- Test 2: Verify initial amenities exist
SELECT '=== TEST 2: Initial Amenities Verification ===' AS test_name;
SELECT * FROM amenities ORDER BY name;

-- Test 3: Count initial data
SELECT '=== TEST 3: Data Count Verification ===' AS test_name;
SELECT 'Users' AS table_name, COUNT(*) AS count FROM users
UNION ALL
SELECT 'Amenities' AS table_name, COUNT(*) AS count FROM amenities;

-- ==============================================
-- SECTION 2: CREATE OPERATIONS (INSERT TESTS)
-- ==============================================

-- Test 4: Insert a regular user
SELECT '=== TEST 4: Create Regular User ===' AS test_name;
INSERT INTO users (
    id, first_name, last_name, email, password, is_admin, created_at, updated_at
) VALUES (
    'test-user-123e4567-e89b-12d3-a456-426614174000',
    'John',
    'Doe',
    'john.doe@example.com',
    'hashed_password_here',
    FALSE,
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- Verify user creation
SELECT * FROM users WHERE email = 'john.doe@example.com';

-- Test 5: Insert a place
SELECT '=== TEST 5: Create Place ===' AS test_name;
INSERT INTO places (
    id, title, description, price, latitude, longitude, owner_id, created_at, updated_at
) VALUES (
    'place-123e4567-e89b-12d3-a456-426614174000',
    'Beautiful Apartment',
    'A lovely apartment in the heart of the city',
    120.50,
    40.7128,
    -74.0060,
    'test-user-123e4567-e89b-12d3-a456-426614174000',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- Verify place creation
SELECT * FROM places WHERE title = 'Beautiful Apartment';

-- ==============================================
-- SECTION 3: UPDATE OPERATIONS (UPDATE TESTS)
-- ==============================================

-- Test 6: Update user information
SELECT '=== TEST 6: Update User Information ===' AS test_name;
UPDATE users 
SET first_name = 'Jane', last_name = 'Smith', updated_at = CURRENT_TIMESTAMP 
WHERE email = 'john.doe@example.com';

-- Verify update
SELECT * FROM users WHERE email = 'john.doe@example.com';

-- Test 7: Update place price
SELECT '=== TEST 7: Update Place Price ===' AS test_name;
UPDATE places 
SET price = 150.00, updated_at = CURRENT_TIMESTAMP 
WHERE title = 'Beautiful Apartment';

-- Verify update
SELECT title, price FROM places WHERE title = 'Beautiful Apartment';

-- ==============================================
-- SECTION 4: DELETE OPERATIONS (DELETE TESTS)
-- ==============================================

-- Test 8: Insert and delete a review
SELECT '=== TEST 8: Create and Delete Review ===' AS test_name;
INSERT INTO reviews (
    id, text, rating, user_id, place_id, created_at, updated_at
) VALUES (
    'review-123e4567-e89b-12d3-a456-426614174000',
    'Great place to stay!',
    5,
    'test-user-123e4567-e89b-12d3-a456-426614174000',
    'place-123e4567-e89b-12d3-a456-426614174000',
    CURRENT_TIMESTAMP,
    CURRENT_TIMESTAMP
);

-- Verify review creation
SELECT * FROM reviews;

-- Delete the review
DELETE FROM reviews WHERE id = 'review-123e4567-e89b-12d3-a456-426614174000';

-- Verify deletion
SELECT 'Reviews after deletion:' AS status, COUNT(*) AS count FROM reviews;
