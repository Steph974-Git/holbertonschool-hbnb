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
    Client->>+UserAPI: Send sign-up information
    activate UserAPI
    UserAPI->>UserAPI: Check if form is complete
    Note over UserAPI: Make sure all required fields are filled
    UserAPI->>+HBnBFacade: Process this registration
    activate HBnBFacade
    HBnBFacade->>HBnBFacade: Check if information is valid
    Note over HBnBFacade: Verify age, password strength, etc.
    HBnBFacade->>UserRepository: Is this email already used?
    UserRepository-->>HBnBFacade: Email status (used or available)
    alt Email already used
        HBnBFacade-->>UserAPI: Someone already has this email
        UserAPI-->>Client: Error: Please use a different email
    else Email available
        HBnBFacade->>+PasswordService: Make password secure
        PasswordService-->>-HBnBFacade: Protected password
        HBnBFacade->>+UserModel: Create new account
        UserModel->>+UserRepository: Save this account
        UserRepository-->>-UserModel: Account saved successfully
        UserModel-->>-HBnBFacade: Account is now created
        HBnBFacade->>+EmailService: Send welcome email
        EmailService-->>-HBnBFacade: Email sent
        HBnBFacade-->>-UserAPI: Account is ready
        UserAPI-->>-Client: Success: Your account is created!
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
    Client->>+PlaceAPI: Submit new property listing
    activate PlaceAPI
    PlaceAPI->>PlaceAPI: Check if listing is complete
    Note over PlaceAPI: Make sure all required fields are filled
    PlaceAPI->>+HBnBFacade: Create this property listing
    activate HBnBFacade
    HBnBFacade->>+UserModel: Can this user add listings?
    UserModel-->>-HBnBFacade: User status and permissions
    alt User not permitted
        HBnBFacade-->>PlaceAPI: User can't add listings
        PlaceAPI-->>Client: Error: You can't create listings
    else User permitted
        HBnBFacade->>HBnBFacade: Check property details
        Note over HBnBFacade: Verify price, description, photos, etc.
        HBnBFacade->>+LocationService: Is this address real?
        LocationService-->>-HBnBFacade: Confirmed address details
        HBnBFacade->>+AmenityRepository: Get selected amenities
        AmenityRepository-->>-HBnBFacade: Available amenities
        alt Address or amenities invalid
            HBnBFacade-->>PlaceAPI: Property details have problems
            PlaceAPI-->>Client: Error: Please fix property details
        else All details valid
            HBnBFacade->>+PlaceModel: Create new property
            PlaceModel->>+PlaceRepository: Save this property
            PlaceRepository-->>-PlaceModel: Property saved with new ID
            PlaceModel-->>-HBnBFacade: Property successfully created
            alt Property has amenities
                HBnBFacade->>PlaceRepository: Add amenities to property
                PlaceRepository-->>HBnBFacade: Amenities connected
            end
            HBnBFacade-->>-PlaceAPI: Property listing complete
            PlaceAPI->>PlaceAPI: Prepare success message
            PlaceAPI-->>-Client: Success: Your property is now listed!
        end
    end
    deactivate Client
```
```mermaid
---
config:
  theme: redux-dark-color
title : Review Submission
---
sequenceDiagram
    participant Client
    participant ReviewAPI
    participant HBnBFacade
    participant UserModel
    participant PlaceModel
    participant ReviewModel
    participant ReviewRepository
    Client->>+ReviewAPI: Send review for a place
    activate ReviewAPI
    ReviewAPI->>ReviewAPI: Check if form is complete
    Note over ReviewAPI: Make sure rating and comment are provided
    ReviewAPI->>+HBnBFacade: Process this review
    activate HBnBFacade
    HBnBFacade->>+UserModel: Is this a valid user?
    UserModel-->>-HBnBFacade: User info or not found
    alt User not valid
        HBnBFacade-->>ReviewAPI: User can't post reviews
        ReviewAPI-->>Client: Error: Not allowed to post reviews
    else User valid
        HBnBFacade->>+PlaceModel: Does this place exist?
        PlaceModel-->>-HBnBFacade: Place info or not found
        alt Place doesn't exist
            HBnBFacade-->>ReviewAPI: Can't find this place
            ReviewAPI-->>Client: Error: Place not found
        else Place exists
            HBnBFacade->>HBnBFacade: Check review quality
            Note over HBnBFacade: Is rating 1-5? Is comment long enough?
            alt Review not good enough
                HBnBFacade-->>ReviewAPI: Review doesn't meet standards
                ReviewAPI-->>Client: Error: Please fix your review
            else Review is good
                HBnBFacade->>+ReviewModel: Create new review
                ReviewModel->>+ReviewRepository: Save this review
                ReviewRepository-->>-ReviewModel: Review saved successfully
                ReviewModel-->>-HBnBFacade: Review is now created
                HBnBFacade->>PlaceModel: Update place's average rating
                PlaceModel-->>HBnBFacade: Rating updated
                HBnBFacade-->>-ReviewAPI: Review is complete
                ReviewAPI->>ReviewAPI: Prepare success message
                ReviewAPI-->>-Client: Success: Your review is published!
            end
        end
    end
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