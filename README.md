# HBnB Project – Technical Documentation

## 1. Introduction

This technical document presents the architecture of the **HBnB** project, a housing rental platform inspired by Airbnb.

It brings together all the UML diagrams created during the design phases:
- The **package diagram** (layered architecture),
- The **business class diagram** (Business Logic Layer),
- The **sequence diagrams** illustrating API call flows.

This document serves as a **technical reference** for the development phases, ensuring clarity, consistency, and maintainability of the system.

---

## 2. High-Level Architecture

### 2.1 Package Diagram

```mermaid

---
config:
  look: neo
  theme: neo-dark
  layout: dagre
title: High-Level Package Diagram
---
classDiagram
direction TB
    namespace PresentationLayer {
        class UserAPI {
            +register(userData)
            +login(credentials)
            +getProfile(userId)
            +updateProfile(userId, data)
        }
        class PlaceAPI {
            +create(placeData)
            +getById(id)
            +search(criteria)
            +update(id, data)
        }
        class ReviewAPI {
            +submitReview(reviewData)
            +getByPlaceId(placeId)
            +getByAuthorId(authorId)
        }
        class BookingService {
            +createBooking(bookingData)
            +confirmBooking(bookingId)
            +cancelBooking(bookingId)
        }
    }
    namespace BusinessLogicLayer {
        class HBnBFacade {
            +registerUser(data)
            +authenticateUser(credentials)
            +createPlace(placeData)
            +searchPlaces(criteria)
            +submitReview(reviewData)
            +createBooking(bookingData)
        }
        class User {
            -id: String
            -email: String
            -name: String
            -hashedPassword: String
            +validate()
            +isPasswordValid(password)
            +getPublicProfile()
        }
        class Place {
            -id: String
            -name: String
            -description: String
            -location: Location
            -ownerId: String
            -price: Number
            +validate()
            +isAvailable(dates)
            +calculateTotalPrice(checkIn, checkOut)
        }
        class Review {
            -id: String
            -placeId: String
            -authorId: String
            -rating: Number
            -comment: String
            -date: Date
            +validate()
        }
        class Amenity {
            -id: String
            -name: String
            -icon: String
            +validate()
        }
    }
    namespace PersistenceLayer {
        class UserRepository {
            +findByEmail(email)
            +findByName(name)
        }
        class PlaceRepository {
            +findByLocation(location, radius)
            +findByAmenities(amenityIds)
            +findByPriceRange(min, max)
        }
        class ReviewRepository {
            +findByPlaceId(placeId)
            +findByAuthorId(authorId)
            +getAverageRating(placeId)
        }
        class AmenityRepository {
            +findByCategory(category)
        }
    }
    UserAPI --> HBnBFacade : use
    PlaceAPI --> HBnBFacade : use
    ReviewAPI --> HBnBFacade : use
    BookingService --> HBnBFacade : use
    HBnBFacade --> User : delegate
    HBnBFacade --> Place : delegate
    HBnBFacade --> Review : delegate
    HBnBFacade --> Amenity : delegate
    User --> UserRepository : access data
    Place --> PlaceRepository : access data
    Review --> ReviewRepository : access data
    Amenity --> AmenityRepository : access data
```

### 2.2 Description of the Layered Architecture

The system is based on a layered architecture:

- **API Layer (Interface)**: handles REST requests, acts as a facade.
- **Business Logic Layer**: contains business rules (user creation, reviews, etc.)
- **Storage Layer**: interaction with files or database.

This separation allows for good **modularity**, **testability**, and **maintainability** of the code.

---

## 3. Business Logic Layer

### 3.1 Business Class Diagram

```mermaid

---
config:
  theme: neo-dark
  layout: elk
title: Business Logic Layer
---
classDiagram
direction TB
    class Base {
        +UUID id
        +created_at
        +updated_at
    }
    class UserModel {
        +str first_name
        +str last_name
        +str email
        -str password
        +bool is_admin
        +register()
        +update_profile()
        +delete()
    }
    class PlaceModel {
        +str title
        +str description
        +float price
        +float latitude
        +float longitude
        +create()
        +update()
        +delete()
    }
    class AmenityModel {
        +str name
        +str description
        +create()
        +update()
        +delete()
    }
    class ReviewModel {
        +int rating
        +str comment
        +submit()
        +edit()
        +delete()
    }
    class PlaceAmenity {
        +UUID id
        +UUID place_id
        +UUID amenity_id
    }

    <<abstract>> Base

    PlaceModel --|> Base
    AmenityModel --|> Base
    ReviewModel --|> Base
    UserModel --|> Base
    UserModel "1" *-- "*" PlaceModel : owns and controls
    PlaceModel "1" *-- "*" ReviewModel : has
    AmenityModel "1" o-- "*" PlaceAmenity : used by
    PlaceModel "1" *-- "*" PlaceAmenity : manages
```

### 3.2 Description of Entities and Relationships

#### 🔸 Base
Common abstract class, provides: `id`, `created_at`, `updated_at`.

#### 🔸 User
Represents a user:
- Attributes: `first_name`, `last_name`, `email`, `is_admin`, etc.
- Methods: `register()`, `delete()`, etc.
- Inherits from `Base`.
- **Composition** with `Place`: a `User` owns their `Place`.

