# HBnB - Holberton BnB

## About the project

HBnB (Holberton BnB) is a lodging rental application inspired by Airbnb. This project implements a layered architecture with a RESTful API that allows users to manage accounts, properties, amenities, and reviews. Developed as part of the Holberton School program, HBnB demonstrates the application of software design principles, object-oriented programming, and REST API development.

## Project Architecture

HBnB uses a layered architecture that clearly separates responsibilities, allowing for easier maintenance and increased scalability:

### 1. API Layer (Presentation)
- Implemented with Flask and Flask-RESTx for a robust RESTful API
- Structured endpoints for all main entities (users, places, amenities, reviews)
- Automatic documentation via Swagger UI to facilitate testing and integration
- Management of HTTP requests and appropriate formatting of JSON responses
- Input data validation before processing

### 2. Business Logic Layer (Services)
- Facade Pattern (HBnBFacade) that centralizes and orchestrates operations
- Encapsulation of business logic and validation rules
- Management of interactions between different entities
- Single interface for the API layer, reducing coupling

### 3. Model Layer (Domain)
- Definition of business entities with their attributes and behaviors
- Data validation at the model level to ensure integrity
- Relationships between different entities (owner-place, place-amenity, etc.)
- Inheritance from BaseModel for common functionalities (identifiers, timestamps)

### 4. Persistence Layer
- Repository Pattern to abstract storage and retrieval of data
- Repository interface defining standard operations (CRUD)
- InMemoryRepository implementation for in-memory storage
- Design allowing easy extension to other storage types

## Main Entities

### Users
- Complete user account management (creation, modification, consultation)
- Validation of personal information (email, first name, last name)
- Support for user roles (administrator vs. standard user)
- Constraints on fields (maximum length, email format)

### Places
- Management of properties available for rent
- Detailed information: title, description, price, geographic location
- Relationships with the owner (User)
- Associations with available amenities
- Collection of reviews left by users

### Amenities
- Characteristics or services available in a property
- Examples: WiFi, air conditioning, equipped kitchen, swimming pool, etc.
- Bidirectional association with places
- Validation of the name (required, maximum length)

### Reviews
- Evaluation system allowing users to rate their stay
- Rating on a scale of 1 to 5 stars
- Textual comments detailing the experience
- Relationships with the user who left the review and the place concerned
- Validation of content and rating

## API Features

### Complete RESTful API

Each resource has a complete set of CRUD endpoints:

#### User Management
- `POST /api/v1/users`: Creation of a new account
- `GET /api/v1/users`: Retrieval of the list of users
- `GET /api/v1/users/{id}`: Consultation of user details
- `PUT /api/v1/users/{id}`: Update of user information

#### Place Management
- `POST /api/v1/places`: Creation of a new place
- `GET /api/v1/places`: Retrieval of the list of places
- `GET /api/v1/places/{id}`: Consultation of place details
- `PUT /api/v1/places/{id}`: Update of place information

#### Amenity Management
- `POST /api/v1/amenities`: Creation of a new amenity
- `GET /api/v1/amenities`: Retrieval of the list of amenities
- `GET /api/v1/amenities/{id}`: Consultation of amenity details
- `PUT /api/v1/amenities/{id}`: Update of an amenity

#### Review System
- `POST /api/v1/reviews`: Submission of a new review
- `GET /api/v1/reviews`: Retrieval of the list of reviews
- `GET /api/v1/reviews/{id}`: Consultation of review details
- `PUT /api/v1/reviews/{id}`: Update of a review
- `DELETE /api/v1/reviews/{id}`: Deletion of a review
- `GET /api/v1/places/{id}/reviews`: Retrieval of reviews for a specific place

## Error Handling and Testing

### Robust Error Handling
- Complete validation of input data at each level (API, services, models)
- Appropriate HTTP status codes according to the type of error:
  - `400 Bad Request`: Invalid or missing data
  - `404 Not Found`: Non-existent resource
  - `500 Internal Server Error`: Unexpected errors
- Clear and informative error messages to facilitate debugging
- Exception logging with tracing for server-side analysis
- Handling of edge cases and unexpected values
- Consistent try/except structure in all endpoints

