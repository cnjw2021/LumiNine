"use client";

import React from "react";
import { Stack, Text } from "@mantine/core";
import rawNumerologyTraits from "@/data/numerology_traits.json";

interface NumerologyData {
    title: string;
    traits: string;
}

const numerologyTraits = rawNumerologyTraits as Record<string, NumerologyData>;

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

                <div style={{ marginBottom: '40px' }}>
                    <p style={{
                        color: 'rgba(74, 74, 74, 0.85)',
                        fontSize: '15px', lineHeight: 2.0,
                        fontFamily: '"Noto Serif JP", serif',
                        margin: 0, marginBottom: '24px',
                        textAlign: 'center'
                    }}>
                        数秘術（Numerology）は、生年月日や姓名から導き出される数字を用いて、個人の性格、才能、運命などを読み解く占術です。
                    </p>
                    <p style={{
                        color: 'rgba(74, 74, 74, 0.85)',
                        fontSize: '15px', lineHeight: 2.0,
                        fontFamily: '"Noto Serif JP", serif',
                        margin: 0,
                        textAlign: 'center'
                    }}>
                        以下は、1から9までの基本ナンバーと、11, 22, 33からなるマスターナンバーの性質です。
                    </p>
                </div>

                <Stack gap="xl" style={{ marginTop: '16px' }}>
                    {Object.entries(numerologyTraits).map(([num, data], index, array) => (
                        <div key={num} style={{
                            display: 'flex',
                            flexDirection: 'column',
                            paddingBottom: index === array.length - 1 ? '0' : '32px',
                            borderBottom: index === array.length - 1 ? 'none' : '1px solid rgba(212, 175, 55, 0.15)',
                        }}>
                            <div style={{
                                display: 'flex',
                                alignItems: 'center',
                                gap: '16px',
                                marginBottom: '16px',
                            }}>
                                <span style={{
                                    fontSize: '36px', fontWeight: 700,
                                    fontFamily: '"Noto Serif JP", serif',
                                    color: '#d8a7a7', lineHeight: 1,
                                    width: '40px', textAlign: 'center'
                                }}>
                                    {num}
                                </span>
                                <div style={{ width: '1px', height: '28px', backgroundColor: 'rgba(212, 175, 55, 0.3)' }} />
                                <span style={{
                                    fontSize: '17px', fontWeight: 600,
                                    fontFamily: '"Shippori Mincho", "Noto Serif JP", serif',
                                    color: '#4a4a4a', letterSpacing: '0.05em'
                                }}>
                                    {data.title}
                                </span>
                            </div>

                            <Text style={{
                                color: 'rgba(74, 74, 74, 0.85)',
                                fontSize: '14px', lineHeight: 1.8,
                                fontFamily: '"Noto Serif JP", serif',
                                margin: 0,
                                whiteSpace: 'pre-line'
                            }}>
                                {data.traits}
                            </Text>
                        </div>
                    ))}
                </Stack>

            </main>
        </div>
    );
}
