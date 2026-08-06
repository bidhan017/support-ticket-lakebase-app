-- Optional: create a dedicated schema for this app
CREATE SCHEMA IF NOT EXISTS support;

-- Tickets table
CREATE TABLE IF NOT EXISTS support.tickets (
  ticket_id      BIGSERIAL PRIMARY KEY,
  title          TEXT NOT NULL,
  status         TEXT NOT NULL CHECK (status IN ('open','in_progress','resolved')),
  priority       TEXT NOT NULL DEFAULT 'medium' CHECK (priority IN ('low','medium','high')),
  created_by     TEXT NOT NULL,
  created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Messages table (FK to tickets)
CREATE TABLE IF NOT EXISTS support.ticket_messages (
  message_id   BIGSERIAL PRIMARY KEY,
  ticket_id    BIGINT NOT NULL REFERENCES support.tickets(ticket_id) ON DELETE CASCADE,
  message_text TEXT NOT NULL,
  author       TEXT NOT NULL,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);