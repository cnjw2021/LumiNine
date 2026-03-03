-- 推薦履歴テーブル
-- ユーザー別パワーストーン推薦結果を記録

CREATE TABLE IF NOT EXISTS `recommendation_history` (
  `id`                  INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
  `user_id`             INT          NOT NULL COMMENT 'ユーザーID',
  `main_star`           INT          NOT NULL COMMENT '本命星 (1~9)',
  `target_year`         INT          NOT NULL COMMENT '対象年度',
  `target_month`        INT          NOT NULL COMMENT '対象節月インデックス (1~12)',
  `base_stone_id`       VARCHAR(30)  NOT NULL COMMENT '基本石ストーンID',
  `monthly_stone_id`    VARCHAR(30)  NOT NULL COMMENT '月運石ストーンID',
  `protection_stone_id` VARCHAR(30)  NOT NULL COMMENT '護身石ストーンID',
  `locale`              VARCHAR(5)   NOT NULL DEFAULT 'ja' COMMENT '応答ロケール',
  `created_at`          TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  FOREIGN KEY (`base_stone_id`) REFERENCES `powerstone_master` (`stone_id`),
  FOREIGN KEY (`monthly_stone_id`) REFERENCES `powerstone_master` (`stone_id`),
  FOREIGN KEY (`protection_stone_id`) REFERENCES `powerstone_master` (`stone_id`),
  UNIQUE KEY `uq_user_period` (`user_id`, `target_year`, `target_month`) COMMENT 'ユーザー×年月の一意制約'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='パワーストーン推薦履歴';
