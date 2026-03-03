-- パワーストーン シードデータ
-- powerstone_catalog.json からの移行データ (20件 + star_base_stones 9件)

INSERT INTO `powerstone_master` (`stone_id`, `name_ja`, `name_ko`, `name_en`, `gogyo`, `is_primary`, `base_star`) VALUES
-- 水 (Water)
('aquamarine',    'アクアマリン',       '아쿠아마린',      'Aquamarine',     '水', TRUE,  1),
('lapis_lazuli',  'ラピスラズリ',       '라피스 라줄리',   'Lapis Lazuli',   '水', FALSE, NULL),
('blue_topaz',    'ブルートパーズ',     '블루 토파즈',     'Blue Topaz',     '水', FALSE, NULL),
('onyx',          'オニキス',           '오닉스',          'Onyx',           '水', FALSE, NULL),

-- 木 (Wood)
('emerald',       'エメラルド',         '에메랄드',        'Emerald',        '木', TRUE,  3),
('peridot',       'ペリドット',         '페리도트',        'Peridot',        '木', FALSE, 4),
('aventurine',    'アベンチュリン',     '아벤츄린',        'Aventurine',     '木', FALSE, NULL),
('jade',          '翡翠',               '비취',            'Jade',           '木', FALSE, NULL),

-- 火 (Fire)
('garnet',        'ガーネット',         '가넷',            'Garnet',         '火', TRUE,  9),
('carnelian',     'カーネリアン',       '카넬리안',        'Carnelian',      '火', FALSE, NULL),
('ruby',          'ルビー',             '루비',            'Ruby',           '火', FALSE, NULL),
('amethyst',      'アメジスト',         '자수정',          'Amethyst',       '火', FALSE, NULL),

-- 土 (Earth)
('citrine',       'シトリン',           '시트린',          'Citrine',        '土', TRUE,  2),
('tigers_eye',    'タイガーアイ',       '타이거 아이',     'Tiger''s Eye',   '土', FALSE, 5),
('yellow_jasper', 'イエロージャスパー', '옐로 재스퍼',     'Yellow Jasper',  '土', FALSE, NULL),
('smoky_quartz',  'スモーキークォーツ', '스모키 쿼츠',     'Smoky Quartz',   '土', FALSE, 8),

-- 金 (Metal)
('clear_quartz',  '水晶',               '수정',            'Clear Quartz',   '金', TRUE,  6),
('moonstone',     'ムーンストーン',     '문스톤',          'Moonstone',      '金', FALSE, NULL),
('rose_quartz',   'ローズクォーツ',     '로즈 쿼츠',       'Rose Quartz',    '金', FALSE, 7),
('pearl',         'パール',             '진주',            'Pearl',          '金', FALSE, NULL);
