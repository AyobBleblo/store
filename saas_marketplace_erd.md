# SaaS Marketplace (Mapp) + Social Commerce ERD

This document contains the production-level Entity-Relationship Diagram (ERD) and architecture details for your multi-tenant SaaS Social Commerce platform.

## Mermaid ER Diagram

```mermaid
erDiagram
    %% Core System
    Users ||--o{ Stores : "owns (1:N)"
    
    %% Commerce System
    Stores ||--o{ Products : "has (1:N)"
    Products ||--o{ CartItems : "added to (1:N)"
    Products ||--o{ OrderItems : "part of (1:N)"
    
    %% Customers & Marketplace
    Stores ||--o{ StoreFollowers : "followed by (1:N)"
    Customers ||--o{ StoreFollowers : "follows (1:N)"
    
    %% Carts and Checkout (1 Store per Cart)
    Stores ||--o{ Carts : "contains (1:N)"
    Customers ||--o{ Carts : "creates (1:N)"
    Carts ||--o{ CartItems : "has items (1:N)"
    
    %% Order Management
    Stores ||--o{ Orders : "receives (1:N)"
    Customers ||--o{ Orders : "places (1:N)"
    Orders ||--o{ OrderItems : "has items (1:N)"
    
    %% Social & Messaging System
    Stores ||--o{ Messages : "manages (1:N)"
    Customers ||--o{ Messages : "sends/receives (1:N)"
    Orders |o--o{ Messages : "linked to (0:N)"


    %% ================= ENTITIES ================= %%

    Users {
        uuid id PK
        string email UK
        string password
        string role "admin, store_owner"
        datetime created_at
    }

    Stores {
        uuid id PK
        uuid owner_id FK
        string name
        string description
        boolean is_active
        datetime created_at
    }

    Customers {
        uuid id PK
        string name
        string phone
        string email "nullable"
        datetime created_at
    }

    StoreFollowers {
        uuid id PK
        uuid store_id FK
        uuid customer_id FK
    }

    Products {
        uuid id PK
        uuid store_id FK
        string name
        string description
        decimal price
        integer stock
        boolean is_active
        datetime created_at
    }

    Carts {
        uuid id PK
        uuid customer_id FK
        uuid store_id FK
        string status "active, converted, abandoned"
        datetime created_at
        datetime updated_at
    }

    CartItems {
        uuid id PK
        uuid cart_id FK
        uuid product_id FK
        integer quantity
        decimal price
    }

    Orders {
        uuid id PK
        uuid store_id FK
        uuid customer_id FK
        string status "pending, shipped, delivered"
        decimal total_price
        string source "web, whatsapp, facebook"
        datetime created_at
    }

    OrderItems {
        uuid id PK
        uuid order_id FK
        uuid product_id FK
        integer quantity
        decimal price
    }

    Messages {
        uuid id PK
        uuid store_id FK
        uuid customer_id FK
        uuid order_id FK "nullable"
        string message_text
        string message_type "text, image"
        string direction "incoming, outgoing"
        string source "whatsapp, facebook"
        string status "new, handled"
        datetime created_at
    }
```

## Schema Domains & Groupings

### 1. Core (Multi-Tenant Administration)
- **`Users`**: Admin or store owners. Authenticates platform and tenant management access.
- **`Stores`**: Tenants on your platform. Includes basic tenant metadata. `owner_id` establishes which user controls it.

### 2. Marketplace 
- **`Customers`**: The end consumer layer. They are global across the application (multi-tenant marketplace concept) so they can buy from any store.
- **`StoreFollowers`**: Tracks customer affinity mapping to stores. Enables marketplace-style feeds and targeted marketing.

### 3. Commerce (Catalogs & Fulfillment)
- **`Products`**: Catalog elements strictly isolated directly to a single `Stores` tenant via `store_id`.
- **`Carts`**: Simplified for the MVP by enforcing a `store_id` parameter. Ensures customers cannot create complex multi-seller checkouts reducing transaction overhead and vendor routing.
- **`CartItems`**: Tied to `Carts`, maps specific quantities of `Products` ready for order projection.
- **`Orders` & `OrderItems`**: The final commercial receipt. Tracks total price, statuses, and links specifically to individual stores and customers.

### 4. Social / AI Context
- **`Messages`**: Ties conversations from WhatsApp/FB directly to a `store_id` and a `customer_id`. Can be optionally linked to a specific `order_id` if a question or custom request initiates an order. 
- *Future AI Readines*: Structuring this manually with specific explicit sources (`message_type`, `direction`, `source`) pre-optimizes for an AI service or LLM ingestion engine (such as LangChain/RAG architectures that contextualize previous order history alongside live WhatsApp text streams).

## Scalability & Production Indices
Use standard B-Tree indexing effectively, especially as SaaS tables swell rapidly across multiple tenants. Note that clustered indices matter for UUID architectures (Use sequential/v7 UUIDs if possible on insert-heavy large models to stop fragmentation).

**Key Index Locations:**
* Every table should have an index on `store_id` (Tenant isolating filtering is the most frequent query).
* **Queries**: Composite index on `Messages (store_id, customer_id, created_at)` for highly efficient timeline reconstructions and fast query loading of inbox feeds.
* **Filter Opts**: Single index everywhere on `is_active` for Shops and Products.
* **Order Analysis**: Index on `Orders(store_id, status)` + `Orders(source)` for rapid merchant dashboard insights.
