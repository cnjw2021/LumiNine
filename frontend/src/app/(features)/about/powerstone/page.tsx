"use client";

import React from "react";
import { Stack, Text, SimpleGrid } from "@mantine/core";
import Image from "next/image";
import rawPowerstoneCatalog from "@/data/numerology_powerstone_catalog.json";

interface StoneData {
    names: {
        ja: string;
        ko: string;
        en: string;
    };
    description: {
        ja: string;
        ko: string;
        en: string;
    };
}

interface PowerstoneCatalog {
    stones: Record<string, StoneData>;
}

const powerstoneCatalog = rawPowerstoneCatalog as PowerstoneCatalog;

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

                <SimpleGrid cols={{ base: 1, sm: 2, lg: 3 }} spacing="md">
                    {Object.entries(powerstoneCatalog.stones).map(([key, stoneData]) => (
                        <div key={key} style={{
                            display: 'flex',
                            flexDirection: 'column',
                            alignItems: 'center',
                            textAlign: 'center',
                            backgroundColor: '#ffffff',
                            borderRadius: '16px',
                            padding: '20px 12px',
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
                                width: '100px',
                                height: '100px',
                                borderRadius: '50%',
                                overflow: 'hidden',
                                marginBottom: '20px',
                                border: '1px solid rgba(212, 175, 55, 0.2)',
                                position: 'relative',
                                backgroundColor: '#f9f7f2'
                            }}>
                                <Image
                                    src={`/images/stones/${key}.jpg`}
                                    alt={stoneData.names.ja}
                                    fill
                                    style={{ objectFit: 'cover' }}
                                    sizes="100px"
                                />
                            </div>

                            <span style={{
                                fontSize: '18px', fontWeight: 600,
                                fontFamily: '"Shippori Mincho", "Noto Serif JP", serif',
                                color: '#4a4a4a',
                                marginBottom: '4px'
                            }}>
                                {stoneData.names.ja}
                            </span>
                            <span style={{
                                fontSize: '11px',
                                fontFamily: '"Montserrat", sans-serif',
                                color: '#d4af37',
                                letterSpacing: '0.1em',
                                marginBottom: '16px'
                            }}>
                                {stoneData.names.en}
                            </span>

                            <Text style={{
                                color: 'rgba(74, 74, 74, 0.85)',
                                fontSize: '13px', lineHeight: 1.6,
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
