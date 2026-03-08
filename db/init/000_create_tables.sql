-- ================================================================
-- 九星気学 PostgreSQL スキーマ
-- MySQL (mysql/init/000_create_tables.sql) からの移行版
-- 変更点:
--   AUTO_INCREMENT → GENERATED ALWAYS AS IDENTITY
--   ENGINE=InnoDB / CHARSET=utf8mb4 → 削除
--   ON UPDATE CURRENT_TIMESTAMP → トリガー対応 (updated_atは挿入時のみ設定)
--   UNIQUE KEY name (col) → CONSTRAINT name UNIQUE (col)
--   `backtick` → "double_quote" (省略して無クォート)
-- ================================================================

-- 九星の基本情報テーブル
CREATE TABLE IF NOT EXISTS stars (
  star_number INT PRIMARY KEY,
  name_jp     VARCHAR(50)  NOT NULL,
  name_en     VARCHAR(50)  NOT NULL,
  element     VARCHAR(20)  NOT NULL,
  keywords    VARCHAR(255) NOT NULL,
  description TEXT,
  created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

-- 暦情報テーブル（節入り日など）
CREATE TABLE IF NOT EXISTS solar_starts (
  year              INT PRIMARY KEY,
  solar_starts_date DATE        NOT NULL,
  solar_starts_time TIME        NOT NULL,
  zodiac            VARCHAR(10) NOT NULL,
  star_number       INT         NOT NULL,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS solar_terms (
  id                BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  year              INT         NOT NULL,
  month             INT         NOT NULL,
  solar_terms_date  DATE        NOT NULL,
  solar_terms_time  TIME        NOT NULL,
  solar_terms_name  VARCHAR(20) NOT NULL,
  zodiac            VARCHAR(10) NOT NULL,
  star_number       INT         NOT NULL,
  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_solar_terms_year_month UNIQUE (year, month)
);

-- 日付ごとの干支と九星の情報を保存するテーブル
CREATE TABLE IF NOT EXISTS daily_astrology (
  id         BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  date       DATE        NOT NULL,
  year       INT         NOT NULL,
  month      INT         NOT NULL,
  day        INT         NOT NULL,
  zodiac     VARCHAR(16) NOT NULL,
  star_number INT        NOT NULL,
  lunar_date VARCHAR(6)  NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_daily_astrology_date UNIQUE (date)
);
CREATE INDEX IF NOT EXISTS idx_daily_date ON daily_astrology (date);
CREATE INDEX IF NOT EXISTS idx_daily_ymd  ON daily_astrology (year, month, day);

-- 星のグループ管理テーブル（東四命、中三命、西二命）
CREATE TABLE IF NOT EXISTS star_groups (
  id           INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  star_number  INT         NOT NULL,
  group_id     INT         NOT NULL,
  name_jp      VARCHAR(50) NOT NULL,
  name_kanji   VARCHAR(50) NOT NULL,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_star_groups_star_number UNIQUE (star_number)
);

-- 九星盤の星配置テーブル
CREATE TABLE IF NOT EXISTS star_grid_patterns (
  id           INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  center_star  INT NOT NULL,
  north        INT NOT NULL,
  northeast    INT NOT NULL,
  east         INT NOT NULL,
  southeast    INT NOT NULL,
  south        INT NOT NULL,
  southwest    INT NOT NULL,
  west         INT NOT NULL,
  northwest    INT NOT NULL,
  season_start VARCHAR(50) DEFAULT NULL,
  season_end   VARCHAR(50) DEFAULT NULL,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_sgp_center_star UNIQUE (center_star),
  FOREIGN KEY (center_star)  REFERENCES stars (star_number) ON DELETE CASCADE,
  FOREIGN KEY (north)        REFERENCES stars (star_number) ON DELETE CASCADE,
  FOREIGN KEY (northeast)    REFERENCES stars (star_number) ON DELETE CASCADE,
  FOREIGN KEY (east)         REFERENCES stars (star_number) ON DELETE CASCADE,
  FOREIGN KEY (southeast)    REFERENCES stars (star_number) ON DELETE CASCADE,
  FOREIGN KEY (south)        REFERENCES stars (star_number) ON DELETE CASCADE,
  FOREIGN KEY (southwest)    REFERENCES stars (star_number) ON DELETE CASCADE,
  FOREIGN KEY (west)         REFERENCES stars (star_number) ON DELETE CASCADE,
  FOREIGN KEY (northwest)    REFERENCES stars (star_number) ON DELETE CASCADE
);

-- 月盤方位データテーブル
CREATE TABLE IF NOT EXISTS monthly_directions (
  id                 INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  group_id           INT         NOT NULL,
  month              INT         NOT NULL,
  zodiac             VARCHAR(10) DEFAULT NULL,
  center_star        INT         NOT NULL,
  north              INT         NOT NULL,
  northeast          INT         NOT NULL,
  east               INT         NOT NULL,
  southeast          INT         NOT NULL,
  south              INT         NOT NULL,
  southwest          INT         NOT NULL,
  west               INT         NOT NULL,
  northwest          INT         NOT NULL,
  north_fortune      VARCHAR(30) DEFAULT NULL,
  northeast_fortune  VARCHAR(30) DEFAULT NULL,
  east_fortune       VARCHAR(30) DEFAULT NULL,
  southeast_fortune  VARCHAR(30) DEFAULT NULL,
  south_fortune      VARCHAR(30) DEFAULT NULL,
  southwest_fortune  VARCHAR(30) DEFAULT NULL,
  west_fortune       VARCHAR(30) DEFAULT NULL,
  northwest_fortune  VARCHAR(30) DEFAULT NULL,
  season_start       VARCHAR(50) DEFAULT NULL,
  season_end         VARCHAR(50) DEFAULT NULL,
  description        TEXT        DEFAULT NULL,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at         TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_md_group_month UNIQUE (group_id, month),
  FOREIGN KEY (center_star) REFERENCES stars (star_number) ON DELETE CASCADE,
  FOREIGN KEY (north)       REFERENCES stars (star_number) ON DELETE CASCADE,
  FOREIGN KEY (northeast)   REFERENCES stars (star_number) ON DELETE CASCADE,
  FOREIGN KEY (east)        REFERENCES stars (star_number) ON DELETE CASCADE,
  FOREIGN KEY (southeast)   REFERENCES stars (star_number) ON DELETE CASCADE,
  FOREIGN KEY (south)       REFERENCES stars (star_number) ON DELETE CASCADE,
  FOREIGN KEY (southwest)   REFERENCES stars (star_number) ON DELETE CASCADE,
  FOREIGN KEY (west)        REFERENCES stars (star_number) ON DELETE CASCADE,
  FOREIGN KEY (northwest)   REFERENCES stars (star_number) ON DELETE CASCADE
);

-- 十二支グループマスタ
CREATE TABLE IF NOT EXISTS zodiac_groups (
  id         INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  group_name VARCHAR(20) NOT NULL,
  description VARCHAR(100) DEFAULT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_zodiac_groups_name UNIQUE (group_name)
);

-- 十二支 → グループID 対応
CREATE TABLE IF NOT EXISTS zodiac_group_members (
  zodiac     VARCHAR(2) PRIMARY KEY,
  group_id   INT         NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  FOREIGN KEY (group_id) REFERENCES zodiac_groups (id) ON DELETE CASCADE
);

-- 干支グループ × 九星中宮 → 時の十二支
CREATE TABLE IF NOT EXISTS hourly_star_zodiacs (
  id          INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  pattern_type VARCHAR(10) NOT NULL CHECK (pattern_type IN ('SP_ASC','SP_DESC')),
  group_id    INT         NOT NULL,
  center_star INT         NOT NULL,
  hour_zodiac VARCHAR(2)  NOT NULL,
  start_hour  INT         NOT NULL,
  end_hour    INT         NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  FOREIGN KEY (group_id) REFERENCES zodiac_groups (id) ON DELETE CASCADE
);

-- 九星の詳細属性テーブル
CREATE TABLE IF NOT EXISTS star_attributes (
  id              INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  star_number     INT          NOT NULL,
  attribute_type  VARCHAR(30)  NOT NULL,
  attribute_value VARCHAR(255) NOT NULL,
  description     VARCHAR(255) DEFAULT NULL,
  created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
  FOREIGN KEY (star_number) REFERENCES stars (star_number) ON DELETE CASCADE,
  CONSTRAINT uq_star_attribute UNIQUE (star_number, attribute_type, attribute_value)
);
CREATE INDEX IF NOT EXISTS idx_sa_star_type ON star_attributes (star_number, attribute_type);

-- システム設定テーブル
CREATE TABLE IF NOT EXISTS system_config (
  id          INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  key         VARCHAR(100) NOT NULL,
  value       TEXT,
  description VARCHAR(255),
  created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_system_config_key UNIQUE (key)
);

-- 管理者アカウント制限テーブル
CREATE TABLE IF NOT EXISTS admin_account_limit (
  id           INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  max_accounts INT         NOT NULL DEFAULT 10,
  created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 権限テーブル
CREATE TABLE IF NOT EXISTS permissions (
  id          INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name        VARCHAR(100) NOT NULL,
  description VARCHAR(255),
  category    VARCHAR(255) NULL,
  created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_permissions_name UNIQUE (name)
);

-- ユーザーテーブル
CREATE TABLE IF NOT EXISTS users (
  id                 INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  name               VARCHAR(100) NOT NULL,
  email              VARCHAR(120) NOT NULL,
  password           VARCHAR(200) NOT NULL,
  is_active          BOOLEAN      NOT NULL DEFAULT TRUE,
  is_admin           BOOLEAN      NOT NULL DEFAULT FALSE,
  is_superuser       BOOLEAN      NOT NULL DEFAULT FALSE,
  subscription_start TIMESTAMPTZ  NULL,
  subscription_end   TIMESTAMPTZ  NULL,
  account_limit      INT          NOT NULL DEFAULT 5,
  created_at         TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
  updated_at         TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
  created_by         INT          NULL,
  is_deleted         BOOLEAN      NOT NULL DEFAULT FALSE,
  deleted_at         TIMESTAMPTZ  NULL,
  deleted_by         INT          NULL,
  CONSTRAINT uq_users_email UNIQUE (email)
);

-- ユーザー権限テーブル
CREATE TABLE IF NOT EXISTS user_permissions (
  id            INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id       INT         NOT NULL,
  permission_id INT         NOT NULL,
  created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  FOREIGN KEY (user_id)       REFERENCES users (id)       ON DELETE CASCADE,
  FOREIGN KEY (permission_id) REFERENCES permissions (id) ON DELETE CASCADE,
  CONSTRAINT uq_user_permission UNIQUE (user_id, permission_id)
);

-- パワーストーンマスターテーブル
CREATE TABLE IF NOT EXISTS powerstone_master (
  id          INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  stone_id    VARCHAR(30)  NOT NULL,
  name_ja     VARCHAR(50)  NOT NULL,
  name_ko     VARCHAR(50)  NOT NULL,
  name_en     VARCHAR(50)  NOT NULL,
  gogyo       VARCHAR(5)   NOT NULL,
  is_primary  BOOLEAN      NOT NULL DEFAULT FALSE,
  image_url   VARCHAR(255) NULL,
  base_star   INT          NULL,
  created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
  updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
  CONSTRAINT uq_powerstone_stone_id UNIQUE (stone_id),
  CONSTRAINT uq_powerstone_base_star UNIQUE (base_star)
);
CREATE INDEX IF NOT EXISTS idx_pm_gogyo      ON powerstone_master (gogyo);
CREATE INDEX IF NOT EXISTS idx_pm_is_primary ON powerstone_master (is_primary);

-- 推薦履歴テーブル
CREATE TABLE IF NOT EXISTS recommendation_history (
  id                  INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  user_id             INT         NOT NULL,
  main_star           INT         NOT NULL,
  target_year         INT         NOT NULL,
  target_month        INT         NOT NULL,
  base_stone_id       VARCHAR(30) NOT NULL,
  monthly_stone_id    VARCHAR(30) NOT NULL,
  protection_stone_id VARCHAR(30) NOT NULL,
  locale              VARCHAR(5)  NOT NULL DEFAULT 'ja',
  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  FOREIGN KEY (user_id)             REFERENCES users (id)             ON DELETE CASCADE,
  FOREIGN KEY (base_stone_id)       REFERENCES powerstone_master (stone_id),
  FOREIGN KEY (monthly_stone_id)    REFERENCES powerstone_master (stone_id),
  FOREIGN KEY (protection_stone_id) REFERENCES powerstone_master (stone_id),
  CONSTRAINT uq_rh_user_period UNIQUE (user_id, target_year, target_month)
);
