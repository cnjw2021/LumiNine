-- システム設定の初期データ
INSERT INTO `system_config` (`key`, `value`, `description`, `created_at`, `updated_at`) VALUES
('site_name', '九星気学占い', 'サイト名', NOW(), NOW()),
('site_description', '九星気学に基づいた運勢占いサイト', 'サイトの説明', NOW(), NOW()),
('admin_email', 'admin@example.com', '管理者メールアドレス', NOW(), NOW()),
('max_daily_readings', '3', '1日あたりの最大占い回数', NOW(), NOW()),
('maintenance_mode', 'false', 'メンテナンスモード（true/false）', NOW(), NOW());

-- 管理者アカウント制限
INSERT INTO `admin_account_limit` (`max_accounts`, `created_at`, `updated_at`) VALUES (10, NOW(), NOW());

-- 権限の初期データ
INSERT INTO `permissions` (`name`, `description`, `category`, `created_at`, `updated_at`) VALUES
('user_read', 'ユーザー情報の閲覧', 'ユーザー管理', NOW(), NOW()),
('user_create', 'ユーザーの作成', 'ユーザー管理', NOW(), NOW()),
('user_update', 'ユーザー情報の更新', 'ユーザー管理', NOW(), NOW()),
('user_delete', 'ユーザーの削除', 'ユーザー管理', NOW(), NOW()),
('fortune_read', '運勢情報の閲覧', 'データ管理', NOW(), NOW()),
('fortune_create', '運勢情報の作成', 'データ管理', NOW(), NOW()),
('fortune_update', '運勢情報の更新', 'データ管理', NOW(), NOW()),
('fortune_delete', '運勢情報の削除', 'データ管理', NOW(), NOW()),
('system_config', 'システム設定の変更', 'システム管理', NOW(), NOW()),
('admin_access', '管理画面へのアクセス', 'システム管理', NOW(), NOW());
