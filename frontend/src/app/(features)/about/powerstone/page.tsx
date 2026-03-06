"use client";

import React from "react";
import { Stack, Text, SimpleGrid } from "@mantine/core";
import Image from "next/image";
interface StoneData {
    names: {
        ja: string;
        en: string;
    };
    description: {
        ja: string;
    };
}

const POWERSTONES: Record<string, StoneData> = {
    ruby: {
        names: { ja: "ルビー", en: "Ruby" },
        description: { ja: "情熱と活力の石。太陽のエネルギーを宿す。" }
    },
    garnet: {
        names: { ja: "ガーネット", en: "Garnet" },
        description: { ja: "実りと忍耐の石。深い赤が生命力を象徴。" }
    },
    moonstone: {
        names: { ja: "ムーンストーン", en: "Moonstone" },
        description: { ja: "直感と感受性の石。月の光のように穏やかなエネルギー。" }
    },
    pearl: {
        names: { ja: "パール", en: "Pearl" },
        description: { ja: "純粋と保護の石。母なる海の知恵を象徴。" }
    },
    citrine: {
        names: { ja: "シトリン", en: "Citrine" },
        description: { ja: "繁栄と成功の石。太陽の光を凝縮した黄金色。" }
    },
    amethyst: {
        names: { ja: "アメジスト", en: "Amethyst" },
        description: { ja: "知恵と霊性の石。精神の安定と浄化をもたらす。" }
    },
    green_aventurine: {
        names: { ja: "グリーンアベンチュリン", en: "Green Aventurine" },
        description: { ja: "幸運と癒しの石。心身のバランスを整える。" }
    },
    emerald: {
        names: { ja: "エメラルド", en: "Emerald" },
        description: { ja: "叡智とコミュニケーションの石。水星の知的エネルギー。" }
    },
    peridot: {
        names: { ja: "ペリドット", en: "Peridot" },
        description: { ja: "希望と前進の石。太陽の石とも呼ばれる明るいエネルギー。" }
    },
    rose_quartz: {
        names: { ja: "ローズクォーツ", en: "Rose Quartz" },
        description: { ja: "愛と美の石。金星のエネルギーを宿し、恋愛運を高める。" }
    },
    turquoise: {
        names: { ja: "ターコイズ", en: "Turquoise" },
        description: { ja: "友情と幸福の石。旅の守護石としても知られる。" }
    },
    lapis_lazuli: {
        names: { ja: "ラピスラズリ", en: "Lapis Lazuli" },
        description: { ja: "真実と内なる視野の石。ケートゥの神秘的エネルギー。" }
    },
    onyx: {
        names: { ja: "オニキス", en: "Onyx" },
        description: { ja: "忍耐と規律の石。土星の安定したエネルギー。" }
    },
    blue_sapphire: {
        names: { ja: "ブルーサファイア", en: "Blue Sapphire" },
        description: { ja: "叡智と真理の石。土星の深い教訓を象徴。" }
    },
    carnelian: {
        names: { ja: "カーネリアン", en: "Carnelian" },
        description: { ja: "勇気と行動力の石。火星の勝利のエネルギー。" }
    },
    tiger_eye: {
        names: { ja: "タイガーアイ", en: "Tiger's Eye" },
        description: { ja: "洞察力と金運の石。富と繁栄を引き寄せる。" }
    },
    red_coral: {
        names: { ja: "レッドコーラル", en: "Red Coral" },
        description: { ja: "生命力と健康の石。火星の保護エネルギー。" }
    },
    yellow_sapphire: {
        names: { ja: "イエローサファイア", en: "Yellow Sapphire" },
        description: { ja: "幸運と豊穣の石。木星の祝福のエネルギー。" }
    },
    sunstone: {
        names: { ja: "サンストーン", en: "Sunstone" },
        description: { ja: "自信とリーダーシップの石。太陽の輝きを宿す。" }
    },
    diamond: {
        names: { ja: "ダイヤモンド", en: "Diamond" },
        description: { ja: "永遠と純粋の石。金星の最高の愛のエネルギー。" }
    },
    cats_eye: {
        names: { ja: "キャッツアイ", en: "Cat's Eye" },
        description: { ja: "直感と保護の石。ケートゥの守護エネルギー。" }
    },
    hessonite: {
        names: { ja: "ヘソナイト", en: "Hessonite" },
        description: { ja: "浄化と解放の石。ラーフの変容エネルギー。" }
    },
    labradorite: {
        names: { ja: "ラブラドライト", en: "Labradorite" },
        description: { ja: "直感と変容の石。オーロラのような輝きが霊的覚醒を促す。" }
    },
    fluorite: {
        names: { ja: "フローライト", en: "Fluorite" },
        description: { ja: "集中と明晰の石。精神の秩序を整え、天才の石と呼ばれる。" }
    },
    clear_quartz: {
        names: { ja: "水晶", en: "Clear Quartz" },
        description: { ja: "増幅と調和の石。すべてのエネルギーを浄化・増幅するマスタークリスタル。" }
    },
    smoky_quartz: {
        names: { ja: "スモーキークォーツ", en: "Smoky Quartz" },
        description: { ja: "グラウンディングと解毒の石。大地のエネルギーで安定をもたらす。" }
    }
};

