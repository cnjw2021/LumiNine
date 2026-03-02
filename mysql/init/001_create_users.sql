-- テーブル作成後の権限設定
-- このスクリプトはDockerコンテナ初期化時にrootユーザーとして実行されます
-- NOTE: MYSQL_USER は docker-compose で指定した DB_USER に対応する

-- データベース操作権限 (MYSQL_USER に対してGRANT)
-- Docker MySQL 初期化ではMYSQL_USERが自動作成されるため、既に存在を前提とする
GRANT ALL PRIVILEGES ON ninestarki.* TO CURRENT_USER;

-- CSVロード用のFILE権限 (root用)
-- NOTE: FILE権限はグローバルレベルでのみ設定可能で、rootユーザーに対して設定
-- MYSQL_USERにはFILE権限を付与しない（権限エラーを防ぐ）

-- 権限変更を反映
FLUSH PRIVILEGES; 