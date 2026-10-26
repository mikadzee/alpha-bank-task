# Модель данных

```mermaid
erDiagram
  USERS ||--o{ AUTH_SESSIONS : authenticates
  USERS ||--o{ CLIENT_COMPANIES : owns
  USERS ||--o{ APPLICATIONS : creates
  USERS o|--o{ APPLICATIONS : reviews
  APPLICATIONS ||--o{ DOCUMENTS : contains
  APPLICATIONS ||--o{ APPLICATION_EVENTS : records
  LOAN_PRODUCTS o|--o{ APPLICATIONS : selected_for
  USERS {
    uuid id PK
    string email UK
    string password_hash
    string role
  }
  AUTH_SESSIONS {
    uuid id PK
    uuid user_id FK
    string refresh_token_hash
    timestamp expires_at
    timestamp revoked_at
  }
  CLIENT_COMPANIES {
    uuid id PK
    uuid user_id FK
    string inn
    string company_name
    string okved
  }
  APPLICATIONS {
    uuid id PK
    uuid user_id FK
    uuid selected_product_id FK
    json company_data
    json financial_data
    string status
    uuid reviewed_by FK
  }
  DOCUMENTS {
    uuid id PK
    uuid application_id FK
    string document_type
    string storage_path
    string mime_type
  }
  APPLICATION_EVENTS {
    uuid id PK
    uuid application_id FK
    uuid actor_user_id FK
    string event_type
    string from_status
    string to_status
  }
  LOAN_PRODUCTS {
    uuid id PK
    string code UK
    string purpose
    decimal annual_rate
  }
```

`company_data` и `financial_data` — JSONB снимок сведений именно на момент заявки; справочник компаний можно обновлять отдельно, не меняя прошлые заявки. Файлы вне БД, в таблице находятся метаданные и путь в приватном volume. Внешние идентификаторы ФНС/БКИ не хранятся, так как интеграций в MVP нет.
