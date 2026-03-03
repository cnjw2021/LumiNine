-- パワーストーンマスターテーブル
-- powerstone_catalog.json のデータを DB 管理に移行

CREATE TABLE IF NOT EXISTS `powerstone_master` (
  `id`          INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
  `stone_id`    VARCHAR(30)  NOT NULL COMMENT 'スートン識別子 (例: aquamarine, garnet)',
  `name_ja`     VARCHAR(50)  NOT NULL COMMENT '日本語名',
  `name_ko`     VARCHAR(50)  NOT NULL COMMENT '韓国語名',
  `name_en`     VARCHAR(50)  NOT NULL COMMENT '英語名',
  `gogyo`       VARCHAR(5)   NOT NULL COMMENT '五行 (水/木/火/土/金)',
  `is_primary`  BOOLEAN      NOT NULL DEFAULT FALSE COMMENT '主石フラグ (TRUE=主石, FALSE=副石)',
  `image_url`   VARCHAR(255) NULL COMMENT 'スートン画像URL',
  `base_star`   INT          NULL COMMENT '基本石の場合の本命星番号 (1~9)。NULL=基本石ではない',
  `created_at`  TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at`  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
  UNIQUE KEY `uq_stone_id` (`stone_id`) COMMENT 'ストーンIDの一意制約',
  INDEX `idx_gogyo` (`gogyo`),
  INDEX `idx_base_star` (`base_star`),
  INDEX `idx_is_primary` (`is_primary`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='パワーストーンマスター';
