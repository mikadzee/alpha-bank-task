CREATE TABLE IF NOT EXISTS application_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    application_id UUID NOT NULL REFERENCES applications(id) ON DELETE CASCADE,
    actor_user_id UUID REFERENCES users(id) ON DELETE SET NULL,
    event_type VARCHAR(40) NOT NULL,
    from_status VARCHAR(30),
    to_status VARCHAR(30),
    note TEXT NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_application_events_timeline
    ON application_events(application_id, created_at, id);

ALTER TABLE applications ADD COLUMN IF NOT EXISTS offer_data JSONB;
ALTER TABLE applications DROP CONSTRAINT IF EXISTS applications_status_check;
ALTER TABLE applications ADD CONSTRAINT applications_status_check
    CHECK (status IN ('draft', 'pending', 'needs_info', 'approved', 'rejected', 'offer_made', 'offer_accepted', 'offer_declined'));

INSERT INTO application_events (application_id, event_type, to_status, note, created_at)
SELECT id, 'draft_created', 'draft', 'Черновик заявки создан', created_at
FROM applications
WHERE NOT EXISTS (
    SELECT 1 FROM application_events event
    WHERE event.application_id = applications.id
);

INSERT INTO application_events (application_id, event_type, to_status, note, created_at)
SELECT id, 'submitted', 'pending', 'Заявка отправлена в банк', submitted_at
FROM applications
WHERE submitted_at IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM application_events event
      WHERE event.application_id = applications.id AND event.event_type = 'submitted'
  );

INSERT INTO application_events (application_id, actor_user_id, event_type, from_status, to_status, note, created_at)
SELECT id, reviewed_by, 'decision', 'pending', status,
       COALESCE(review_comment, 'Решение банка зафиксировано'), reviewed_at
FROM applications
WHERE reviewed_at IS NOT NULL
  AND NOT EXISTS (
      SELECT 1 FROM application_events event
      WHERE event.application_id = applications.id AND event.event_type = 'decision'
  );
