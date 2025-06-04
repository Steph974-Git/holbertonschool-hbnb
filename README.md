# HBnB Project – Technical Documentation

## 1. Introduction

Ce document technique présente l’architecture du projet **HBnB**, une plateforme de location de logements inspirée d’Airbnb.

Il regroupe l’ensemble des diagrammes UML créés lors des étapes de conception :
- Le **diagramme de packages** (architecture en couches),
- Le **diagramme de classes métier** (Business Logic Layer),
- Les **diagrammes de séquence** illustrant le flux des appels API.

Ce document sert de **référence technique** pour les phases de développement, garantissant clarté, cohérence et maintenabilité du système.

---

## 2. High-Level Architecture

### 2.1 Diagramme de packages

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

### 2.2 Description de l’architecture en couches

Le système est basé sur une architecture en couches :

- **Couche API (Interface)** : gère les requêtes REST, agit comme façade.
- **Couche Logique Métier** : contient les règles métier (création d’utilisateurs, d’avis, etc.)
- **Couche de Stockage** : interaction avec les fichiers ou la base de données.

Cette séparation permet une bonne **modularité**, **testabilité** et **maintenabilité** du code.

---

## 3. Business Logic Layer

### 3.1 Diagramme de classes métier

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

### 3.2 Description des entités et relations

#### 🔸 Base
Classe abstraite commune, fournit : `id`, `created_at`, `updated_at`.

#### 🔸 User
Représente un utilisateur :
- Attributs : `first_name`, `last_name`, `email`, `is_admin`, etc.
- Méthodes : `register()`, `delete()`, etc.
- Hérite de `Base`.
- **Composition** avec `Place` : un `User` possède ses `Place`.

#### 🔸 Place
Représente un logement publié :
- Attributs : `title`, `price`, `latitude`, etc.
- Méthodes : `create()`, `update()`, etc.
- Composé dans `User`, agrège des `Review`.

#### 🔸 Review
Représente un avis :
- Attributs : `rating`, `comment`
- Méthodes : `submit()`, `edit()`
- Lié à `User` et `Place` via associations simples

#### 🔸 Amenity
Représente un équipement (Wi-Fi, etc.)
- Associé via `PlaceAmenity`
- Vit indépendamment des `Place`

#### 🔸 PlaceAmenity
Table d’association entre `Place` et `Amenity`
- **Composé dans `Place`**
- **Agrégé par `Amenity`**

---

## 4. API Interaction Flow

### 4.1 Diagrammes de séquence

```mermaid
---
config:
  theme: redux-dark-color
  look: neo
title: User Registration
---
sequenceDiagram
    participant Client as User Device
    participant UserAPI as Registration API
    participant HBnBFacade as Main Service
    participant UserModel as User Creator
    participant PasswordService as Password Service
    participant EmailService as Email Service
    participant UserRepository as User Database
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
    participant Client as User's Device
    participant PlaceAPI as API Endpoint
    participant HBnBFacade as Main Service
    participant UserModel as User Database
    participant PlaceModel as Place Creator
    participant LocationService as Address Checker
    participant AmenityRepository as Amenities List 
    participant PlaceRepository as Place Storage
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

Exemples recommandés :
- Création d’un `Place` par un utilisateur
- Écriture d’un `Review`
- Suppression d’un compte utilisateur

### 4.2 Explication des scénarios

#### Exemple : Écriture d’un avis

1. L’utilisateur authentifié soumet un avis via l’API.
2. L’API valide l’authentification et le format.
3. Le `Review` est créé dans la couche métier.
4. Le `Review` est lié à l’utilisateur et au logement.
5. L’objet est sauvegardé en base.

---

## 5. Conclusion *(optionnel)*

Ce document constitue la **base de référence** technique du projet HBnB.  
Il permet de guider la mise en œuvre du système en respectant les règles métier, les interactions entre couches et les contraintes de conception.

---

## 📎 Annexes *(optionnel)*

- Liens vers les sources (guides UML, style guides)
- Références du projet ou outils utilisés (Mermaid, PlantUML, etc.)
