-- 月盤方位データの初期データ
-- 各グループの各月の方位データを設定
-- group_idは星グループID（1-3）を表し、monthは1-12の月を表す
-- 注意: 九星気学では北と南、東と西が地図上の方位と逆になります

-- グループ1（一白水星、四緑木星、七赤金星）の月盤データ
INSERT INTO `monthly_directions` (`group_id`, `month`, `zodiac`, `center_star`, `north`, `northeast`, `east`, `southeast`, `south`, `southwest`, `west`, `northwest`, `north_fortune`, `northeast_fortune`, `east_fortune`, `southeast_fortune`, `south_fortune`, `southwest_fortune`, `west_fortune`, `northwest_fortune`, `season_start`, `season_end`, `created_at`, `updated_at`) 
VALUES 
-- 添付図に基づき、九星気学の方位を考慮して配置
(1, 1, '丑', 6, 2, 9, 4, 5, 1, 3, 8, 7, null, null, null, null, null, '破', null, 'ア', '小寒', '大寒', NOW(), NOW()),  -- 1月（丑）
(1, 2, '寅', 8, 4, 2, 6, 7, 3, 5, 1, 9, null, 'ア', null, null, null, '破', null, null, '立春', '雨水', NOW(), NOW()),  -- 2月（寅）
(1, 3, '卯', 7, 3, 1, 5, 6, 2, 4, 9, 8, null, null, null, null, null, null, 'ア', null, '啓蟄', '春分', NOW(), NOW()),  -- 3月（卯）
(1, 4, '辰', 6, 2, 9, 4, 5, 1, 3, 8, 7, null, null, null, null, null, null, null, 'ア', '清明', '穀雨', NOW(), NOW()),  -- 4月（辰）
(1, 5, '巳', 5, 1, 8, 3, 4, 9, 2, 7, 6, null, null, null, null, null, null, null, '破', '立夏', '小満', NOW(), NOW()),  -- 5月（巳）
(1, 6, '午', 4, 9, 7, 2, 3, 8, 1, 6, 5, '破', null, null, null, null, null, null, null, '芒種', '夏至', NOW(), NOW()),  -- 6月（午）
(1, 7, '未', 3, 8, 6, 1, 2, 7, 9, 5, 4, null, '破', 'ア', null, null, null, null, null, '小暑', '大暑', NOW(), NOW()),  -- 7月（未）
(1, 8, '申', 2, 7, 5, 9, 1, 6, 8, 4, 3, null, '破', null, null, null, 'ア', null, null, '立秋', '処暑', NOW(), NOW()),  -- 8月（申）
(1, 9, '酉', 1, 6, 4, 8, 9, 5, 7, 3, 2, 'ア', null, '破', null, null, null, null, null, '白露', '秋分', NOW(), NOW()),  -- 9月（酉）
(1, 10, '戌', 9, 5, 3, 7, 8, 4, 6, 2, 1, null, null, null, '破', 'ア', null, null, null, '寒露', '霜降', NOW(), NOW()), -- 10月（戌）
(1, 11, '亥', 8, 4, 2, 6, 7, 3, 5, 1, 9, null, 'ア', null, '破', null, null, null, 'ア', '立冬', '小雪', NOW(), NOW()), -- 11月（亥）
(1, 12, '子', 7, 3, 1, 5, 6, 2, 4, 9, 8, null, null, null, null, '破', null, 'ア', null, '大雪', '冬至', NOW(), NOW()); -- 12月（子）

