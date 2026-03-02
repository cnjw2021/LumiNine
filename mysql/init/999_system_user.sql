-- システム管理者に全権限を付与
-- 条件付きでユーザーに権限を付与（ユーザーが存在する場合のみ）
INSERT INTO `user_permissions` (`user_id`, `permission_id`, `created_at`, `updated_at`)
SELECT 
  u.id, 
  p.id, 
  NOW(), 
  NOW()
FROM 
  users u, 
  permissions p
WHERE 
  u.email = 'superuser'; 