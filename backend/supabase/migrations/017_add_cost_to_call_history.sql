-- Add cost field to call_history table
ALTER TABLE call_history
ADD COLUMN IF NOT EXISTS cost DECIMAL(10, 4);

-- Add index for filtering by outcome
CREATE INDEX IF NOT EXISTS idx_call_history_outcome ON call_history (outcome);

CREATE INDEX IF NOT EXISTS idx_call_history_started_at ON call_history (started_at DESC);