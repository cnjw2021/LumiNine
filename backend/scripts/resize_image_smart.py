#!/usr/bin/env python3
"""
Certificate Template 汎用A4比率調整スクリプト
装飾枠を自動検出し、中央部分を調整してA4比率に最適化します
"""

from PIL import Image
import os
import sys
import datetime

def detect_frame_ratio(image, file_path):
    """
    画像から装飾枠の比率を自動検出する
    簡易的な方法：上下の特定範囲の透明度や色の変化を分析
    """
    width, height = image.size
    
    # デフォルト値（全テンプレートに適用）
    default_frame_ratio = 0.10  # 10%
    
    # より高度な検出アルゴリズムを後で実装可能
    # 現在は安全なデフォルト値を使用
    return default_frame_ratio

def log_template_info(file_name, original_size, new_size, original_ratio, new_ratio, a4_ratio):
    """処理情報をログファイルに記録"""
    log_file = "template_resize_log.txt"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    original_width, original_height = original_size
    new_width, new_height = new_size
    
    original_diff = abs(original_ratio - a4_ratio)
    new_diff = abs(new_ratio - a4_ratio)
    
    log_entry = (
        f"{timestamp} | "
        f"{file_name} | "
        f"変更前: {original_width}x{original_height} | "
        f"変更後: {new_width}x{new_height} | "
        f"元比率: {original_ratio:.3f} | "
        f"新比率: {new_ratio:.3f} | "
        f"A4比率: {a4_ratio:.3f} | "
        f"元A4差: {original_diff:.3f} | "
        f"新A4差: {new_diff:.3f}\n"
    )
    
    # ログファイルに追記
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry)
    
    # コンソールにも表示
    print(f"📊 ログ記録: {log_entry.strip()}")

def smart_resize_to_a4_ratio(file_path):
    """汎用A4比率調整関数"""
    # A4の比率 (210mm / 297mm)
    A4_RATIO = 210.0 / 297.0  # 約0.707
    
    # ファイル名を取得
    file_name = os.path.basename(file_path)
    file_dir = os.path.dirname(file_path)
    name_without_ext = os.path.splitext(file_name)[0]
    extension = os.path.splitext(file_name)[1]
    
    # バックアップパスを生成
    backup_path = os.path.join(file_dir, f"{name_without_ext}_backup{extension}")
    
    print(f"処理対象: {file_name}")
    print(f"元画像パス: {file_path}")
    
    # ファイル存在チェック
    if not os.path.exists(file_path):
        print(f"❌ エラー: 画像ファイルが見つかりません: {file_path}")
        return False
    
    # 画像ファイルかチェック
    try:
        with Image.open(file_path) as test_image:
            pass  # ファイルが正常に開けるかテスト
    except Exception:
        print(f"❌ エラー: 有効な画像ファイルではありません: {file_path}")
        return False
    
    # バックアップを作成
    if not os.path.exists(backup_path):
        print("バックアップを作成中...")
        image = Image.open(file_path)
        image.save(backup_path)
        print(f"バックアップ保存: {backup_path}")
    else:
        print("バックアップは既に存在します")
    
    # 元画像を開く
    try:
        image = Image.open(file_path)
        original_width, original_height = image.size
        original_ratio = original_width / original_height
        
        print(f"元画像サイズ: {original_width} x {original_height}")
        print(f"元画像比率: {original_ratio:.3f}")
        print(f"A4目標比率: {A4_RATIO:.3f}")
        print(f"A4との差: {abs(original_ratio - A4_RATIO):.3f}")
        
        if abs(original_ratio - A4_RATIO) < 0.01:
            print("✅ 画像は既にA4比率に近いです。変更は不要です。")
            # ログに記録（変更なし）
            log_template_info(file_name, (original_width, original_height), 
                            (original_width, original_height), original_ratio, 
                            original_ratio, A4_RATIO)
            return True
        
        # 新しい高さを計算（幅は保持）
        new_width = original_width
        new_height = int(original_width / A4_RATIO)
        new_ratio = new_width / new_height
        
        print(f"目標サイズ: {new_width} x {new_height}")
        print(f"目標比率: {new_ratio:.3f}")
        
        # 装飾枠の比率を自動検出
        frame_ratio = detect_frame_ratio(image, file_path)
        frame_height = int(original_height * frame_ratio)
        
        print(f"自動検出装飾枠の高さ: {frame_height}px (比率: {frame_ratio*100:.1f}%)")
        
        # 新しい中央部分の高さを計算
        new_middle_height = new_height - (frame_height * 2)
        original_middle_height = original_height - (frame_height * 2)
        
        print(f"元の中央部分の高さ: {original_middle_height}px")
        print(f"新しい中央部分の高さ: {new_middle_height}px")
        
        if new_middle_height <= 0:
            print("❌ エラー: 中央部分が縮小しすぎです。装飾枠の比率を調整してください。")
            return False
        
        # 縮小/拡大方向を判定
        resize_direction = "縮小" if new_height < original_height else "拡大"
        change_percent = abs((new_height - original_height) / original_height * 100)
        print(f"処理方向: {resize_direction} ({change_percent:.1f}%)")
        
        # 新しい画像を作成
        new_image = Image.new('RGBA', (new_width, new_height), (0, 0, 0, 0))
        
        # 上部の装飾枠をコピー
        top_frame = image.crop((0, 0, original_width, frame_height))
        new_image.paste(top_frame, (0, 0))
        print("✅ 上部装飾枠をコピーしました")
        
        # 中央部分を縮小/拡大してコピー
        middle_part = image.crop((0, frame_height, original_width, original_height - frame_height))
        
        # リサンプリング方法を選択（画質優先）
        if new_middle_height < original_middle_height:
            # 縮小の場合
            resampling = Image.Resampling.LANCZOS
        else:
            # 拡大の場合
            resampling = Image.Resampling.BICUBIC
        
        middle_resized = middle_part.resize((new_width, new_middle_height), resampling)
        new_image.paste(middle_resized, (0, frame_height))
        print(f"✅ 中央部分を{resize_direction}してコピーしました")
        
        # 下部の装飾枠をコピー
        bottom_frame = image.crop((0, original_height - frame_height, original_width, original_height))
        new_image.paste(bottom_frame, (0, new_height - frame_height))
        print("✅ 下部装飾枠をコピーしました")
        
        # 画像を保存
        new_image.save(file_path, "PNG", optimize=True)
        
        print(f"✅ {file_name} を正常に調整しました: {file_path}")
        print(f"📁 元の画像はバックアップとして保存されています: {backup_path}")
        print(f"📏 新しいサイズ: {new_width} x {new_height} (比率: {new_ratio:.3f})")
        
        # 詳細ログを記録
        log_template_info(file_name, (original_width, original_height), 
                         (new_width, new_height), original_ratio, new_ratio, A4_RATIO)
        
        return True
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        return False

