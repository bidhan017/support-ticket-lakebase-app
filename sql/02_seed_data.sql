INSERT INTO support.tickets (title, status, priority, created_by) VALUES
  ('Login fails on mobile', 'open', 'high', 'alice@example.com'),
  ('Data export timeout', 'in_progress', 'medium', 'bob@example.com'),
  ('Dashboard shows stale metrics', 'resolved', 'low', 'carol@example.com');

INSERT INTO support.ticket_messages (ticket_id, message_text, author) VALUES
  (1, 'User reports error code 503 when logging in via iOS app.', 'alice@example.com'),
  (1, 'Reproduced on staging; investigating auth service logs.', 'support-bot'),
  (2, 'Export job >10M rows hangs after 5 minutes.', 'bob@example.com'),
  (2, 'Working on pagination + server-side streaming fix.', 'support-bot'),
  (3, 'Metrics panel not refreshing after latest deploy.', 'carol@example.com'),
  (3, 'Cache invalidation fixed; marking resolved.', 'support-bot');