### Comprehensive Testing
- Unit tests for each model with pytest
- Test scenarios covering:
  - Validation of constraints (required fields, formats, limits)
  - Verification of relationships between entities
  - Tests of expected error cases
  - Correct behavior of specific methods
- Integration tests of API endpoints
- Verification of status codes and response formats
- End-to-end tests simulating user scenarios

The tests ensure that:
- Data validation works correctly
- Relationships between entities are maintained consistently
- APIs respond with appropriate HTTP codes
- Errors are captured and clearly communicated
- The system remains stable and predictable in all use cases

## Technologies Used

- **Backend**: Python 3.x
- **Web Framework**: Flask 2.x
- **REST API**: Flask-RESTx
- **API Documentation**: Swagger UI (integrated via Flask-RESTx)
- **Persistence**: InMemoryRepository (abstraction for future storage)
- **Testing**: unittest
- **Dependency Management**: pip, requirements.txt

## Installation and Startup

### Prerequisites
- Python 3.6 or higher
- pip (Python package manager)
- Virtual environment recommended (venv or virtualenv)

### Installation
```bash
# Clone the repository
git clone https://github.com/your-username/holbertonschool-hbnb.git
cd holbertonschool-hbnb/part2/hbnb

# Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Running the server
```bash
python run.py
```

The API will be accessible at: http://127.0.0.1:5000/  
Swagger UI documentation is available at: http://127.0.0.1:5000/

### Running tests
```bash
# Run all tests
pytest

# Run specific tests
pytest tests/models/test_user.py
```

## Project Structure

```
hbnb/
├── app/                      # Main application directory
│   ├── __init__.py           # Flask application initialization
│   ├── api/                  # API Layer
│   │   ├── __init__.py
│   │   ├── v1/               # API Version 1
│   │   │   ├── __init__.py
│   │   │   ├── amenities.py  # Endpoints for amenities
│   │   │   ├── places.py     # Endpoints for places
│   │   │   ├── reviews.py    # Endpoints for reviews
│   │   │   ├── users.py      # Endpoints for users
│   │   │   └── views/        # Additional views
│   ├── models/               # Model Layer (Domain)
│   │   ├── __init__.py
│   │   ├── amenity.py        # Amenity Model
│   │   ├── base_model.py     # Base class with common functionality
│   │   ├── place.py          # Place Model
│   │   ├── review.py         # Review Model
│   │   └── user.py           # User Model
│   ├── persistence/          # Persistence Layer
│   │   ├── __init__.py
│   │   └── repository.py     # Repository Pattern and implementation
│   └── services/             # Service Layer (Business Logic)
│       ├── __init__.py
│       └── facade.py         # Facade Pattern for orchestration
├── tests/                    # Unit and integration tests
│   └── models/
│       ├── __init__.py
│       ├── test_amenity.py
│       ├── test_place.py
│       ├── test_review.py
│       └── test_user.py
├── config.py                 # Application configuration
├── requirements.txt          # Project dependencies
└── run.py                    # Entry point for execution
```

## Project Strengths

### Architecture and Design
1. **Layered Architecture** - Clear separation of concerns facilitating maintenance
2. **Facade Pattern** - Unified interface simplifying access to complex functionality
3. **Repository Pattern** - Abstraction of persistence allowing storage changes
4. **SOLID Principles** - Application of object-oriented design principles
5. **Design Patterns** - Use of recognized patterns to solve common problems

### Quality and Robustness
1. **Multi-level Validation** - Data control at each processing stage
2. **Error Handling** - Complete and consistent handling of error cases
3. **Unit Testing** - Complete coverage of functionality and edge cases
4. **Documentation** - API documented via Swagger UI and commented code
5. **Extensibility** - Design allowing easy addition of new features

## Conclusion

The HBnB project demonstrates the application of advanced software design principles and layered architecture in the development of a complete RESTful API. The emphasis on separation of concerns, data validation, and error handling ensures a robust and maintainable application.

The integrated documentation via Swagger UI, comprehensive tests, and consistent application of design patterns make HBnB a practical example of modern and well-structured web application development.