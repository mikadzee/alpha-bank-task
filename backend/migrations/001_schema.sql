CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'client' CHECK (role = 'client'),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS auth_sessions (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_token_hash TEXT NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_auth_sessions_user_id ON auth_sessions(user_id);

CREATE TABLE IF NOT EXISTS loan_products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(40) NOT NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    purpose VARCHAR(40) NOT NULL,
    description TEXT NOT NULL DEFAULT '',
    min_amount NUMERIC(15, 0) NOT NULL CHECK (min_amount > 0),
    max_amount NUMERIC(15, 0) NOT NULL CHECK (max_amount >= min_amount),
    min_term_months INTEGER NOT NULL CHECK (min_term_months > 0),
    max_term_months INTEGER NOT NULL CHECK (max_term_months >= min_term_months),
    annual_rate NUMERIC(6, 3) NOT NULL CHECK (annual_rate >= 0),
    is_active BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS applications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    company_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    financial_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    selected_product_id UUID REFERENCES loan_products(id),
    status VARCHAR(20) NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'pending')),
    submitted_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_applications_user_updated ON applications(user_id, updated_at DESC);

CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    document_type VARCHAR(40) NOT NULL,
    original_name TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    size_bytes BIGINT NOT NULL CHECK (size_bytes > 0),
    uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_documents_application ON documents(application_id, uploaded_at);

CREATE TABLE IF NOT EXISTS mock_companies (
    inn VARCHAR(12) PRIMARY KEY,
    company_name VARCHAR(255) NOT NULL,
    ogrn VARCHAR(15),
    address TEXT,
    okved VARCHAR(20) NOT NULL DEFAULT ''
);
