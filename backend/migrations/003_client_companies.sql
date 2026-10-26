CREATE TABLE IF NOT EXISTS client_companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    inn VARCHAR(12) NOT NULL,
    ogrn VARCHAR(15) NOT NULL DEFAULT '',
    company_name VARCHAR(255) NOT NULL,
    address TEXT NOT NULL DEFAULT '',
    okved VARCHAR(20) NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, inn)
);

CREATE INDEX IF NOT EXISTS idx_client_companies_user_updated
    ON client_companies(user_id, updated_at DESC);

INSERT INTO client_companies (user_id, inn, ogrn, company_name, address, okved, updated_at)
SELECT DISTINCT ON (applications.user_id, applications.company_data ->> 'inn')
    applications.user_id,
    applications.company_data ->> 'inn',
    COALESCE(applications.company_data ->> 'ogrn', ''),
    COALESCE(applications.company_data ->> 'companyName', ''),
    COALESCE(applications.company_data ->> 'address', ''),
    COALESCE(applications.company_data ->> 'okved', ''),
    applications.updated_at
FROM applications
WHERE COALESCE(applications.company_data ->> 'inn', '') <> ''
  AND COALESCE(applications.company_data ->> 'companyName', '') <> ''
ORDER BY applications.user_id, applications.company_data ->> 'inn', applications.updated_at DESC
ON CONFLICT (user_id, inn) DO NOTHING;