#### 🔸 Place
Represents a published accommodation:
- Attributes: `title`, `price`, `latitude`, etc.
- Methods: `create()`, `update()`, etc.
- Composed in `User`, aggregates `Review`.

#### 🔸 Review
Represents a review:
- Attributes: `rating`, `comment`
- Methods: `submit()`, `edit()`
- Linked to `User` and `Place` via simple associations

#### 🔸 Amenity
Represents a facility (Wi-Fi, etc.)
- Associated via `PlaceAmenity`
- Exists independently of `Place`

#### 🔸 PlaceAmenity
Association table between `Place` and `Amenity`
- **Composed in `Place`**
- **Aggregated by `Amenity`**

---

## 4. API Interaction Flow

### 4.1 Sequence Diagrams

```mermaid
---
config:
  theme: redux-dark-color
  look: neo
title: User Registration
---
sequenceDiagram
    participant Client
    participant UserAPI
    participant HBnBFacade
    participant UserModel
    participant PasswordService
    participant EmailService
    participant UserRepository
    activate Client
    Client->>+UserAPI: Send registration data (POST /register)
    activate UserAPI
    UserAPI->>UserAPI: Verify request format
    Note over UserAPI: Checking mandatory fields
    UserAPI->>+HBnBFacade: Request user registration
    activate HBnBFacade
    HBnBFacade->>HBnBFacade: Verify business rules
    Note over HBnBFacade: System rules verification
    HBnBFacade->>UserRepository: Find user by email
    UserRepository-->>HBnBFacade: User (null if not exists)
    alt Email already used
        HBnBFacade-->>UserAPI: Error: email already registered
        UserAPI-->>Client: Error 409: Conflict (details)
    else Email available
        HBnBFacade->>+PasswordService: Secure the password
        PasswordService-->>-HBnBFacade: Hashed password
        HBnBFacade->>+UserModel: Create user with data
        UserModel->>+UserRepository: Save user
        UserRepository-->>-UserModel: Saved user with ID
        UserModel-->>-HBnBFacade: Created user
        HBnBFacade->>+EmailService: Send verification email
        EmailService-->>-HBnBFacade: Email sending status
        HBnBFacade-->>-UserAPI: Created user object
        UserAPI-->>-Client: Success 201: User created (details)
    end
    deactivate Client
```

```mermaid
---
config:
  theme: redux-dark-color
  look: neo
title : Place Creation
---
sequenceDiagram
    participant Client
    participant PlaceAPI
    participant HBnBFacade
    participant UserModel
    participant PlaceModel
    participant LocationService
    participant AmenityRepository
    participant PlaceRepository
    activate Client
    Client->>+PlaceAPI: Send place info (POST /places)
    activate PlaceAPI
    PlaceAPI->>PlaceAPI: Check if request has required info
    Note over PlaceAPI: Makes sure all needed fields are present
    PlaceAPI->>+HBnBFacade: Ask to create place with user ID
    activate HBnBFacade
    HBnBFacade->>+UserModel: Check if user exists
    UserModel-->>-HBnBFacade: Return user info or error
    alt User not allowed
        HBnBFacade-->>PlaceAPI: User can't do this
        PlaceAPI-->>Client: Error 403: Not allowed
    else User allowed
        HBnBFacade->>HBnBFacade: Check if place info is valid
        Note over HBnBFacade: Check price, description is good, etc.
        HBnBFacade->>+LocationService: Check if address is real
        LocationService-->>-HBnBFacade: Return verified location
        HBnBFacade->>+AmenityRepository: Get amenities by IDs
        AmenityRepository-->>-HBnBFacade: Return list of amenities
        alt Location or amenities not valid
            HBnBFacade-->>PlaceAPI: Something is wrong with the data
            PlaceAPI-->>Client: Error 400: Bad data (with details)
        else Everything is valid
            HBnBFacade->>+PlaceModel: Create new place with data
            PlaceModel->>+PlaceRepository: Save place to database
            PlaceRepository-->>-PlaceModel: Return saved place with ID
            PlaceModel-->>-HBnBFacade: Return the created place
            alt Place has amenities
                HBnBFacade->>PlaceRepository: Connect amenities to place
                PlaceRepository-->>HBnBFacade: Confirm connection
            end
            HBnBFacade-->>-PlaceAPI: Return created place
            PlaceAPI->>PlaceAPI: Format the response
            PlaceAPI-->>-Client: Success 201: Place created (with details)
        end
    end
    deactivate Client
```

Recommended examples:
- Creation of a `Place` by a user
- Writing a `Review`
- Deletion of a user account

### 4.2 Explanation of Scenarios

#### Example: Writing a review

1. The authenticated user submits a review via the API.
2. The API validates authentication and format.
3. The `Review` is created in the business layer.
4. The `Review` is linked to the user and accommodation.
5. The object is saved in the database.

---

## 5. Conclusion

This document constitutes the **technical reference base** for the HBnB project.  
It guides the implementation of the system while respecting business rules, interactions between layers, and design constraints.

---

## 📎 Appendices

- Links to sources (UML guides, style guides)
- Project references or tools used (Mermaid, PlantUML, etc.)