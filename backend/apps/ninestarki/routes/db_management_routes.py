"""Database management routes blueprint for NineStarKi."""

from flask import Blueprint, request, jsonify
import json
import os
import glob
import re
from datetime import datetime
from flask_jwt_extended import jwt_required
from core.database import db
from core.utils.logger import get_logger
from core.auth.auth_utils import permission_required

logger = get_logger(__name__)

def create_db_management_bp():
    db_bp = Blueprint('db_management', __name__, url_prefix='/api/admin/db')

    @db_bp.route('/sql-files', methods=['GET'])
    @jwt_required()
    @permission_required('data_management')
    def get_sql_files():
        """MySQL初期化用SQLファイルの一覧を取得する"""
        try:
            # Docker環境でのSQLファイルパス（複数のパスを試す）
            sql_directories = [
                "/app/mysql/init",                      # Dockerコンテナ内の可能性のあるパス1
                "/mysql/init",                          # Dockerコンテナ内の可能性のあるパス2
                "/backend/mysql/init",                  # Dockerコンテナ内の可能性のあるパス3
                os.path.join(os.getcwd(), "mysql/init") # カレントディレクトリからの相対パス
            ]
            
            # ローカル開発環境でのSQLファイルパス
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            sql_directories.append(os.path.join(base_dir, "mysql", "init"))
            
            # 実際に存在するディレクトリを探す
            sql_directory = None
            for directory in sql_directories:
                logger.info(f"Checking SQL directory: {directory}")
                if os.path.exists(directory):
                    sql_directory = directory
                    logger.info(f"Found SQL directory: {directory}")
                    break
            
            if not sql_directory:
                # すべてのディレクトリが見つからない場合
                logger.error("SQL directory not found in any of the checked paths")
                return jsonify({
                    'error': 'SQLファイルディレクトリが見つかりません', 
                    'checked_paths': sql_directories
                }), 500
            
            # SQLファイル一覧を取得
            sql_files = glob.glob(os.path.join(sql_directory, "*.sql"))
            logger.info(f"Found {len(sql_files)} SQL files in {sql_directory}")
            
            # ファイル情報をリストに追加
            files_info = []
            for file_path in sql_files:
                file_name = os.path.basename(file_path)
                file_size = os.path.getsize(file_path)
                files_info.append({
                    'name': file_name,
                    'path': file_path,
                    'size': file_size
                })
            
            # 名前でソート
            files_info.sort(key=lambda x: x['name'])
            
            return jsonify(files_info), 200
            
        except Exception as e:
            logger.error(f"Error getting SQL files: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    @db_bp.route('/execute-sql', methods=['POST'])
    @jwt_required()
    @permission_required('data_management')
    def execute_sql_files():
        """SQLファイルを実行するAPI"""
        try:
            data = request.get_json()
            if not data or 'files' not in data:
                return jsonify({'error': 'No files specified'}), 400

            # SQLファイルディレクトリの候補を定義
            sql_directories = [
                "/app/mysql/init",                      # Dockerコンテナ内の可能性のあるパス1
                "/mysql/init",                          # Dockerコンテナ内の可能性のあるパス2
                "/backend/mysql/init",                  # Dockerコンテナ内の可能性のあるパス3
                os.path.join(os.getcwd(), "mysql/init") # カレントディレクトリからの相対パス
            ]
            
            # ローカル開発環境でのSQLファイルパス
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            sql_directories.append(os.path.join(base_dir, "mysql", "init"))

            results = []
            for file_path in data['files']:
                try:
                    # ファイル名を抽出
                    file_name = os.path.basename(file_path)
                    logger.info(f"処理対象のSQLファイル: {file_name}")

                    # 各ディレクトリでファイルを探す
                    actual_path = None
                    for directory in sql_directories:
                        test_path = os.path.join(directory, file_name)
                        logger.debug(f"SQLファイルパスを確認: {test_path}")
                        if os.path.exists(test_path):
                            actual_path = test_path
                            logger.info(f"SQLファイルが見つかりました: {actual_path}")
                            break

                    if not actual_path:
                        logger.error(f"ファイルが見つかりません: {file_name}")
                        logger.error(f"検索したパス: {sql_directories}")
                        results.append({
                            'file': file_path,
                            'success': False,
                            'message': 'ファイルが見つかりません'
                        })
                        continue

                    # SQLファイルを読み込む
                    with open(actual_path, 'r', encoding='utf-8') as f:
                        sql_content = f.read()
                        logger.debug(f"SQLファイルの内容:\n{sql_content}")

                    # SQLを文単位で分割して実行
                    connection = db.engine.raw_connection()
                    cursor = connection.cursor()
                    
                    try:
                        # SQL文を適切に分割
                        sql_statements = []
                        current_statement = []
                        
                        for line in sql_content.split('\n'):
                            # 空行をスキップ
                            if not line.strip():
                                continue
                            
                            # コメント行をスキップ
                            if line.strip().startswith('--'):
                                continue
                            
                            # 行を追加
                            current_statement.append(line)
                            
                            # セミコロンで終わる行を見つけたら文を完成させる
                            if line.strip().endswith(';'):
                                statement = '\n'.join(current_statement).strip()
                                if statement:
                                    sql_statements.append(statement)
                                current_statement = []
                        
                        # 最後の文が残っている場合も追加
                        if current_statement:
                            statement = '\n'.join(current_statement).strip()
                            if statement:
                                sql_statements.append(statement)
                        
                        logger.info(f"SQL文の数: {len(sql_statements)}")
                        
                        # 各SQL文を実行
                        affected_rows = 0
                        errors = []
                        
                        # 各SQL文に対して前処理を実行
                        processed_statements = []
                        for stmt in sql_statements:
                            # INSERTステートメントをREPLACE INTOに変換するか、DELETE→INSERTの2ステップに分割
                            insert_match = re.match(r'INSERT\s+INTO\s+`([^`]+)`', stmt, re.IGNORECASE)
                            
                            if insert_match:
                                table_name = insert_match.group(1)
                                logger.info(f"INSERT文の処理: テーブル '{table_name}'")
                                
                                # DELETEして再INSERTを選択
                                # コメントに特定のフラグがある場合、またはテーブル名が特定のパターンに一致する場合
                                if '-- DELETE_FIRST' in stmt.upper() or any(pattern in table_name for pattern in ['daily_star_readings', 'monthly_star_readings', 'star_attributes']):
                                    # DELETE文を作成
                                    # INSERT...VALUES構文からWHERE条件を抽出するケース
                                    values_match = re.search(r'VALUES\s*\(([^)]+)', stmt, re.IGNORECASE)
                                    columns_match = re.search(r'INSERT\s+INTO\s+`[^`]+`\s*\(([^)]+)\)', stmt, re.IGNORECASE)
                                    
                                    if values_match and columns_match:
                                        columns = [col.strip().strip('`') for col in columns_match.group(1).split(',')]
                                        values = [val.strip() for val in values_match.group(1).split(',')]
                                        
                                        # 主キーやユニークキーとなる可能性が高いカラムを特定
                                        key_columns = ['id', 'star_number', 'name', 'code']
                                        where_conditions = []
                                        
                                        for col, val in zip(columns, values):
                                            if col in key_columns:
                                                where_conditions.append(f"`{col}` = {val}")
                                        
                                        if where_conditions:
                                            delete_stmt = f"DELETE FROM `{table_name}` WHERE {' AND '.join(where_conditions)};"
                                            logger.info(f"生成されたDELETE文: {delete_stmt}")
                                            processed_statements.append(delete_stmt)
                                    
                                    processed_statements.append(stmt)
                                else:
                                    # REPLACE INTOに変換
                                    replace_stmt = stmt.replace('INSERT INTO', 'REPLACE INTO')
                                    logger.info(f"INSERTをREPLACEに変換しました")
                                    processed_statements.append(replace_stmt)
                            else:
                                # それ以外のSQL文はそのまま追加
                                processed_statements.append(stmt)
                        
                        # 処理済みのステートメントを実行
                        for i, stmt in enumerate(processed_statements, 1):
                            if stmt:
                                logger.info(f"SQL実行 ({i}/{len(processed_statements)}): {stmt[:100]}...")
                                try:
                                    cursor.execute(stmt)
                                    current_affected = cursor.rowcount
                                    affected_rows += current_affected
                                    logger.info(f"SQL実行成功 - 影響行数: {current_affected}")
                                except Exception as stmt_error:
                                    error_msg = str(stmt_error)
                                    # 重複エラーの場合は警告として記録（REPLACE INTOに変換しても発生する可能性がある）
                                    if "Duplicate entry" in error_msg:
                                        logger.warning(f"重複データをスキップ: {error_msg}")
                                        errors.append({
                                            'type': 'duplicate',
                                            'message': error_msg,
                                            'sql': stmt
                                        })
                                    else:
                                        # その他のエラーは失敗として記録
                                        logger.error(f"SQL実行エラー: {error_msg}")
                                        logger.error(f"エラーが発生したSQL: {stmt}")
                                        errors.append({
                                            'type': 'error',
                                            'message': error_msg,
                                            'sql': stmt
                                        })
                        
                        # エラーがない場合のみコミット
                        if not any(e['type'] == 'error' for e in errors):
                            connection.commit()
                            logger.info(f"コミット成功 - 合計影響行数: {affected_rows}")
                            
                            # 重複エラーがある場合は警告付きで成功
                            duplicate_count = sum(1 for e in errors if e['type'] == 'duplicate')
                            if duplicate_count > 0:
                                results.append({
                                    'file': file_path,
                                    'success': True,
                                    'warning': True,
                                    'message': f'SQL実行が完了しました（{duplicate_count}件の重複をスキップ）',
                                    'affectedRows': affected_rows,
                                    'duplicates': [e for e in errors if e['type'] == 'duplicate']
                                })
                            else:
                                results.append({
                                    'file': file_path,
                                    'success': True,
                                    'message': 'SQL実行が完了しました',
                                    'affectedRows': affected_rows
                                })
                        else:
                            # エラーがある場合はロールバック
                            connection.rollback()
                            logger.error(f"SQL実行エラーによりロールバック")
                            results.append({
                                'file': file_path,
                                'success': False,
                                'message': 'SQLの実行中にエラーが発生しました',
                                'errors': [e for e in errors if e['type'] == 'error']
                            })
                        
                    finally:
                        cursor.close()
                        connection.close()
                        logger.info("データベース接続をクローズしました")

                except Exception as e:
                    error_message = str(e)
                    results.append({
                        'file': file_path,
                        'success': False,
                        'message': f'エラー: {error_message}'
                    })
                    logger.error(f"SQLファイル実行エラー {file_path}: {error_message}")

            return jsonify({
                'message': 'SQL実行が完了しました',
                'results': results
            }), 200

        except Exception as e:
            logger.error(f"SQL実行処理全体でエラー: {str(e)}")
            return jsonify({'error': str(e)}), 500

    @db_bp.route('/tables', methods=['GET'])
    @jwt_required()
    @permission_required('data_management')
    def get_tables():
        """データベースのテーブル一覧を取得するAPI"""
        try:
            # 000_create_tables.sqlからテーブル定義を抽出
            tables = []
            tables_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "mysql", "init")
            create_tables_file = os.path.join(tables_dir, "000_create_tables.sql")
            
            if os.path.exists(create_tables_file):
                with open(create_tables_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # テーブル定義を抽出（CREATE TABLE文を検索）
                table_definitions = []
                pattern = r'CREATE TABLE IF NOT EXISTS\s+`([^`]+)`\s*\(([\s\S]*?)(?:\) ENGINE=|\);)'
                matches = re.findall(pattern, content)
                
                for table_name, definition in matches:
                    # テーブルの説明文を抽出（最初のコメント行）
                    table_comment_match = re.search(r'--\s*(.*?)\s*\n', content.split(f'CREATE TABLE IF NOT EXISTS `{table_name}`')[0].split('--')[-1])
                    table_comment = table_comment_match.group(1) if table_comment_match else ""
                    
                    table_definitions.append({
                        'name': table_name,
                        'comment': table_comment,
                        'definition': f'CREATE TABLE IF NOT EXISTS `{table_name}` ({definition}) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;'
                    })
                
                tables = sorted(table_definitions, key=lambda x: x['name'])
            
            return jsonify({
                'tables': tables
            }), 200
                
        except Exception as e:
            logger.error(f"Error getting table list: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    @db_bp.route('/tables/<table_name>/recreate', methods=['POST'])
    @jwt_required()
    @permission_required('data_management')
    def recreate_table(table_name):
        """テーブルを再作成するAPI（DROP & CREATE）"""
        try:
            # テーブル名のバリデーション
            if not re.match(r'^[a-zA-Z0-9_]+$', table_name):
                return jsonify({'error': 'Invalid table name'}), 400
            
            # 000_create_tables.sqlからテーブル定義を取得
            tables_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), "mysql", "init")
            create_tables_file = os.path.join(tables_dir, "000_create_tables.sql")
            
            if not os.path.exists(create_tables_file):
                return jsonify({'error': 'Table definition file not found'}), 404
            
            with open(create_tables_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 指定されたテーブルの定義を抽出
            pattern = f'CREATE TABLE IF NOT EXISTS `{table_name}`\\s*\\(([\\s\\S]*?)(?:\\) ENGINE=|\\);)'
            match = re.search(pattern, content)
            
            if not match:
                return jsonify({'error': f'Table definition for {table_name} not found'}), 404
            
            table_definition = f'CREATE TABLE IF NOT EXISTS `{table_name}` ({match.group(1)}) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;'
            
            # テーブルのDROP & CREATE実行
            connection = db.engine.raw_connection()
            cursor = connection.cursor()
            
            try:
                # トランザクション開始
                drop_query = f'DROP TABLE IF EXISTS `{table_name}`;'
                logger.info(f"Executing query: {drop_query}")
                cursor.execute(drop_query)
                
                logger.info(f"Executing query: {table_definition}")
                cursor.execute(table_definition)
                
                # コミット
                connection.commit()
                logger.info(f"Table {table_name} recreated successfully")
                
                return jsonify({
                    'message': f'テーブル {table_name} を再作成しました',
                    'table_name': table_name
                }), 200
                
            except Exception as e:
                # エラー時はロールバック
                connection.rollback()
                logger.error(f"Error recreating table {table_name}: {str(e)}")
                return jsonify({'error': str(e)}), 500
                
            finally:
                cursor.close()
                connection.close()
                
        except Exception as e:
            logger.error(f"Error processing table recreation: {str(e)}")
            return jsonify({'error': str(e)}), 500

    return db_bp 