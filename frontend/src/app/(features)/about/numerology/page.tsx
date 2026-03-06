"use client";

import React from "react";

export default function NumerologyPage() {
    return (
        <div style={{
            minHeight: '100%',
            display: 'flex',
            flexDirection: 'column',
            backgroundColor: '#f9f7f2',
            position: 'relative',
            fontFamily: '"Montserrat", sans-serif',
            color: '#4a4a4a',
            backgroundImage: `
        radial-gradient(circle at 10% 10%, rgba(216, 167, 167, 0.03) 0%, transparent 40%),
        radial-gradient(circle at 90% 90%, rgba(155, 176, 165, 0.03) 0%, transparent 40%)
      `
        }}>
            <header className="result-header" style={{
                width: '100%',
                borderBottom: '1px solid rgba(212, 175, 55, 0.1)',
                backgroundColor: 'rgba(255, 255, 255, 0.3)',
                backdropFilter: 'blur(4px)',
                position: 'sticky', top: 0, zIndex: 50
            }}>
                <div style={{ maxWidth: '800px', margin: '0 auto', display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <span style={{ color: '#d4af37', fontSize: '20px' }}>✦</span>
                    <h1 style={{
                        fontSize: 'clamp(16px, 4vw, 20px)', fontWeight: 'normal', color: '#4a4a4a',
                        fontFamily: '"Shippori Mincho", "Noto Serif JP", serif',
                        letterSpacing: '0.05em', margin: 0
                    }}>
                        数秘術について
                    </h1>
                </div>
            </header>

            <main className="result-main" style={{ maxWidth: '800px', margin: '0 auto', position: 'relative', zIndex: 10, width: '100%' }}>

                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', marginBottom: '32px' }}>
                    <h3 style={{
                        color: '#d4af37', fontSize: '14px', letterSpacing: '0.3em',
                        fontWeight: 500, textTransform: 'uppercase',
                        fontFamily: '"Montserrat", sans-serif', margin: 0
                    }}>
                        Numerology
                    </h3>
                    <div style={{ width: '40px', height: '1px', background: 'linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.6), transparent)' }} />
                </div>

                <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '24px',
                    color: 'rgba(74, 74, 74, 0.85)',
                    fontSize: '15px', lineHeight: 2.0,
                    fontFamily: '"Noto Serif JP", serif',
                    marginTop: '24px'
                }}>
                    <p style={{ margin: 0 }}>
                        数秘術（Numerology）は、「数」に霊的な意味があると考える占術です。
                    </p>
                    <p style={{ margin: 0 }}>
                        起源は古代バビロニアやエジプトに遡り、建築や信仰で数の神秘が重視されました。
                    </p>
                    <p style={{ margin: 0 }}>
                        ギリシアの数学者ピタゴラスは、「万物は数から成る」という思想を提唱しました。
                    </p>
                    <p style={{ margin: 0 }}>
                        中世以降はカバラなどの神秘思想とも結びつき、近代ヨーロッパで体系化が進みます。
                    </p>
                    <p style={{ margin: 0 }}>
                        現代の主流では、生年月日や名前を一定のルールで数に置き換え、1～9に還元します。
                    </p>
                    <p style={{ margin: 0 }}>
                        生年月日を合計して導き出す運命数（ライフパスナンバー）は、個人の基本的な性格や人生のテーマを示す重要な数とされ、数秘術の中でも特に広く活用されています。
                    </p>
                    <p style={{ margin: 0 }}>
                        たとえば2025年1月26日生まれは「2+0+2+5+1+2+6=18→1+8=9」が運命数となります。
                    </p>
                    <p style={{ margin: 0 }}>
                        1～9の数字は、それぞれ独立性や協調性など異なる象徴を持ちます。<br />
                        1はリーダーシップ、2は協調、3は創造性、4は安定、5は自由、6は愛、7は探究、8は成功、9は博愛。
                    </p>
                    <p style={{ margin: 0 }}>
                        また、マスターナンバーと呼ばれる11、22、33は、一般的な数とは異なり、特別な使命や強いエネルギーを持つ数とされています。
                    </p>
                    <p style={{ margin: 0 }}>
                        名前のアルファベットを数字に置き換える方法もあり、「表現数」などを読み解きます。
                    </p>
                    <p style={{ margin: 0 }}>
                        数秘術は自己分析のほか、相性占いや日々の指針を知るためのツールにもなります。
                    </p>
                    <p style={{ margin: 0 }}>
                        数秘術は、科学とは異なる視点から、数字を通じて自分や未来を考える楽しいツールとして活用できます。<br />
                        まずは運命数を計算し、1～9のキーワードを知るだけでも楽しめます。<br />
                        古代から続く数字の神秘を身近に感じながら、自分や周囲を見つめ直してみてください。
                    </p>
                </div>

            </main>
        </div>
    );
}
