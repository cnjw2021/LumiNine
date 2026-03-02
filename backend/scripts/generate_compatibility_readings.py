#!/usr/bin/env python3
import csv
import os
import random

# データ格納用ディレクトリを確認
os.makedirs('backend/scripts/csv', exist_ok=True)

# シンボルパターンを読み込む
patterns = []
with open('backend/scripts/csv/compatibility_symbol_pattern_master.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        patterns.append(row)

# シンボルの意味を読み込む
symbols_meaning = {}
symbols_desc = {}
with open('backend/scripts/csv/compatibility_symbol_master.csv', 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        symbols_meaning[row['symbol']] = row['meaning']
        symbols_desc[row['symbol']] = row['description']

# シンボルの重みを定義（高いほど良い相性）
symbol_weights = {
    '★': 10,
    '☆': 9,
    '◎': 8,
    '○': 7,
    'Ｐ': 6,
    'Ｆ': 5,
    'Ｎ': 0,
    '▲': -5,
    '◆': -10
}

# シンボルの分類
positive_symbols = ['★', '☆', '◎', '○', 'Ｐ', 'Ｆ']
neutral_symbols = ['Ｎ']
negative_symbols = ['▲', '◆']

# 各シンボルの関係性への影響を定義
symbol_aspects = {
    '★': ['恋愛', '結婚', '家庭', '信頼'],
    '☆': ['長期的関係', '相互成長', '精神的つながり'],
    '◎': ['価値観', '協力', '共同作業', '調和'],
    '○': ['理解', '安定', '平和', '穏やか'],
    'Ｐ': ['仕事', '実務', 'ビジネス', '目標達成'],
    'Ｆ': ['友情', '気軽さ', '社交', '楽しさ'],
    'Ｎ': ['中立', '変動', '不確定'],
    '▲': ['摩擦', '衝突', '誤解', '価値観の違い'],
    '◆': ['対立', '反発', '大きな衝突', '相容れない']
}

# シンボルの組み合わせによる相乗効果
synergy_patterns = {
    '★☆': 'お互いの良さを引き出し合う組み合わせ',
    '★◎': '深い絆と実務的な協力が両立する',
    '☆◎': '共感と理解に基づく長期的な協力関係',
    'ＰＦ': 'ビジネスと友情が良いバランスで両立する',
    '◎○': '安定感のある穏やかな協力関係',
    '▲◆': '大きな衝突が予想される厳しい関係'
}

# 相性パターンごとの具体的なアドバイス
relationship_advice = {
    'best': [
        '互いに素直な気持ちを伝え合うことで、さらに絆が深まります。',
        '共通の趣味や活動を通じて、より深いつながりを築けるでしょう。',
        '互いの長所を認め合い、成長を促進し合える関係です。',
        '困難な時こそ力を合わせることで、より強固な絆になります。'
    ],
    'good': [
        '定期的なコミュニケーションを心がけることで、理解が深まります。',
        'お互いのプライバシーや個性を尊重することで、良好な関係が続きます。',
        '小さな誤解があっても、話し合いで解決できる関係です。',
        '互いの違いを認め合うことで、より安定した関係を築けます。'
    ],
    'business': [
        '明確な役割分担が、より良い協力関係につながります。',
        '定期的なフィードバックで、ビジネス関係を向上させられます。',
        '互いの専門性を活かすことで、より高い成果が期待できます。',
        '目標を共有し、定期的に進捗を確認することが大切です。'
    ],
    'friendship': [
        '気軽に連絡を取り合う関係を維持することが大切です。',
        '互いに期待しすぎず、自然体で接することがコツです。',
        '趣味や興味を共有することで、より楽しい時間を過ごせます。',
        '相手の話をよく聞くことで、友情が深まります。'
    ],
    'caution': [
        'コミュニケーションの取り方に工夫が必要です。',
        '互いの違いを理解し、尊重する姿勢が大切です。',
        '期待値を現実的に設定することで、摩擦を減らせます。',
        '相手の価値観や考え方を否定せず、受け入れる努力をしましょう。'
    ],
    'avoid': [
        '必要以上の関わりは避け、一定の距離を保つことが賢明です。',
        '重要な決断を共にすることは控えた方が良いでしょう。',
        '互いに干渉しすぎないよう、境界線を明確にしておきましょう。',
        '衝突を避けるため、デリケートな話題には触れないように気をつけましょう。'
    ],
    'neutral': [
        '関係の発展は互いの努力次第です。',
        '共通の興味を見つけることで、関係が良い方向に進む可能性があります。',
        '相手の長所に注目することで、より良い関係を築ける可能性があります。',
        '状況や環境が変われば、関係性も変化する可能性があります。'
    ]
}

# テーマのリスト
themes = [
    "general",      # 全般的な相性解説
    "relationship", # 恋愛・結婚関係
    "business",     # ビジネス関係
    "friendship",   # 友人関係
    "family"        # 家族関係
]

# シンボルの繰り返しによる強調効果を解析する関数
def analyze_repeated_symbols(symbols):
    # シンボルごとの出現回数をカウント
    symbol_counts = {}
    for s in symbols:
        if s not in symbol_counts:
            symbol_counts[s] = 1
        else:
            symbol_counts[s] += 1
    
    # 繰り返しの強調効果を分析
    emphasis = []
    for symbol, count in symbol_counts.items():
        if count >= 2:
            if symbol in positive_symbols:
                if count >= 4:
                    emphasis.append(f"{symbols_meaning[symbol]}の要素が極めて強く、この関係の中心的な特徴となります。")
                elif count == 3:
                    emphasis.append(f"{symbols_meaning[symbol]}の要素が非常に強く、お互いの関係において重要な役割を果たします。")
                else:  # count == 2
                    emphasis.append(f"{symbols_meaning[symbol]}の要素が強調されています。")
            elif symbol in negative_symbols:
                if count >= 4:
                    emphasis.append(f"{symbols_meaning[symbol]}の要素が極めて強く、関係において特に注意が必要です。")
                elif count == 3:
                    emphasis.append(f"{symbols_meaning[symbol]}の要素が非常に強く、関係において慎重なアプローチが必要です。")
                else:  # count == 2
                    emphasis.append(f"{symbols_meaning[symbol]}の要素がより顕著に表れます。")
            elif symbol in neutral_symbols:
                if count >= 2:
                    emphasis.append(f"{symbols_meaning[symbol]}の要素が特に強調されます。")
    
    return emphasis

# 文字数制限に合わせて文章を生成する補助関数
def limit_text_length(text, max_length=400):
    if len(text) <= max_length:
        return text
    
    # 文章を句点で分割
    sentences = text.split('。')
    result = ""
    
    # 文章を一つずつ追加し、制限を超えないようにする
    for sentence in sentences:
        if sentence:  # 空文字列でない場合
            temp = result + sentence + "。"
            if len(temp) <= max_length:
                result = temp
            else:
                break
    
    return result

# 鑑定文を生成する関数
def generate_reading(pattern_code, symbols, theme):
    # シンボルごとの出現回数をカウント
    symbol_counts = {s: symbols.count(s) for s in set(symbols)}
    
    # シンボルの繰り返しによる強調を分析
    emphasis_effects = analyze_repeated_symbols(symbols)
    has_emphasis = len(emphasis_effects) > 0
    
    # シンボルの総合的な重み付けスコアを計算
    total_score = sum(symbol_weights[s] * count for s, count in symbol_counts.items())
    
    # 肯定的・中立的・否定的シンボルの数をカウント
    positive_count = sum(symbol_counts.get(s, 0) for s in positive_symbols)
    neutral_count = sum(symbol_counts.get(s, 0) for s in neutral_symbols)
    negative_count = sum(symbol_counts.get(s, 0) for s in negative_symbols)
    
    # 最も多いシンボルを特定
    dominant_symbol = max(symbol_counts.items(), key=lambda x: x[1])[0] if symbol_counts else None
    
    # 存在するシンボルのリスト
    present_symbols = [s for s in symbol_counts.keys()]
    
    # シンボルの組み合わせによる相乗効果を確認
    synergies = []
    for combo, description in synergy_patterns.items():
        if all(s in symbols for s in combo):
            synergies.append(description)
    
    # 関係の主要な側面を特定
    aspects = []
    for s in present_symbols:
        if s in symbol_aspects:
            aspects.extend(symbol_aspects[s])
    
    # 重複を排除
    aspects = list(set(aspects))
    
    # 相性のタイプを決定
    if total_score >= 15:
        relationship_type = "最高の相性"
        advice_type = "best"
    elif total_score >= 10:
        relationship_type = "とても良い相性"
        advice_type = "best"
    elif total_score >= 7:
        relationship_type = "優れた相性"
        advice_type = "good"
    elif total_score >= 5:
        relationship_type = "良好な相性"
        advice_type = "good"
    elif total_score > 0:
        if 'Ｐ' in symbols and ('ビジネス' in aspects or '仕事' in aspects):
            relationship_type = "ビジネス向きの相性"
            advice_type = "business"
        elif 'Ｆ' in symbols and ('友情' in aspects or '気軽さ' in aspects):
            relationship_type = "友人向きの相性"
            advice_type = "friendship"
        else:
            relationship_type = "穏やかな相性"
            advice_type = "good"
    elif total_score == 0:
        relationship_type = "中立の相性"
        advice_type = "neutral"
    elif total_score > -7:
        relationship_type = "注意が必要な相性"
        advice_type = "caution"
    else:
        relationship_type = "避けるべき相性"
        advice_type = "avoid"
    
    # テーマに応じたタイトルの調整
    theme_titles = {
        "general": relationship_type,
        "relationship": f"{relationship_type}の恋愛関係",
        "business": f"{relationship_type}のビジネス関係",
        "friendship": f"{relationship_type}の友人関係",
        "family": f"{relationship_type}の家族関係"
    }
    
    title = theme_titles.get(theme, relationship_type)
    
    # テーマに応じた導入文
    theme_intros = {
        "general": "この相性は全体的に",
        "relationship": "恋愛や結婚関係においては",
        "business": "仕事やビジネス関係においては",
        "friendship": "友人関係においては",
        "family": "家族関係においては"
    }
    
    # 関係の詳細な説明を生成
    content_parts = []
    content_parts.append(theme_intros.get(theme, "この相性は"))
    
    # 相性の基本的な説明
    if total_score >= 10:
        content_parts.append("非常に良好で、互いに強い絆で結ばれる運命的な関係を築ける可能性があります。")
    elif total_score >= 7:
        content_parts.append("とても良く、お互いの価値観が合い、深い理解と調和に基づく関係を築けます。")
    elif total_score >= 5:
        content_parts.append("良好で、安定した関係を築きやすい特徴があります。")
    elif total_score > 0:
        content_parts.append("基本的に良好ですが、一部に課題もある関係です。")
    elif total_score == 0:
        content_parts.append("特に良くも悪くもない中立的な関係で、互いの努力次第で発展します。")
    elif total_score > -7:
        content_parts.append("一部に課題があり、注意が必要な関係です。")
    else:
        content_parts.append("大きな課題があり、互いに距離を置くことが賢明かもしれません。")
    
    # 強調効果の説明を追加
    if has_emphasis:
        content_parts.append(random.choice(emphasis_effects) + " ")
    
    # 相乗効果の説明
    if synergies:
        content_parts.append(f"{random.choice(synergies)}と言えます。")
    
    # 主要な側面の説明
    if aspects:
        selected_aspects = random.sample(aspects, min(2, len(aspects)))
        content_parts.append(f"特に{', '.join(selected_aspects)}の面で特徴が現れるでしょう。")
    
    # テーマに応じたアドバイスのカスタマイズ
    theme_advice_types = {
        "relationship": "best" if total_score > 0 else "caution",
        "business": "business" if total_score > 0 else "caution",
        "friendship": "friendship" if total_score > 0 else "neutral",
        "family": "good" if total_score > 0 else "neutral"
    }
    
    # テーマに基づいたアドバイスタイプを選択（既定値が優先）
    if theme in theme_advice_types:
        if total_score < -7:  # 非常に悪い相性の場合は避けるべきアドバイス
            theme_advice = "avoid"
        else:
            theme_advice = theme_advice_types[theme]
        advice = random.choice(relationship_advice[theme_advice])
    else:
        advice = random.choice(relationship_advice[advice_type])
    
    content_parts.append(advice)
    
    # 文章を連結して長さを制限
    content = ' '.join(content_parts)
    content = limit_text_length(content)
    
    return {
        "title": title,
        "content": content
    }

# パターンコードごとの特殊鑑定文（オーバーライド用）
special_readings = {
    "PATTERN_001": {  # 単体の▲
        "general": {
            "title": "軽度の注意が必要な相性",
            "content": "この相性は一部の側面で注意が必要ですが、全体としては大きな問題はありません。コミュニケーションを工夫することで、良好な関係を築くことも可能です。互いの違いを尊重し、理解を深めることで徐々に関係が改善していくでしょう。"
        },
        "relationship": {
            "title": "やや注意が必要な恋愛相性",
            "content": "恋愛関係においては、時に小さな誤解が生じやすい相性です。お互いの価値観の違いを理解し尊重することで、安定した関係に発展する可能性があります。定期的なコミュニケーションを心がけ、互いの気持ちを素直に伝え合うことが大切です。"
        },
        "business": {
            "title": "軽度の注意が必要なビジネス相性",
            "content": "仕事上の関係では、時に意見の相違が生じることがありますが、それを前向きな議論に変えることができれば、むしろ創造的な結果を生み出せる可能性があります。役割分担を明確にし、定期的なフィードバックを行うことで、より良い関係を築けるでしょう。"
        }
    },
    "PATTERN_074": {  # 単体の◆
        "general": {
            "title": "強い衝突の可能性がある相性",
            "content": "この相性はエネルギーの衝突が強く、大きな摩擦が生じやすい特徴があります。互いに距離を置くことが賢明かもしれません。必要以上の関わりは避け、相手の価値観や考え方を否定せず、一定の境界線を保つことが重要です。"
        },
        "relationship": {
            "title": "避けるべき恋愛相性",
            "content": "恋愛関係においては、基本的な価値観や生活スタイルが大きく異なるため、お互いにストレスを感じやすい関係になる可能性が高いです。無理に関係を深めようとするよりも、友人としての関係を保つか、適度な距離を置くことを検討した方が良いでしょう。"
        }
    },
    "PATTERN_085": {  # 単体の◎
        "general": {
            "title": "協力的で調和の取れた相性",
            "content": "この相性は互いの価値観が合い、協力し合える良好な特徴があります。共同作業や長期的な関係に適しています。互いの考え方や感じ方が似ているため、自然と調和のとれた関係を築きやすいでしょう。共通の目標に向かって協力することで、良い成果を上げられます。"
        },
        "business": {
            "title": "調和のとれたビジネス相性",
            "content": "ビジネス関係においては、互いの強みを活かし合える協力関係を築きやすいでしょう。共通の目標に向かって効率よく進むことができます。価値観が合うため、コミュニケーションがスムーズで、互いを尊重し合える関係を築きやすいでしょう。"
        }
    },
    "PATTERN_206": {  # 単体のＦ
        "general": {
            "title": "友好的で気軽な相性",
            "content": "この相性は気軽で友好的な関係を築きやすい特徴があります。負担のない付き合いに適しています。リラックスした雰囲気の中で、楽しい時間を共有できるでしょう。深刻な話題よりも、軽い交流が心地よく感じられる関係です。"
        },
        "friendship": {
            "title": "理想的な友人関係",
            "content": "友人関係においては、気軽に楽しい時間を共有できる関係を築きやすいでしょう。互いにプレッシャーをかけず、自然体で接することができます。趣味や興味を共有することで、より楽しい時間を過ごせるでしょう。"
        }
    },
    "PATTERN_237": {  # 単体のＮ
        "general": {
            "title": "中立的で可変性のある相性",
            "content": "この相性は特に良くも悪くもない中立的な特徴があります。関係の質は状況や互いの努力次第で変化していくでしょう。共通の興味を見つけることで、関係を良い方向に発展させることができます。状況や環境が変われば、関係性も変化する可能性があります。"
        }
    },
    "PATTERN_238": {  # 単体のＰ
        "general": {
            "title": "実務的な相性の良さ",
            "content": "この相性はビジネスや実務的な関係において良好な特徴があります。目標達成に向けた協力関係に適しています。共通の目標に向かって効率よく協力でき、互いの役割を尊重し合える関係を築けるでしょう。"
        },
        "business": {
            "title": "効率的なビジネスパートナー",
            "content": "ビジネス関係では、互いの役割を尊重し合い、実務的な信頼関係を形成しやすいでしょう。共通の目標に向かって効率的に協力できる関係です。明確な役割分担により、より良い協力関係を築くことができます。"
        }
    }
}

# 特定のパターンに対するカスタム鑑定文生成関数
def get_custom_reading(pattern_code, symbols, theme):
    # 特殊パターンの場合かつテーマが対応している場合
    if pattern_code in special_readings and theme in special_readings[pattern_code]:
        return special_readings[pattern_code][theme]
    # 特殊パターンだが対応するテーマがない場合は一般的な内容を使用
    elif pattern_code in special_readings and "general" in special_readings[pattern_code]:
        return special_readings[pattern_code]["general"]
    
    # ★が含まれるパターンの特別処理
    if '★' in symbols:
        special_star_readings = {
            "general": {
                "title": "運命的な最高の相性",
                "content": "これは非常に稀で特別な相性です。互いに強く惹かれ合い、深い絆で結ばれる運命的な関係と言えるでしょう。結婚や長期的なパートナーシップに最適な相性です。互いの長所を認め合い、成長を促進し合える関係で、困難な時こそ力を合わせることで、さらに強固な絆になります。"
            },
            "relationship": {
                "title": "運命的な恋愛相性",
                "content": "恋愛関係においては、この相性は非常に特別です。互いに深い魂のレベルで共鳴し合い、長期的で充実した関係を築くことができるでしょう。お互いに素直な気持ちを伝え合うことで、さらに絆が深まります。共通の価値観を持ち、互いに高め合える関係を築けます。"
            },
            "business": {
                "title": "卓越したビジネス相性",
                "content": "ビジネス関係においては、互いの才能を最大限に引き出し合える関係です。共同での事業や長期的なパートナーシップに最適です。互いの専門性を活かすことで、より高い成果が期待できます。目標を共有し、定期的に進捗を確認することで、さらなる発展を促せるでしょう。"
            },
            "friendship": {
                "title": "生涯の友情",
                "content": "友人関係においては、互いに深い理解と信頼で結ばれた特別な友情を築くことができるでしょう。時間や距離を超えて続く絆を育むことができます。共通の趣味や活動を通じて、より深いつながりを築けるでしょう。お互いの人生の大切な場面で支え合える関係です。"
            },
            "family": {
                "title": "理想的な家族関係",
                "content": "家族関係においては、互いに深い愛情と尊重の絆で結ばれた関係を築くことができます。強い信頼と深い絆が特徴の理想的な家族関係になるでしょう。互いの個性を尊重しながらも、共通の価値観で結ばれた強固な家族の絆を形成できます。"
            }
        }
        
        if theme in special_star_readings:
            return special_star_readings[theme]
        else:
            return special_star_readings["general"]
    
    # 他のカスタムパターン条件をここに追加可能
    return None

# 鑑定文を生成してCSVに書き込む
with open('backend/scripts/csv/compatibility_readings_master.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f, quoting=csv.QUOTE_ALL)
    writer.writerow(["pattern_code", "theme", "title", "content"])
    
    for pattern in patterns:
        pattern_code = pattern['pattern_code']
        symbols = pattern['symbols']
        
        # 各テーマに対する鑑定文を生成
        for theme in themes:
            # カスタム鑑定文があるか確認
            custom_reading = get_custom_reading(pattern_code, symbols, theme)
            
            # なければ通常の生成関数を使用
            reading = custom_reading if custom_reading else generate_reading(pattern_code, symbols, theme)
            
            # 鑑定文を書き込む
            writer.writerow([pattern_code, theme, reading["title"], reading["content"]])

print(f"backend/scripts/csv/compatibility_readings_master.csv が生成されました。{len(patterns)}種類のパターンに対して、{len(themes)}つのテーマごとの鑑定文が生成されました（合計{len(patterns)*len(themes)}件）。") 