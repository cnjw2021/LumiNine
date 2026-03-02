Refactor the model class in `backend/core/models/abc.py` according to the instructions below.

---

### GOAL

Refactor the existing SQLAlchemy model class, which currently follows the Active Record pattern, into a clean architecture structure. The responsibilities must be clearly separated into four distinct layers: Route, UseCase, Domain, and Infrastructure.

---
### **1. Route Layer (Controller)**

-   **Location**: `backend/apps/ninestarki/routes`
-   **Responsibility**: Handles HTTP requests and responses. Contains no business logic.
-   **Tasks**:
    -   Define Flask Blueprint endpoints.
    -   Inject or instantiate the appropriate UseCase.
    -   Parse request data, call the `use_case.execute()` method, and return a formatted response (`jsonify`).

---
### **2. UseCase Layer (Application Business Logic)**

-   **Location**: `backend/apps/ninestarki/use_cases`
-   **Responsibility**: Orchestrates a specific application feature. Depends only on interfaces from the Domain layer.
-   **Tasks**:
    -   Inject Repository **Interfaces** via the constructor (`__init__`).
    -   Implement an `execute()` method containing the business logic flow.

---
### **3. Domain Layer (Core Business Logic & Entities)**

-   **Responsibility**: Core business rules and data structures. Must have no dependencies on outer layers.

-   **3.1. Entity**
    -   **Location**: `backend/apps/ninestarki/domain/entities`
    -   **Tasks**:
        -   Define the Entity class. For this project, we will pragmatically continue to use the SQLAlchemy declarative base (`db.Model`) as our entity, but it must be stripped of all other responsibilities. It should only contain the column (`db.Column`) and relationship (`db.relationship`) definitions.
        -   Include only methods that operate on the entity's own data (e.g., password hashing, `to_dict()`).
        -   **Crucially, all methods that perform direct DB queries (e.g., `Model.query...`) must be removed.**

-   **3.2. Repository Interface**
    -   **Location**: `backend/apps/ninestarki/domain/repositories`
    -   **Tasks**:
        -   Define an abstract interface (ABC) for data persistence.
        -   Declare methods like `find_by_id()` and `save()` using `@abstractmethod` without implementation.

-   **3.3. Domain Service**
    -   **Location**: `backend/apps/ninestarki/domain/services`
    -   **Tasks**:
        -   Implement stateless business logic that doesn't fit into a single Entity (e.g., complex calculations).
        -   **If any existing service classes in `apps/ninestarki/services` contain pure, stateless business logic, refactor and move them to this layer.**
        -   Depends only on other Domain components (Entities, Repository Interfaces).

---
### **4. Infrastructure Layer (External Concerns)**

-   **Responsibility**: Implements the concrete details of external concerns like the database.

-   **4.1. Repository Implementation**
    -   **Location**: `backend/apps/ninestarki/infrastructure/persistence`
    -   **Tasks**:
        -   Create a concrete class that **implements the Repository Interface**.
        -   **Use `session: Session = db.session` as default parameter in constructor.**
        -   **Use `self.session.query(Model)` for database operations instead of `Model.query`.**
        -   All SQLAlchemy database operations must be located here using session-based queries.