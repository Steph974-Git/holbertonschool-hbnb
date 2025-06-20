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
        class UserModel {
            -id: String
            -email: String
            -name: String
            -hashedPassword: String
            +validate()
            +isPasswordValid(password)
            +getPublicProfile()
        }
        class PlaceModel {
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
        class ReviewModel {
            -id: String
            -placeId: String
            -authorId: String
            -rating: Number
            -comment: String
            -date: Date
            +validate()
        }
        class AmenityModel {
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
    HBnBFacade --> UserModel : delegate
    HBnBFacade --> PlaceModel : delegate
    HBnBFacade --> ReviewModel : delegate
    HBnBFacade --> AmenityModel : delegate
    UserModel --> UserRepository : access data
    PlaceModel --> PlaceRepository : access data
    ReviewModel --> ReviewRepository : access data
    AmenityModel --> AmenityRepository : access data
```

### 2.2 Description of the Layered Architecture

The system is based on a layered architecture:

- **API Layer (Interface)**: handles REST requests, acts as a facade.
- **Business Logic Layer**: contains business rules (user creation, reviews, etc.)
- **Storage Layer**: interaction with files or database.

This separation allows for good **modularity**, **testability**, and **maintainability** of the code.

### 2.3 Detailed Package Diagram Analysis

The package diagram illustrates the three-tier architecture of the HBnB system, designed with clear separation of concerns:

1. **Presentation Layer (PresentationLayer)**:
   - Functions as the external interface for all client interactions through standardized REST APIs
   - `UserAPI` handles the complete user lifecycle (registration, authentication, profile management)
   - `PlaceAPI` centralizes all accommodation operations (listing creation, search with complex criteria, updates)
   - `ReviewAPI` manages the entire review process (submission, retrieval, filtering)
   - `BookingService` orchestrates the booking workflow from request to confirmation or cancellation
   - This layer validates input data format but delegates business rule validation to lower layers

2. **Business Logic Layer (BusinessLogicLayer)**:
   - Implements the Facade pattern through `HBnBFacade`, providing a simplified interface to complex subsystems
   - Contains domain entities with encapsulated business rules:
     - `User`: handles authentication logic, password policies, and profile validation
     - `Place`: manages pricing rules, availability calculations, and listing requirements
     - `Review`: enforces rating guidelines and content policies
     - `Amenity`: standardizes facility categorization and representation
   - Business logic is isolated from both presentation concerns and data persistence implementation

3. **Persistence Layer (PersistenceLayer)**:
   - Implements the Repository pattern to abstract data access operations
   - Each repository specializes in data operations for a specific entity type:
     - `UserRepository`: handles user credential verification and profile retrieval
     - `PlaceRepository`: supports complex geographical and feature-based queries
     - `ReviewRepository`: manages aggregations like average ratings and filtering
     - `AmenityRepository`: enables categorization and classification of amenities
   - This layer can be adapted to different storage solutions (SQL/NoSQL databases, file systems) without affecting upper layers

The architecture follows key design principles:
- **Dependency Inversion**: Higher layers depend on abstractions, not implementations
- **Single Responsibility**: Each component has a focused, well-defined purpose
- **Interface Segregation**: APIs are tailored to specific client needs
- **Open/Closed**: The system can be extended without modifying existing code

This structured approach enables independent development, comprehensive testing, and easier maintenance as the system evolves.


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

### 3.3 In-Depth Business Class Diagram Analysis

The business class diagram reveals the domain model structure and relationships with these key elements:

1. **Abstract `Base` Class**:
   - Serves as the foundation for all persistent entities in the system
   - Implements the concept of entity identity through UUID generation
   - Provides automatic temporal tracking (`created_at`, `updated_at`) for audit trails
   - Creates a consistent interface for common operations across all derived classes
   - Standardizes serialization/deserialization behaviors for all model objects

2. **Entity Relationships and Semantics**:
   - **Composition relationship** (`*--`) between `UserModel` and `PlaceModel`:
     - Indicates strong ownership and lifecycle dependency
     - When a user is deleted, all their places are automatically removed
     - A place cannot exist independently of its owner
   
   - **Composition relationship** between `PlaceModel` and `ReviewModel`:
     - Reviews are dependent on the existence of their associated place
     - Deletion of a place cascades to removal of all its reviews
   
   - **Aggregation relationship** (`o--`) between `AmenityModel` and `PlaceAmenity`:
     - Amenities exist independently of any specific place
     - The same amenity can be associated with multiple places
     - Deleting a place doesn't affect the amenity itself, only the association

   - **Multiplicities** provide important cardinality constraints:
     - "1" to "*" between User and Place: a user can own multiple places
     - "1" to "*" between Place and Review: a place can have multiple reviews
     - "1" to "*" between Amenity/Place and PlaceAmenity: implements many-to-many relationship

3. **Attribute Visibility and Encapsulation**:
   - **Public attributes** (`+`): Accessible throughout the system
     - Used for attributes that need wide visibility for business operations
   
   - **Private attributes** (`-`): Internal to their containing class
     - Protects sensitive data (e.g., `password` in `UserModel`) from unauthorized access
     - Forces access through controlled methods that can apply validation and business rules
   
   - **Methods** implement behavior specific to each entity type:
     - CRUD operations (`create()`, `update()`, `delete()`)
     - Business validations (`validate()`)
     - Entity-specific operations (`register()` for users, `submit()` for reviews)

This domain model structure enables:
- Precise representation of business concepts and relationships
- Data integrity through relationship constraints
- Security through proper encapsulation
- Clear separation between data structure and behavior

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
##  User Registration

###  Purpose
Allow a new user to securely register an account.

###  Flow Description
1. The **Client** submits the sign-up form.
2. The **UserAPI** checks if all required fields are filled.
3. Data is sent to **HBnBFacade** for processing.
4. **HBnBFacade** validates the input (age, password strength, etc.).
5. It queries the **UserRepository** to check if the email already exists.
6. If the email is **available**:
   - **PasswordService** secures the password.
   - The **UserModel** creates a new user and saves it.
   - A welcome email is sent via **EmailService**.
   - The client receives a success message.
7. If the email is **already used**:
   - An error message is returned to the client.

###  Key Considerations
- Email uniqueness check.
- Secure password encryption.
- Full input validation.

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
    participant PlaceRepository

    Client->>+PlaceAPI: Submit new property listing
    PlaceAPI->>PlaceAPI: Check if listing is complete
    PlaceAPI->>+HBnBFacade: Create this property listing

    HBnBFacade->>+UserModel: Can this user add listings?
    UserModel-->>-HBnBFacade: User permission

    alt User not permitted
        HBnBFacade-->>PlaceAPI: User can't add listings
        PlaceAPI-->>Client: Error: Not authorized
    else
        HBnBFacade->>HBnBFacade: Basic property checks
        Note over HBnBFacade: Check price, title, description

        HBnBFacade->>+PlaceModel: Create new property
        PlaceModel->>+PlaceRepository: Save property
        PlaceRepository-->>-PlaceModel: Saved
        PlaceModel-->>-HBnBFacade: Created
        
        HBnBFacade-->>PlaceAPI: Property listing created
        PlaceAPI-->>Client: Success: Your listing is live!
    end
```
---

##  Place Creation

###  Purpose
Enable a user to create and publish a property listing.

###  Flow Description
1. The **Client** submits a new property form via **PlaceAPI**.
2. The API validates form completeness.
3. The request is passed to **HBnBFacade**.
4. **HBnBFacade** checks the user's permission via **UserModel**.
5. If the user is **not allowed**, an error is returned.
6. If the user is **authorized**:
   - Basic checks are performed (price, description, title).
   - **PlaceModel** creates a property object and saves it.
   - A confirmation is returned to the client.

###  Key Considerations
- Permission checks.
- Data validation before saving.
- Proper storage in **PlaceRepository**.
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
    
    Client->>+ReviewAPI: Submit new review
    ReviewAPI->>ReviewAPI: Check required fields
    ReviewAPI->>+HBnBFacade: Process review
    
    HBnBFacade->>+UserModel: Verify user
    UserModel-->>-HBnBFacade: User status
    
    alt User invalid
        HBnBFacade-->>ReviewAPI: Not authorized
        ReviewAPI-->>Client: Error: Not allowed
    else User valid
        HBnBFacade->>+PlaceModel: Verify place
        PlaceModel-->>-HBnBFacade: Place status
        
        alt Place invalid
            HBnBFacade-->>ReviewAPI: Place not found
            ReviewAPI-->>Client: Error: Place not found
        else Place valid
            HBnBFacade->>HBnBFacade: Check review quality
            
            alt Review invalid
                HBnBFacade-->>ReviewAPI: Invalid content
                ReviewAPI-->>Client: Error: Fix your review
            else Review valid
                HBnBFacade->>ReviewStorage: Save review
                ReviewStorage-->>HBnBFacade: Saved review
                
                HBnBFacade->>PlaceModel: Update rating
                PlaceModel-->>HBnBFacade: Updated
                
                HBnBFacade-->>ReviewAPI: Review created
                ReviewAPI-->>Client: Success: Review published
            end
        end
    end
```
---

##  Review Submission

###  Purpose
Let users write reviews about places they've visited.

###  Flow Description
1. The **Client** submits a review through **ReviewAPI**.
2. The API checks for required fields.
3. The review is passed to **HBnBFacade**.
4. **HBnBFacade**:
   - Verifies user identity via **UserModel**.
   - Checks if the place exists via **PlaceModel**.
5. If the user or place is **invalid**, an error is returned.
6. If both are **valid**:
   - The review content is checked for quality.
   - It is saved to **ReviewStorage**.
   - The place’s rating is updated.
   - A success message is sent to the client.

###  Key Considerations
- User and place verification.
- Content quality control.
- Real-time rating updates.
```mermaid
---
config:
  theme: redux-dark-color
  look: neo
title: Fetching a List of Places
---
sequenceDiagram
    participant Client
    participant PlaceAPI
    participant HBnBFacade
    participant SearchService
    participant PlaceRepository
    participant AmenityRepository
    
    activate Client
    Client->>+PlaceAPI: GET /places (search criteria)
    activate PlaceAPI
    Note over Client,PlaceAPI: Location, price, amenities, dates
    
    PlaceAPI->>PlaceAPI: Validate search parameters
    PlaceAPI->>+HBnBFacade: searchPlaces(filters)
    activate HBnBFacade
    
    HBnBFacade->>+SearchService: processSearch(searchCriteria)
    activate SearchService
    SearchService->>SearchService: Optimize search query
    Note over SearchService: Convert location to coordinates, normalize filters
    
    alt Location and amenities specified
        SearchService->>+AmenityRepository: getAmenityIds(amenityNames)
        AmenityRepository-->>SearchService: Fetched amenity IDs
        
        SearchService->>+PlaceRepository: findByLocationAndAmenities(...)
        PlaceRepository-->>-SearchService: Filtered properties
    else Other search criteria
        SearchService->>+PlaceRepository: findByFilters(processedFilters)
        PlaceRepository-->>-SearchService: Matching properties
    end
    
    SearchService->>SearchService: Apply additional filters
    Note over SearchService: Handle price range, dates, etc.
    
    SearchService-->>-HBnBFacade: Filtered search results
    
    HBnBFacade->>HBnBFacade: Sort and paginate results
    Note over HBnBFacade: Order by relevance and limit results per page
    
    HBnBFacade->>HBnBFacade: Prepare place details
    Note over HBnBFacade: Format for public view
    
    HBnBFacade-->>-PlaceAPI: searchResults object
    
    PlaceAPI->>PlaceAPI: Format response
    PlaceAPI-->>-Client: 200 OK (places list with details)
    deactivate Client

```
---

##  Fetching a List of Places

###  Purpose
Allow users to search for available properties based on specific criteria.

###  Flow Description
1. The **Client** sends a GET request with filters (e.g., location, price, dates).
2. **PlaceAPI** validates search parameters.
3. The request is forwarded to **HBnBFacade**, then to **SearchService**.
4. **SearchService**:
   - Optimizes the search (location coordinates, normalize filters).
   - If amenities are included:
     - Queries **AmenityRepository** for IDs.
     - Calls **PlaceRepository** for matching results.
   - Otherwise, filters directly via **PlaceRepository**.
5. Results are post-processed:
   - Additional filters (price range, availability) are applied.
   - Results are sorted and paginated.
6. Results are formatted and returned to the client.

###  Key Considerations
- Efficient query optimization.
- Filter precision (especially for amenities and dates).
- User-friendly output format.

---

Recommended examples:
- Creation of a `Place` by a userOh, she said. It's much more than not to be here. 
- Writing a `Review`
- Deletion of a user account

### 4.2 Explanation of Scenarios

#### Example: Writing a review

1. The authenticated user submits a review via the API.
2. The API validates authentication and format.
3. The `Review` is created in the business layer.
4. The `Review` is linked to the user and accommodation.
5. The object is saved in the database.

### 4.3 Detailed Sequence Diagram Analysis

The sequence diagrams illustrate the runtime behavior of key system operations:

#### User Registration Sequence

1. **Request Processing and Validation**:
   - The flow begins with client input and proceeds through multiple validation layers
   - Initial validation in `UserAPI` checks basic request format requirements
   - Business validation in `HBnBFacade` enforces rules like password strength and age requirements
   - Existing email check demonstrates proper validation before attempting resource creation

2. **Error Handling Strategy**:
   - The diagram shows comprehensive error handling with different response codes
   - Error messages include specific details to guide the client
   - Each error is detected at the appropriate layer and propagated upward
   - This approach demonstrates the system's robustness against invalid inputs

3. **Security and Support Services**:
   - `PasswordService` shows proper security practices for credential handling:
     - Password hashing occurs before storage
     - Original passwords never persist in the system
   - `EmailService` demonstrates integration with external notification systems
   - Both services are properly abstracted behind interfaces for testability

#### Place Creation Sequence

1. **Authorization and Validation Hierarchy**:
   - Demonstrates multi-level validation strategy:
     - Format validation at API layer
     - Permission checking through user verification
     - Business rule validation for place properties
     - External validation through location service
   - Each validation occurs at the appropriate architectural layer

2. **Complex Entity Creation Process**:
   - Shows how creating a place involves multiple components and steps
   - Illustrates verification of reference entities (amenities)
   - Demonstrates proper handling of related entities
   - Models a realistic business process with appropriate complexity

3. **Transactional Integrity**:
   - The diagram shows how the system maintains consistency:
     - Place creation with amenities is handled as an atomic operation
     - Failure at any step results in complete operation failure
     - No partial updates are committed to the database
   - This approach prevents data inconsistencies in the system

#### Review Submission Sequence

1. **Multi-entity Verification**:
   - The process validates both the user submitting the review and the place being reviewed
   - Shows how relationships between entities are verified before allowing operations
   - Demonstrates proper access control based on user identity

2. **Content Quality Control**:
   - Illustrates validation of review content quality (rating range, comment length)
   - Shows how business rules are applied to maintain data quality
   - Demonstrates rejection of substandard content with appropriate feedback

3. **Cascading Updates**:
   - Shows how a single review submission triggers updates to related entities
   - The place's average rating is recalculated after review submission
   - Demonstrates maintenance of derived data for performance optimization

These sequence diagrams serve as:
- Executable specifications for developers
- Documentation for cross-team collaboration
- Verification tools for architecture compliance
- Reference for testing scenarios and edge cases

---

## 5. Conclusion

This document constitutes the **technical reference base** for the HBnB project.  
It guides the implementation of the system while respecting business rules, interactions between layers, and design constraints.

---

## 📎 Appendices

### UML and Design Resources
- [UML Specification](https://www.omg.org/spec/UML/)
- [Mermaid JS Documentation](https://mermaid-js.github.io/mermaid/#/)
- [Design Patterns in Software Engineering](https://refactoring.guru/design-patterns)

### Architecture References
- [The Clean Architecture by Robert C. Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design by Eric Evans](https://domainlanguage.com/ddd/)
- [Microservices Patterns by Chris Richardson](https://microservices.io/patterns/index.html)

### Development Standards
- [RESTful API Design Best Practices](https://restfulapi.net/)
- [SOLID Principles](https://en.wikipedia.org/wiki/SOLID)
- [Test-Driven Development Methodology](https://www.agilealliance.org/glossary/tdd/)