-- グループ2（二黒土星、五黄土星、八白土星）の月盤データ
INSERT INTO `monthly_directions` (`group_id`, `month`, `zodiac`, `center_star`, `north`, `northeast`, `east`, `southeast`, `south`, `southwest`, `west`, `northwest`, `north_fortune`, `northeast_fortune`, `east_fortune`, `southeast_fortune`, `south_fortune`, `southwest_fortune`, `west_fortune`, `northwest_fortune`, `season_start`, `season_end`, `created_at`, `updated_at`) 
VALUES 
(2, 1, '丑', 9, 5, 3, 7, 8, 4, 6, 2, 1, null, null, null, null, 'ア', '破', null, null, '小寒', '大寒', NOW(), NOW()),  -- 1月（丑）
(2, 2, '寅', 2, 7, 5, 9, 1, 6, 8, 4, 3, null, null, null, null, null, 'ア', null, null, '立春', '雨水', NOW(), NOW()),  -- 2月（寅）
(2, 3, '卯', 1, 6, 4, 8, 9, 5, 7, 3, 2, 'ア', null, null, null, null, null, '破', null, '啓蟄', '春分', NOW(), NOW()),  -- 3月（卯）
(2, 4, '辰', 9, 5, 3, 7, 8, 4, 6, 2, 1, null, null, null, null, 'ア', null, null, '破', '清明', '穀雨', NOW(), NOW()),  -- 4月（辰）
(2, 5, '巳', 8, 4, 2, 6, 7, 3, 5, 1, 9, null, 'ア', null, null, null, null, null, '破', '立夏', '小満', NOW(), NOW()),  -- 5月（巳）
(2, 6, '午', 7, 3, 1, 5, 6, 2, 4, 9, 8, '破', null, null, null, null, null, 'ア', null, '芒種', '夏至', NOW(), NOW()),  -- 6月（午）
(2, 7, '未', 6, 2, 9, 4, 5, 1, 3, 8, 7, null, '破', null, null, null, null, null, 'ア', '小暑', '大暑', NOW(), NOW()),  -- 7月（未）
(2, 8, '申', 5, 1, 8, 3, 4, 9, 2, 7, 6, null, '破', null, null, null, null, null, null, '立秋', '処暑', NOW(), NOW()),  -- 8月（申）
(2, 9, '酉', 4, 9, 7, 2, 3, 8, 1, 6, 5, null, null, '破', 'ア', null, null, null, null, '白露', '秋分', NOW(), NOW()),  -- 9月（酉）
(2, 10, '戌', 3, 8, 6, 1, 2, 7, 9, 5, 4, null, null, 'ア', '破', null, null, null, null, '寒露', '霜降', NOW(), NOW()), -- 10月（戌）
(2, 11, '亥', 2, 7, 5, 9, 1, 6, 8, 4, 3, null, null, null, '破', null, 'ア', null, null, '立冬', '小雪', NOW(), NOW()), -- 11月（亥）
(2, 12, '子', 1, 6, 4, 8, 9, 5, 7, 3, 2, 'ア', null, null, null, '破', null, null, null, '大雪', '冬至', NOW(), NOW()); -- 12月（子）

-- グループ3（三碧木星、六白金星、九紫火星）の月盤データ
INSERT INTO `monthly_directions` (`group_id`, `month`, `zodiac`, `center_star`, `north`, `northeast`, `east`, `southeast`, `south`, `southwest`, `west`, `northwest`, `north_fortune`, `northeast_fortune`, `east_fortune`, `southeast_fortune`, `south_fortune`, `southwest_fortune`, `west_fortune`, `northwest_fortune`, `season_start`, `season_end`, `created_at`, `updated_at`) 
VALUES 
(3, 1, '丑', 3, 8, 6, 1, 2, 7, 9, 5, 4, null, null, 'ア', null, null, '破', null, null, '小寒', '大寒', NOW(), NOW()),  -- 1月（丑）
(3, 2, '寅', 5, 1, 8, 3, 4, 9, 2, 7, 6, null, null, null, null, null, '破', null, null, '立春', '雨水', NOW(), NOW()),  -- 2月（寅）
(3, 3, '卯', 4, 9, 7, 2, 3, 8, 1, 6, 5, null, null, null, 'ア', null, null, '破', null, '啓蟄', '春分', NOW(), NOW()),  -- 3月（卯）
(3, 4, '辰', 3, 8, 6, 1, 2, 7, 9, 5, 4, null, null, 'ア', null, null, null, null, '破', '清明', '穀雨', NOW(), NOW()),  -- 4月（辰）
(3, 5, '巳', 2, 7, 5, 9, 1, 6, 8, 4, 3, null, null, null, null, null, 'ア', null, '破', '立夏', '小満', NOW(), NOW()),  -- 5月（巳）
(3, 6, '午', 1, 6, 4, 8, 9, 5, 7, 3, 2, 'ア・破', null, null, null, null, null, null, null, '芒種', '夏至', NOW(), NOW()),  -- 6月（午）
(3, 7, '未', 9, 5, 3, 7, 8, 4, 6, 2, 1, null, '破', null, null, 'ア', null, null, null, '小暑', '大暑', NOW(), NOW()),  -- 7月（未）
(3, 8, '申', 8, 4, 2, 6, 7, 3, 5, 1, 9, null, '破・ア', null, null, null, null, null, null, '立秋', '処暑', NOW(), NOW()),  -- 8月（申）
(3, 9, '酉', 7, 3, 1, 5, 6, 2, 4, 9, 8, null, null, '破', null, null, null, 'ア', null, '白露', '秋分', NOW(), NOW()),  -- 9月（酉）
(3, 10, '戌', 6, 2, 9, 4, 5, 1, 3, 8, 7, null, null, null, '破', null, null, null, 'ア', '寒露', '霜降', NOW(), NOW()), -- 10月（戌）
(3, 11, '亥', 5, 1, 8, 3, 4, 9, 2, 7, 6, null, null, null, '破', null, null, null, null, '立冬', '小雪', NOW(), NOW()), -- 11月（亥）
(3, 12, '子', 4, 9, 7, 2, 3, 8, 1, 6, 5, null, null, null, 'ア', '破', null, null, null, '大雪', '冬至', NOW(), NOW()); -- 12月（子）
