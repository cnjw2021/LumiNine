-- 九星気学データベーススキーマ

-- 九星の基本情報テーブル
CREATE TABLE IF NOT EXISTS `stars` (
  `star_number` INT AUTO_INCREMENT PRIMARY KEY COMMENT '1-9の九星番号',
  `name_jp` VARCHAR(50) NOT NULL COMMENT '日本語名称',
  `name_en` VARCHAR(50) NOT NULL COMMENT '英語名称',
  `element` VARCHAR(20) NOT NULL COMMENT '五行要素',
  `keywords` VARCHAR(255) NOT NULL COMMENT 'キーワード',
  `description` TEXT COMMENT '星の詳細説明',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 暦情報テーブル（節入り日など）
CREATE TABLE IF NOT EXISTS `solar_starts` (
  `year` INT PRIMARY KEY COMMENT '西暦年',
  `solar_starts_date` DATE NOT NULL COMMENT '立春日',
  `solar_starts_time` TIME NOT NULL COMMENT '立春時間',
  `zodiac` VARCHAR(10) NOT NULL COMMENT '干支',
  `star_number` INT NOT NULL COMMENT '九星番号',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時'
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci; 

CREATE TABLE IF NOT EXISTS `solar_terms` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
  `year` INT NOT NULL COMMENT '西暦年',
  `month` INT NOT NULL COMMENT '月（1-12）',
  `solar_terms_date` DATE NOT NULL COMMENT '節入り日',
  `solar_terms_time` TIME NOT NULL COMMENT '節入り時刻',
  `solar_terms_name` VARCHAR(20) NOT NULL COMMENT '節気名',
  `zodiac` VARCHAR(10) NOT NULL COMMENT '干支',
  `star_number` INT NOT NULL COMMENT '九星番号',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
  UNIQUE KEY `year_month` (`year`, `month`) COMMENT '年月の一意制約'
 ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci; 

 -- 日付ごとの干支と九星の情報を保存するテーブル
CREATE TABLE IF NOT EXISTS daily_astrology (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    date DATE NOT NULL COMMENT '日付',
    year INT NOT NULL COMMENT '年',
    month INT NOT NULL COMMENT '月',
    day INT NOT NULL COMMENT '日',
    zodiac VARCHAR(16) NOT NULL COMMENT '干支',
    star_number INT NOT NULL COMMENT '星盤',
    lunar_date VARCHAR(6) NULL COMMENT '旧暦',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
    UNIQUE KEY uk_date (date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='日付ごとの干支と九星の情報';

-- インデックスの作成
CREATE INDEX idx_date ON daily_astrology(date);
CREATE INDEX idx_year_month_day ON daily_astrology(year, month, day);

-- 詳細な属性データテーブル
CREATE TABLE IF NOT EXISTS `star_attributes` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
  `star_number` INT NOT NULL COMMENT '九星番号（1-9）',
  `attribute_type` VARCHAR(50) NOT NULL COMMENT '属性タイプ（color, shape, place等）',
  `attribute_value` VARCHAR(100) NOT NULL COMMENT '属性値',
  `description` TEXT COMMENT '説明',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
  FOREIGN KEY (`star_number`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE,
  UNIQUE KEY `star_attribute_value` (`star_number`, `attribute_type`, `attribute_value`) COMMENT '星・属性タイプ・属性値の一意制約'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 時の運気メッセージテーブル
CREATE TABLE IF NOT EXISTS `main_star_acquired_fortune_message` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
  `star_number` INT NOT NULL COMMENT '九星番号（1-9）',
  `luck_title` VARCHAR(100) NOT NULL COMMENT '吉運タイトル',
  `luck_details` TEXT NOT NULL COMMENT '吉運の詳細説明',
  `unluck_title` VARCHAR(100) NOT NULL COMMENT '凶運タイトル',
  `unluck_details` TEXT NOT NULL COMMENT '凶運の詳細説明',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
  FOREIGN KEY (`star_number`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE,
  UNIQUE KEY `unique_star_message` (`star_number`) COMMENT '星番号の一意制約'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 時の運気メッセージテーブル
CREATE TABLE IF NOT EXISTS `month_star_acquired_fortune_message` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
  `star_number` INT NOT NULL COMMENT '九星番号（1-9）',
  `luck_title` VARCHAR(100) NOT NULL COMMENT '吉運タイトル',
  `luck_details` TEXT NOT NULL COMMENT '吉運の詳細説明',
  `unluck_title` VARCHAR(100) NOT NULL COMMENT '凶運タイトル',
  `unluck_details` TEXT NOT NULL COMMENT '凶運の詳細説明',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
  FOREIGN KEY (`star_number`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE,
  UNIQUE KEY `unique_star_message` (`star_number`) COMMENT '星番号の一意制約'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 星と人生のガイダンス情報を格納するテーブル
CREATE TABLE IF NOT EXISTS `star_life_guidance` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `main_star` INT NOT NULL COMMENT '本命星',
  `month_star` INT NOT NULL COMMENT '月命星',
  `category` ENUM('job', 'lucky_color', 'lucky_item') NOT NULL COMMENT 'カテゴリ',
  `content` TEXT NOT NULL COMMENT '内容',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `idx_main_month_star_category` (`main_star`, `month_star`, `category`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 月命星の鑑定結果を保存するための専用テーブル
CREATE TABLE IF NOT EXISTS `monthly_star_readings` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
  `star_number` INT NOT NULL COMMENT '九星番号（1-9）',
  `title` VARCHAR(100) NOT NULL COMMENT '見出し（例：社会的な顔）',
  `keywords` TEXT COMMENT '特徴を表すキーワード',
  `description` TEXT NOT NULL COMMENT '詳細な鑑定内容',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
  FOREIGN KEY (`star_number`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE,
  UNIQUE KEY `unique_star` (`star_number`) COMMENT '星番号の一意制約'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 日命星の鑑定結果を保存するための専用テーブル
CREATE TABLE IF NOT EXISTS `daily_star_readings` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
  `star_number` INT NOT NULL COMMENT '九星番号（1-9）',
  `title` VARCHAR(100) NOT NULL COMMENT '見出し（例：内面的な性質）',
  `keywords` TEXT COMMENT '特徴を表すキーワード',
  `description` TEXT NOT NULL COMMENT '詳細な鑑定内容',
  `advice` TEXT COMMENT 'アドバイス',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
  FOREIGN KEY (`star_number`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE,
  UNIQUE KEY `unique_star` (`star_number`) COMMENT '星番号の一意制約'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 星のグループを管理するテーブル（東四命、中三命、西二命）
-- 方位などの判定に利用
CREATE TABLE IF NOT EXISTS `star_groups` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `star_number` INT NOT NULL, -- 星の番号（1〜9）
  `group_id` INT NOT NULL, -- グループID
  `name_jp` VARCHAR(50) NOT NULL, -- グループの日本語名（東四命、中三命、西二命）
  `name_kanji` VARCHAR(50) NOT NULL, -- 漢字表記（東四命、中三命、西二命）
  `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY `unique_star_number` (`star_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 九星盤の星配置テーブル
CREATE TABLE IF NOT EXISTS `star_grid_patterns` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
  `center_star` INT NOT NULL COMMENT '中央の星（1-9）',
  `north` INT NOT NULL COMMENT '北の星',
  `northeast` INT NOT NULL COMMENT '北東の星',
  `east` INT NOT NULL COMMENT '東の星',
  `southeast` INT NOT NULL COMMENT '南東の星',
  `south` INT NOT NULL COMMENT '南の星',
  `southwest` INT NOT NULL COMMENT '南西の星',
  `west` INT NOT NULL COMMENT '西の星',
  `northwest` INT NOT NULL COMMENT '北西の星',
  `season_start` VARCHAR(50) DEFAULT NULL COMMENT '季節の始まり（例：立春、立夏）',
  `season_end` VARCHAR(50) DEFAULT NULL COMMENT '季節の終わり（例：雨水、小満）',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
  UNIQUE KEY `center_star` (`center_star`) COMMENT '中央の星の一意制約',
  FOREIGN KEY (`center_star`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE,
  FOREIGN KEY (`north`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE,
  FOREIGN KEY (`northeast`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE,
  FOREIGN KEY (`east`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE,
  FOREIGN KEY (`southeast`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE,
  FOREIGN KEY (`south`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE,
  FOREIGN KEY (`southwest`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE,
  FOREIGN KEY (`west`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE,
  FOREIGN KEY (`northwest`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 九星間の相性マトリックス
CREATE TABLE IF NOT EXISTS `star_compatibility_matrix` (
  `base_star` INT PRIMARY KEY COMMENT '基準となる星（1-9）',
  `star_1` ENUM('BEST', 'BETTER', 'GOOD', 'BAD') NOT NULL COMMENT '一白水星との相性（BEST: 大吉, BETTER: 中吉, GOOD: 小吉, BAD: 凶）',
  `star_2` ENUM('BEST', 'BETTER', 'GOOD', 'BAD') NOT NULL COMMENT '二黒土星との相性',
  `star_3` ENUM('BEST', 'BETTER', 'GOOD', 'BAD') NOT NULL COMMENT '三碧木星との相性',
  `star_4` ENUM('BEST', 'BETTER', 'GOOD', 'BAD') NOT NULL COMMENT '四緑木星との相性',
  `star_5` ENUM('BEST', 'BETTER', 'GOOD', 'BAD') NOT NULL COMMENT '五黄土星との相性',
  `star_6` ENUM('BEST', 'BETTER', 'GOOD', 'BAD') NOT NULL COMMENT '六白金星との相性',
  `star_7` ENUM('BEST', 'BETTER', 'GOOD', 'BAD') NOT NULL COMMENT '七赤金星との相性',
  `star_8` ENUM('BEST', 'BETTER', 'GOOD', 'BAD') NOT NULL COMMENT '八白土星との相性',
  `star_9` ENUM('BEST', 'BETTER', 'GOOD', 'BAD') NOT NULL COMMENT '九紫火星との相性',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
  FOREIGN KEY (`base_star`) REFERENCES `stars` (`star_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 月盤方位データテーブル
CREATE TABLE IF NOT EXISTS `monthly_directions` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
  `group_id` INT NOT NULL COMMENT '本命星グループID（1-3）',
  `month` INT NOT NULL COMMENT '月（1-12）',
  `zodiac` VARCHAR(10) COMMENT '干支（子、丑、寅...）',
  `center_star` INT NOT NULL COMMENT '中央の星（1-9）',
  `north` INT NOT NULL COMMENT '北の星',
  `northeast` INT NOT NULL COMMENT '北東の星',
  `east` INT NOT NULL COMMENT '東の星',
  `southeast` INT NOT NULL COMMENT '南東の星',
  `south` INT NOT NULL COMMENT '南の星',
  `southwest` INT NOT NULL COMMENT '南西の星',
  `west` INT NOT NULL COMMENT '西の星',
  `northwest` INT NOT NULL COMMENT '北西の星',
  `north_fortune` VARCHAR(30) DEFAULT NULL COMMENT '北の吉凶',
  `northeast_fortune` VARCHAR(30) DEFAULT NULL COMMENT '北東の吉凶',
  `east_fortune` VARCHAR(30) DEFAULT NULL COMMENT '東の吉凶',
  `southeast_fortune` VARCHAR(30) DEFAULT NULL COMMENT '南東の吉凶',
  `south_fortune` VARCHAR(30) DEFAULT NULL COMMENT '南の吉凶',
  `southwest_fortune` VARCHAR(30) DEFAULT NULL COMMENT '南西の吉凶',
  `west_fortune` VARCHAR(30) DEFAULT NULL COMMENT '西の吉凶',
  `northwest_fortune` VARCHAR(30) DEFAULT NULL COMMENT '北西の吉凶',
  `season_start` VARCHAR(50) DEFAULT NULL COMMENT '季節の始まり（例：立春、立夏）',
  `season_end` VARCHAR(50) DEFAULT NULL COMMENT '季節の終わり（例：雨水、小満）',
  `description` TEXT DEFAULT NULL COMMENT '追加説明',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
  UNIQUE KEY `group_month` (`group_id`,`month`) COMMENT 'グループIDと月の一意制約',
  FOREIGN KEY (`center_star`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE,
  FOREIGN KEY (`north`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE,
  FOREIGN KEY (`northeast`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE,
  FOREIGN KEY (`east`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE,
  FOREIGN KEY (`southeast`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE,
  FOREIGN KEY (`south`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE,
  FOREIGN KEY (`southwest`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE,
  FOREIGN KEY (`west`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE,
  FOREIGN KEY (`northwest`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 引っ越し吉日テーブル
CREATE TABLE IF NOT EXISTS `moving_auspicious_dates` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
  `year` INT NOT NULL COMMENT '対象年度',
  `main_star` INT NOT NULL COMMENT '本命星',
  `month_star` INT NOT NULL COMMENT '月命星',
  `date` DATE NOT NULL COMMENT '引っ越し吉日',
  `description` TEXT NULL COMMENT '備考・説明',
  `direction` VARCHAR(50) NULL COMMENT '方位（例: 南東、北西）',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
  UNIQUE KEY `unique_year_main_star` (`year`, `main_star`, `month_star`, `date`),
  FOREIGN KEY (`main_star`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE,
  FOREIGN KEY (`month_star`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE,
  INDEX `idx_year` (`year`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='引っ越し吉日情報';


-- 相性マスターテーブル
CREATE TABLE IF NOT EXISTS `compatibility_master` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
  `main_star` INT NOT NULL COMMENT '主星 (判断する側の本命星) 番号',
  `main_birth_month` INT NULL COMMENT '主星の持ち主の生まれ月 (NULL の場合は月に関係なく適用)',
  `target_star` INT NOT NULL COMMENT '対象星 (相手の本命星) 番号',
  `target_birth_month` INT NULL COMMENT '対象星の持ち主の生まれ月 (NULL の場合は月に関係なく適用)',
  `symbols_male` VARCHAR(10) NOT NULL COMMENT '男性の相性記号 (★,○,P,F,N,▲ など)',
  `symbols_female` VARCHAR(10) NOT NULL COMMENT '女性の相性記号 (★,○,P,F,N,▲ など)',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
  UNIQUE KEY `unique_compatibility` (`main_star`, `main_birth_month`, `target_star`, `target_birth_month`, `symbols_male`, `symbols_female`) COMMENT '相性データの一意制約',
  FOREIGN KEY (`main_star`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE,
  FOREIGN KEY (`target_star`) REFERENCES `stars` (`star_number`) ON DELETE CASCADE,
  INDEX `idx_main_star` (`main_star`),
  INDEX `idx_main_birth_month` (`main_birth_month`),
  INDEX `idx_target_star` (`target_star`),
  INDEX `idx_target_birth_month` (`target_birth_month`),
  INDEX `idx_symbols_male` (`symbols_male`),
  INDEX `idx_symbols_female` (`symbols_female`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='相性マスター';

-- 相性記号パターンマスターテーブル
CREATE TABLE IF NOT EXISTS `compatibility_symbol_pattern_master` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
  `symbols` VARCHAR(10) NOT NULL COMMENT '相性記号 (★,○,P,F,N,▲ など)',
  `pattern_code` VARCHAR(30) NOT NULL COMMENT 'パターンコード',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
  UNIQUE KEY `unique_pattern_code` (`pattern_code`) COMMENT 'パターンコードの一意制約',
  UNIQUE KEY `unique_symbols` (`symbols`) COMMENT '記号の一意制約'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='相性記号パターンマスター';

-- 相性記号マスター
CREATE TABLE IF NOT EXISTS `compatibility_symbol_master` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
  `symbol` VARCHAR(10) NOT NULL COMMENT '相性記号 (★,○,P,F,N,▲,◆ など)',
  `meaning` VARCHAR(50) NOT NULL COMMENT '記号の意味（最高・良好・ビジネスなど）',
  `description` TEXT COMMENT '説明',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
  UNIQUE KEY `unique_symbol` (`symbol`) COMMENT '記号の一意制約'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='相性記号マスター';

-- 相性鑑定文テーブル
CREATE TABLE IF NOT EXISTS `compatibility_readings_master` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
  `pattern_code` VARCHAR(30) NOT NULL COMMENT 'パターンコード',
  `theme` VARCHAR(30) NOT NULL COMMENT 'テーマ',
  `title` VARCHAR(100) NOT NULL COMMENT '鑑定タイトル',
  `content` TEXT NOT NULL COMMENT '鑑定内容',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
  UNIQUE KEY `unique_reading` (`pattern_code`, `theme`) COMMENT '鑑定文の一意制約',
  FOREIGN KEY (`pattern_code`) REFERENCES `compatibility_symbol_pattern_master` (`pattern_code`) ON DELETE CASCADE,
  INDEX `idx_pattern_code` (`pattern_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='相性鑑定文マスター';

-- 十二支グループマスタ
CREATE TABLE IF NOT EXISTS `zodiac_groups` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'グループID',
  `group_name` VARCHAR(20) NOT NULL UNIQUE COMMENT 'グループ名（例: 子午卯酉）',
  `description` VARCHAR(100) DEFAULT NULL COMMENT '説明',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='十二支グループマスタ';

-- 十二支 → グループID 対応
CREATE TABLE IF NOT EXISTS `zodiac_group_members` (
  `zodiac` VARCHAR(2) PRIMARY KEY COMMENT '十二支（子丑寅…）',
  `group_id` INT NOT NULL COMMENT 'グループID',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
  FOREIGN KEY (`group_id`) REFERENCES `zodiac_groups` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='十二支とグループの対応テーブル';

-- 干支グループ × 九星中宮 → 時の十二支
CREATE TABLE IF NOT EXISTS `hourly_star_zodiacs` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
  `pattern_type` ENUM('SP_ASC','SP_DESC') NOT NULL COMMENT '陽遁=SP_ASC, 隠遁=SP_DESC',
  `group_id` INT NOT NULL COMMENT '十二支グループID',
  `center_star` INT NOT NULL COMMENT '中宮の九星 (1-9)',
  `hour_zodiac` VARCHAR(2) NOT NULL COMMENT '時の十二支',
  `start_hour` INT NOT NULL COMMENT '開始時間（0-23）',
  `end_hour` INT NOT NULL COMMENT '終了時間（0-23）',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
  FOREIGN KEY (`group_id`) REFERENCES `zodiac_groups` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='時盤(干支グループ×九星→時十二支) マスタ'; 

-- システム設定テーブル
CREATE TABLE IF NOT EXISTS `system_config` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
  `key` VARCHAR(100) NOT NULL COMMENT '設定キー',
  `value` TEXT COMMENT '設定値',
  `description` VARCHAR(255) COMMENT '説明',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
  UNIQUE KEY `unique_key` (`key`) COMMENT 'キーの一意制約'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 管理者アカウント制限テーブル
CREATE TABLE IF NOT EXISTS `admin_account_limit` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
  `max_accounts` INT NOT NULL DEFAULT 10 COMMENT '最大アカウント数',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 権限テーブル
CREATE TABLE IF NOT EXISTS `permissions` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
  `name` VARCHAR(100) NOT NULL COMMENT '権限名',
  `description` VARCHAR(255) COMMENT '説明',
  `category` VARCHAR(255) NULL COMMENT '権限カテゴリ',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
  UNIQUE KEY `unique_name` (`name`) COMMENT '権限名の一意制約'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ユーザーテーブル
CREATE TABLE IF NOT EXISTS `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
  `name` VARCHAR(100) NOT NULL COMMENT 'ユーザー名',
  `email` VARCHAR(120) NOT NULL COMMENT 'メールアドレス',
  `password` VARCHAR(200) NOT NULL COMMENT 'パスワード',
  `is_active` BOOLEAN NOT NULL DEFAULT TRUE COMMENT 'アクティブ状態',
  `is_admin` BOOLEAN NOT NULL DEFAULT FALSE COMMENT '管理者フラグ',
  `is_superuser` BOOLEAN NOT NULL DEFAULT FALSE COMMENT 'スーパーユーザーフラグ',
  `subscription_start` TIMESTAMP NULL COMMENT 'サブスクリプション開始日',
  `subscription_end` TIMESTAMP NULL COMMENT 'サブスクリプション終了日',
  `account_limit` INT NOT NULL DEFAULT 5 COMMENT 'ユーザーが作成できるアカウント数の上限（0は無制限）',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
  `created_by` INT NULL COMMENT '作成者ID',
  `is_deleted` BOOLEAN NOT NULL DEFAULT FALSE COMMENT '削除フラグ',
  `deleted_at` TIMESTAMP NULL COMMENT '削除日時',
  `deleted_by` INT NULL COMMENT '削除者ID',
  UNIQUE KEY `unique_email` (`email`) COMMENT 'メールアドレスの一意制約'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ユーザー権限テーブル
CREATE TABLE IF NOT EXISTS `user_permissions` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
  `user_id` INT NOT NULL COMMENT 'ユーザーID',
  `permission_id` INT NOT NULL COMMENT '権限ID',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE CASCADE,
  UNIQUE KEY `user_permission` (`user_id`, `permission_id`) COMMENT 'ユーザーと権限の組み合わせの一意制約'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;