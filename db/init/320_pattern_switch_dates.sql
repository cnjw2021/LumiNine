-- 陽遁・隠遁 切替日マスタ

CREATE TABLE IF NOT EXISTS pattern_switch_dates (
  id         INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  date       DATE        NOT NULL UNIQUE,
  pattern    VARCHAR(10) NOT NULL CHECK (pattern IN ('SP_ASC','SP_DESC')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
