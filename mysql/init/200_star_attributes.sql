-- 九星の食べ物属性データ (Issue #93: 感情結果に推薦食品を表示)
-- 現時点では food タイプのみ使用。他の属性タイプ（color, shape 等）は今後の拡張時に追加予定。

-- -----------------------------------------------
-- 一白水星 (水)
-- -----------------------------------------------
INSERT INTO `star_attributes` (`star_number`, `attribute_type`, `attribute_value`, `description`, `created_at`, `updated_at`) VALUES
(1, 'food', '水分の多い食べ物・海産物', '一白水星に関連する食べ物', NOW(), NOW()),
(1, 'food', '豆腐・白い食べ物・塩分', '一白水星に関連する食べ物', NOW(), NOW())
ON DUPLICATE KEY UPDATE `attribute_value` = VALUES(`attribute_value`), `description` = VALUES(`description`), `updated_at` = NOW();

-- -----------------------------------------------
-- 二黒土星 (土)
-- -----------------------------------------------
INSERT INTO `star_attributes` (`star_number`, `attribute_type`, `attribute_value`, `description`, `created_at`, `updated_at`) VALUES
(2, 'food', '芋類・根菜・保存食品', '二黒土星に関連する食べ物', NOW(), NOW()),
(2, 'food', '重厚な味わいの料理・黒い食べ物', '二黒土星に関連する食べ物', NOW(), NOW())
ON DUPLICATE KEY UPDATE `attribute_value` = VALUES(`attribute_value`), `description` = VALUES(`description`), `updated_at` = NOW();

-- -----------------------------------------------
-- 三碧木星 (木)
-- -----------------------------------------------
INSERT INTO `star_attributes` (`star_number`, `attribute_type`, `attribute_value`, `description`, `created_at`, `updated_at`) VALUES
(3, 'food', '青菜・新芽・若葉', '三碧木星に関連する食べ物', NOW(), NOW()),
(3, 'food', '発酵食品・ハーブ・酸味のある食べ物', '三碧木星に関連する食べ物', NOW(), NOW())
ON DUPLICATE KEY UPDATE `attribute_value` = VALUES(`attribute_value`), `description` = VALUES(`description`), `updated_at` = NOW();

-- -----------------------------------------------
-- 四緑木星 (木)
-- -----------------------------------------------
INSERT INTO `star_attributes` (`star_number`, `attribute_type`, `attribute_value`, `description`, `created_at`, `updated_at`) VALUES
(4, 'food', '野菜・サラダ・緑の食べ物', '四緑木星に関連する食べ物', NOW(), NOW()),
(4, 'food', '種子・ナッツ・バランスの良い食事', '四緑木星に関連する食べ物', NOW(), NOW())
ON DUPLICATE KEY UPDATE `attribute_value` = VALUES(`attribute_value`), `description` = VALUES(`description`), `updated_at` = NOW();

-- -----------------------------------------------
-- 五黄土星 (土)
-- -----------------------------------------------
INSERT INTO `star_attributes` (`star_number`, `attribute_type`, `attribute_value`, `description`, `created_at`, `updated_at`) VALUES
(5, 'food', '穀物・米・パン・主食', '五黄土星に関連する食べ物', NOW(), NOW()),
(5, 'food', '黄色い食べ物・濃厚な食べ物', '五黄土星に関連する食べ物', NOW(), NOW())
ON DUPLICATE KEY UPDATE `attribute_value` = VALUES(`attribute_value`), `description` = VALUES(`description`), `updated_at` = NOW();

-- -----------------------------------------------
-- 六白金星 (金)
-- -----------------------------------------------
INSERT INTO `star_attributes` (`star_number`, `attribute_type`, `attribute_value`, `description`, `created_at`, `updated_at`) VALUES
(6, 'food', 'スイカ・メロン', '六白金星に関連する食べ物', NOW(), NOW()),
(6, 'food', 'カステラ・天ぷら', '六白金星に関連する食べ物', NOW(), NOW())
ON DUPLICATE KEY UPDATE `attribute_value` = VALUES(`attribute_value`), `description` = VALUES(`description`), `updated_at` = NOW();

-- -----------------------------------------------
-- 七赤金星 (金)
-- -----------------------------------------------
INSERT INTO `star_attributes` (`star_number`, `attribute_type`, `attribute_value`, `description`, `created_at`, `updated_at`) VALUES
(7, 'food', '赤い食べ物・スパイシーな料理', '七赤金星に関連する食べ物', NOW(), NOW()),
(7, 'food', '高級食材・豪華な料理・甘い食べ物', '七赤金星に関連する食べ物', NOW(), NOW())
ON DUPLICATE KEY UPDATE `attribute_value` = VALUES(`attribute_value`), `description` = VALUES(`description`), `updated_at` = NOW();

-- -----------------------------------------------
-- 八白土星 (土)
-- -----------------------------------------------
INSERT INTO `star_attributes` (`star_number`, `attribute_type`, `attribute_value`, `description`, `created_at`, `updated_at`) VALUES
(8, 'food', '白い食べ物・淡白な味わいの料理', '八白土星に関連する食べ物', NOW(), NOW()),
(8, 'food', '粉もの・乾燥食品・伝統的な料理', '八白土星に関連する食べ物', NOW(), NOW())
ON DUPLICATE KEY UPDATE `attribute_value` = VALUES(`attribute_value`), `description` = VALUES(`description`), `updated_at` = NOW();

-- -----------------------------------------------
-- 九紫火星 (火)
-- -----------------------------------------------
INSERT INTO `star_attributes` (`star_number`, `attribute_type`, `attribute_value`, `description`, `created_at`, `updated_at`) VALUES
(9, 'food', '辛い食べ物・赤い料理・燻製', '九紫火星に関連する食べ物', NOW(), NOW()),
(9, 'food', '油を使った料理・焼き料理・熱々の食べ物', '九紫火星に関連する食べ物', NOW(), NOW())
ON DUPLICATE KEY UPDATE `attribute_value` = VALUES(`attribute_value`), `description` = VALUES(`description`), `updated_at` = NOW();
