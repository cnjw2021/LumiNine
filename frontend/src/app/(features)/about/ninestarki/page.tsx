"use client";

import React from "react";
import { Container, Title, Text, Stack, Card, Box } from "@mantine/core";

export default function NineStarKiPage() {
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
                        九星気学について
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
                        Nine Star Ki
                    </h3>
                    <div style={{ width: '40px', height: '1px', background: 'linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.6), transparent)' }} />
                </div>

                <div style={{
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '16px',
                    color: '#4a4a4a',
                    fontSize: '15px', lineHeight: 1.8,
                    fontFamily: '"Noto Serif JP", serif',
                    marginTop: '24px'
                }}>
                    <p style={{ margin: 0 }}>
                        九星気学（Nine Star Ki）は、生年月日から導き出される九星と、それぞれの星が持つ「気」の性質を用いて、運勢や方位の吉凶を占う東洋の占術です。
                    </p>
                    <p style={{ margin: 0 }}>
                        古代中国の民間信仰である「九星」と、五行思想や干支、八卦などの要素が組み合わさり、日本で独自に体系化されました。
                    </p>
                    <p style={{ margin: 0 }}>
                        大正時代に園田真次郎という人物が「気学」としてまとめ上げたものが、現代の九星気学の基礎となっています。
                    </p>
                    <p style={{ margin: 0 }}>
                        宇宙に満ちるエネルギー（気）を9つの種類に分類し、人間が生まれた瞬間にどの「気」を吸い込んだかによって、その人の運命や性格が決定づけられると考えます。
                    </p>
                    <p style={{ margin: 0 }}>
                        LumiNineでは、ベースの性質を表す「本命星」、行動パターンを表す「月命星」などを計算し、年運、月運、そして吉方位・凶方位を導き出します。
                    </p>
                    <p style={{ margin: 0 }}>
                        自分の持つ星の性質を知り、良い気を持つ方位（吉方位）へ動くことで開運へと導く、非常に実践的で前向きな占術です。
                    </p>

                    <Box mt="lg">
                        <h4 style={{
                            color: '#d4af37', fontSize: '16px', letterSpacing: '0.1em',
                            fontWeight: 600, fontFamily: '"Shippori Mincho", "Noto Serif JP", serif',
                            borderBottom: '1px solid rgba(212, 175, 55, 0.3)', paddingBottom: '8px', marginBottom: '12px'
                        }}>
                            基本原理
                        </h4>

                        <Text fw={600} size="sm" color="#7a665a" mt="sm" mb="xs">九つの星（九星）</Text>
                        <p style={{ margin: 0 }}>
                            一白水星、二黒土星、三碧木星、四緑木星、五黄土星、六白金星、七赤金星、八白土星、九紫火星の9つの星が存在します。それぞれの星は、自然界の要素（五行：木・火・土・金・水）と結びついています。
                        </p>

                        <Text fw={600} size="sm" color="#7a665a" mt="sm" mb="xs">本命星と月命星</Text>
                        <p style={{ margin: 0 }}>
                            生まれた年の気である「本命星」は、その人の基本的な性格や、人生全体を通した運勢の土台を示します。生まれた月の気である「月命星」は、精神的な傾向や、子ども時代（主に20歳頃まで）の性格に強く影響します。
                        </p>

                        <Text fw={600} size="sm" color="#7a665a" mt="sm" mb="xs">吉方位と凶方位</Text>
                        <p style={{ margin: 0 }}>
                            「動く方位」によって運気が変化するという「方位取り（祐気取り）」が気学の大きな特徴です。自分と相性の良い星が回っている方位（吉方位）へ旅行や引越しをすることで良い気を取り込み、逆に相性の悪い方位（凶方位）を避けることで災いを防ぎます。
                        </p>
                    </Box>

                    <Box mt="lg">
                        <h4 style={{
                            color: '#d4af37', fontSize: '16px', letterSpacing: '0.1em',
                            fontWeight: 600, fontFamily: '"Shippori Mincho", "Noto Serif JP", serif',
                            borderBottom: '1px solid rgba(212, 175, 55, 0.3)', paddingBottom: '8px', marginBottom: '12px'
                        }}>
                            現代における意義と活用
                        </h4>
                        <p style={{ margin: 0, marginBottom: '8px' }}>
                            九星気学は、単なる運勢占いにとどまらず、自ら運気を切り開くための具体的な行動指針（アクションプラン）として活用されています：
                        </p>
                        <ul style={{ margin: 0, paddingLeft: '24px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
                            <li>生まれ持った才能や長所・短所の客観的な把握</li>
                            <li>年回りや月回りに合わせたバイオリズムの活用</li>
                            <li>引越しや旅行における「吉方位」の選定と運気アップ</li>
                            <li>ビジネスや対人関係における「相性」の理解と対策</li>
                        </ul>
                        <p style={{ margin: 0, marginTop: '12px' }}>
                            「運命は変えられない」と諦めるのではなく、自分にとって良い時期に、良い方向へ動くことで、未来はより明るく発展させることができるという、能動的で力強いメッセージが九星気学には込められています。
                        </p>
                    </Box>

                </div>

            </main>
        </div>
    );
}