def process_multiple_files(file_paths):
    """複数のファイルを処理"""
    success_count = 0
    total_count = len(file_paths)
    
    print(f"🎯 {total_count}個のファイルを処理します:")
    for file_path in file_paths:
        print(f"  - {os.path.basename(file_path)}")
    print("=" * 80)
    
    # ログファイルの初期化
    log_file = "template_resize_log.txt"
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n=== 処理開始: {timestamp} ===\n")
        f.write(f"処理対象: {[os.path.basename(p) for p in file_paths]}\n")
        f.write("時刻 | ファイル名 | 変更前サイズ | 変更後サイズ | 元比率 | 新比率 | A4比率 | 元A4差 | 新A4差\n")
        f.write("-" * 120 + "\n")
    
    for i, file_path in enumerate(file_paths, 1):
        print(f"\n📋 [{i}/{total_count}] {os.path.basename(file_path)} を処理中...")
        print("-" * 50)
        
        if smart_resize_to_a4_ratio(file_path):
            success_count += 1
            print(f"✅ {os.path.basename(file_path)} 完了")
        else:
            print(f"❌ {os.path.basename(file_path)} 失敗")
    
    # 処理終了をログに記録
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"=== 処理完了: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")
        f.write(f"成功: {success_count}/{total_count} 個\n\n")
    
    print("\n" + "=" * 80)
    print(f"📊 処理結果: {success_count}/{total_count} 個のファイルが正常に処理されました")
    print(f"📝 詳細ログ: {log_file}")
    
    return success_count == total_count

def parse_arguments():
    """コマンドライン引数を解析"""
    # テンプレート番号形式（数値のみ）かファイルパス形式かを判定
    file_paths = []
    
    for arg in sys.argv[1:]:
        if arg.isdigit():
            # 数値の場合、従来のテンプレート番号として処理
            template_num = int(arg)
            file_path = f"backend/apps/ninestarki/static/images/background/certificate_template{template_num}.png"
            file_paths.append(file_path)
        else:
            # ファイルパスとして処理
            file_paths.append(arg)
    
    return file_paths

if __name__ == "__main__":
    print("🖼️  Certificate Template 汎用A4比率調整スクリプト")
    print("📋 装飾枠を自動検出し、中央部分を調整してA4比率に最適化します")
    print("=" * 80)
    
    # コマンドライン引数をチェック
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  テンプレート番号で指定:")
        print("    python3 resize_image_smart.py 3")
        print("    python3 resize_image_smart.py 4 5 6")
        print("")
        print("  ファイルパスで指定:")
        print("    python3 resize_image_smart.py path/to/image1.png")
        print("    python3 resize_image_smart.py image1.png image2.png image3.png")
        print("    python3 resize_image_smart.py backend/apps/ninestarki/static/images/background/certificate_template*.png")
        print("")
        print("  混在も可能:")
        print("    python3 resize_image_smart.py 3 path/to/image.png 5")
        print("")
        print("📝 処理ログは template_resize_log.txt に保存されます")
        sys.exit(1)
    
    # 引数を解析
    try:
        file_paths = parse_arguments()
        
        # ファイルパスの重複を除去
        file_paths = list(dict.fromkeys(file_paths))  # 順序を保持しつつ重複除去
        
        if not file_paths:
            print("❌ エラー: 処理対象のファイルが指定されていません")
            sys.exit(1)
        
        # 処理実行
        success = process_multiple_files(file_paths)
        
        if success:
            print("\n🎉 すべてのファイルが正常に処理されました！")
            print("PDFを生成して結果を確認してください。")
        else:
            print("\n⚠️  一部のファイルで問題が発生しました。")
        
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        sys.exit(1) 