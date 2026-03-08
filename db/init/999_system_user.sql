-- システム管理者に全権限を付与 (PostgreSQL版)
-- バッククォート削除、MySQL固有文法なし

INSERT INTO user_permissions (user_id, permission_id, created_at, updated_at)
SELECT
  u.id,
  p.id,
  NOW(),
  NOW()
FROM
  users u,
  permissions p
WHERE
  u.email = 'superuser'
ON CONFLICT (user_id, permission_id) DO NOTHING;