export default function PowerstonePage() {
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
                <div style={{ maxWidth: '1000px', margin: '0 auto', display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <span style={{ color: '#d4af37', fontSize: '20px' }}>✦</span>
                    <h1 style={{
                        fontSize: 'clamp(16px, 4vw, 20px)', fontWeight: 'normal', color: '#4a4a4a',
                        fontFamily: '"Shippori Mincho", "Noto Serif JP", serif',
                        letterSpacing: '0.05em', margin: 0
                    }}>
                        パワーストーンについて
                    </h1>
                </div>
            </header>

            <main className="result-main" style={{ maxWidth: '1000px', margin: '0 auto', position: 'relative', zIndex: 10, width: '100%' }}>

                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', marginBottom: '32px' }}>
                    <h3 style={{
                        color: '#d4af37', fontSize: '14px', letterSpacing: '0.3em',
                        fontWeight: 500, textTransform: 'uppercase',
                        fontFamily: '"Montserrat", sans-serif', margin: 0
                    }}>
                        Powerstones
                    </h3>
                    <div style={{ width: '40px', height: '1px', background: 'linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.6), transparent)' }} />
                </div>

                <div style={{ marginBottom: '40px' }}>
                    <p style={{
                        color: 'rgba(74, 74, 74, 0.85)',
                        fontSize: '15px', lineHeight: 2.0,
                        fontFamily: '"Noto Serif JP", serif',
                        margin: 0, marginBottom: '24px',
                        textAlign: 'center'
                    }}>
                        パワーストーンは、自然界のエネルギーを宿した天然石であり、身につける人の運気をサポートしたり、バランスを整えたりする力があるとされています。
                    </p>
                    <p style={{
                        color: 'rgba(74, 74, 74, 0.85)',
                        fontSize: '15px', lineHeight: 2.0,
                        fontFamily: '"Noto Serif JP", serif',
                        margin: 0,
                        textAlign: 'center'
                    }}>
                        LumiNineでは、数秘術と九星気学の複合的なアプローチを用いて、その時のあなたに最も必要なパワーストーンを多角的に選定します。<br />
                        以下は、LumiNineの鑑定で使用される主要なパワーストーンとその特徴です。
                    </p>
                </div>

                <SimpleGrid cols={{ base: 2, sm: 3, md: 3, lg: 3 }} spacing={{ base: 8, sm: 16, lg: 24 }}>
                    {Object.entries(POWERSTONES).map(([key, stoneData]) => (
                        <div key={key} style={{
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            textAlign: 'center',
                            backgroundColor: '#ffffff',
                            borderRadius: '16px',
                            padding: '16px 4px', // Reduced horizontal padding to allow more text width
                            boxShadow: '0 5px 20px -5px rgba(0, 0, 0, 0.03)',
                            border: '1px solid rgba(212, 175, 55, 0.05)',
                            transition: 'transform 0.3s ease, box-shadow 0.3s ease',
                            cursor: 'default',
                        }}
                            onMouseEnter={(e) => {
                                e.currentTarget.style.transform = 'translateY(-4px)';
                                e.currentTarget.style.boxShadow = '0 15px 30px -10px rgba(0, 0, 0, 0.08)';
                            }}
                            onMouseLeave={(e) => {
                                e.currentTarget.style.transform = 'none';
                                e.currentTarget.style.boxShadow = '0 5px 20px -5px rgba(0, 0, 0, 0.03)';
                            }}
                        >
                            <div style={{
                                width: '80px', // Scaling down slightly for 2-col
                                height: '80px',
                                borderRadius: '50%',
                                overflow: 'hidden',
                                marginBottom: '16px',
                                border: '1px solid rgba(212, 175, 55, 0.2)',
                                position: 'relative',
                                backgroundColor: '#f9f7f2'
                            }}>
                                <Image
                                    src={`/images/stones/${key}.png`}
                                    alt={stoneData.names.ja}
                                    fill
                                    style={{ objectFit: 'cover' }}
                                    sizes="80px"
                                />
                            </div>

                            <span style={{
                                fontSize: 'clamp(14px, 3.5vw, 18px)', fontWeight: 600,
                                fontFamily: '"Shippori Mincho", "Noto Serif JP", serif',
                                color: '#4a4a4a',
                                marginBottom: '2px'
                            }}>
                                {stoneData.names.ja}
                            </span>
                            <span style={{
                                fontSize: 'clamp(9px, 2.5vw, 11px)',
                                fontFamily: '"Montserrat", sans-serif',
                                color: '#d4af37',
                                letterSpacing: '0.05em', // Reduce letter spacing slightly
                                marginBottom: '12px'
                            }}>
                                {stoneData.names.en}
                            </span>

                            <Text style={{
                                color: 'rgba(74, 74, 74, 0.85)',
                                fontSize: 'clamp(11px, 2.8vw, 13px)', lineHeight: 1.5,
                                fontFamily: '"Noto Serif JP", serif',
                                margin: 0,
                                whiteSpace: 'pre-line'
                            }}>
                                {stoneData.description.ja}
                            </Text>
                        </div>
                    ))}
                </SimpleGrid>

            </main>
        </div>
    );
}
