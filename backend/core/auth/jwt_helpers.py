"""
JWT関連のヘルパー機能を提供するモジュール
"""

# JWTトークンのブラックリストを保持するセット
jwt_blocklist = set()

def add_token_to_blocklist(jti):
    """
    トークンをブラックリストに追加する
    
    Args:
        jti (str): JWTトークンの一意識別子
    """
    jwt_blocklist.add(jti)

def is_token_in_blocklist(jti):
    """
    トークンがブラックリストに含まれているか確認する
    
    Args:
        jti (str): JWTトークンの一意識別子
        
    Returns:
        bool: ブラックリストに含まれている場合はTrue
    """
    return jti in jwt_blocklist 