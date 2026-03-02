-- 陽遁・陰遁の開始日時情報を保存するテーブル
CREATE TABLE IF NOT EXISTS `stellar_cycles` (
  `id` INT AUTO_INCREMENT PRIMARY KEY COMMENT 'ID',
  `year` INT NOT NULL COMMENT '年',
  `first_ascending_phase_date` DATE NULL COMMENT '初回目陽遁開始日',
  `first_ascending_phase_time` TIME NULL COMMENT '初回目陽遁開始時刻',
  `first_descending_phase_date` DATE NOT NULL COMMENT '初回目陰遁開始日',
  `first_descending_phase_time` TIME NOT NULL DEFAULT '00:00:00' COMMENT '初回目陰遁開始時刻',
  `second_ascending_phase_date` DATE NULL COMMENT '二回目陽遁開始日',
  `second_ascending_phase_time` TIME NULL COMMENT '二回目陽遁開始時刻',
  `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '作成日時',
  `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新日時',
  UNIQUE KEY `year_unique` (`year`) COMMENT '年の一意制約'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='九星気学の周期情報';

INSERT INTO stellar_cycles 
(year, first_ascending_phase_date, first_ascending_phase_time, first_descending_phase_date, first_descending_phase_time, second_ascending_phase_date, second_ascending_phase_time, created_at, updated_at) 
VALUES 
(1967, NULL, NULL, '1967-06-29', '00:00:00', '1967-12-26', '00:00:00', NOW(), NOW()),
(1968, NULL, NULL, '1968-06-23', '00:00:00', '1968-12-20', '00:00:00', NOW(), NOW()),
(1969, NULL, NULL, '1969-06-18', '00:00:00', '1969-12-15', '00:00:00', NOW(), NOW()),
(1970, NULL, NULL, '1970-06-13', '00:00:00', '1970-12-10', '00:00:00', NOW(), NOW()),
(1971, NULL, NULL, '1971-06-08', '00:00:00', '1971-12-05', '00:00:00', NOW(), NOW()),
(1972, NULL, NULL, '1972-06-02', '00:00:00', '1972-11-29', '00:00:00', NOW(), NOW()),
(1973, NULL, NULL, '1973-05-28', '00:00:00', '1973-11-24', '00:00:00', NOW(), NOW()),
(1975, NULL, NULL, '1975-07-17', '00:00:00', NULL, NULL, NOW(), NOW()),
(1976, '1976-01-13', '00:00:00', '1976-07-11', '00:00:00', NULL, NULL, NOW(), NOW()),
(1977, '1977-01-07', '00:00:00', '1977-07-06', '00:00:00', NULL, NULL, NOW(), NOW()),
(1978, '1978-01-02', '00:00:00', '1978-07-01', '00:00:00', '1978-12-28', '00:00:00', NOW(), NOW()),
(1979, NULL, NULL, '1979-06-26', '00:00:00', '1979-12-23', '00:00:00', NOW(), NOW()),
(1980, NULL, NULL, '1980-06-20', '00:00:00', '1980-12-17', '00:00:00', NOW(), NOW()),
(1981, NULL, NULL, '1981-06-15', '00:00:00', '1981-12-12', '00:00:00', NOW(), NOW()),
(1982, NULL, NULL, '1982-06-10', '00:00:00', '1982-12-07', '00:00:00', NOW(), NOW()),
(1983, NULL, NULL, '1983-06-05', '00:00:00', '1983-12-02', '00:00:00', NOW(), NOW()),
(1984, NULL, NULL, '1984-05-30', '00:00:00', '1984-11-26', '00:00:00', NOW(), NOW())
;
