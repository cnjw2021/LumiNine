"use client";

import React from "react";
import { Container, Title, Text, Stack, Card } from "@mantine/core";

export default function NumerologyPage() {
    return (
        <div style={{
            minHeight: '100vh',
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
            <main style={{ maxWidth: '800px', margin: '0 auto', padding: '80px 20px', position: 'relative', zIndex: 10, width: '100%' }}>

                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', marginBottom: '48px' }}>
                    <h1 style={{
                        fontSize: 'clamp(24px, 5vw, 32px)', fontWeight: 'normal', color: '#4a4a4a',
                        fontFamily: '"Shippori Mincho", "Noto Serif JP", serif',
                        letterSpacing: '0.05em', margin: 0
                    }}>
                        数秘術について
                    </h1>
                    <div style={{ width: '60px', height: '1px', background: 'linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.6), transparent)' }} />
                    <h3 style={{
                        color: '#d4af37', fontSize: '12px', letterSpacing: '0.3em',
                        fontWeight: 500, textTransform: 'uppercase',
                        fontFamily: '"Montserrat", sans-serif', margin: 0, marginTop: '8px'
                    }}>
                        Numerology
                    </h3>
                </div>

                <div style={{
                    backgroundColor: '#ffffff',
                    borderRadius: '24px',
                    padding: '48px 40px',
                    boxShadow: '0 10px 40px -10px rgba(0, 0, 0, 0.05)',
                    border: '1px solid rgba(212, 175, 55, 0.1)',
                }}>
                    <p style={{
                        color: 'rgba(74, 74, 74, 0.85)',
                        fontSize: '15px', lineHeight: 2.0,
                        fontFamily: '"Noto Serif JP", serif',
                        margin: 0, marginBottom: '24px',
                        textAlign: 'center'
                    }}>
                        数秘術（Numerology）は、生年月日や姓名から導き出される数字を用いて、個人の性格、才能、運命などを読み解く占術です。
                    </p>
                    <div style={{ width: '40px', height: '1px', backgroundColor: 'rgba(212, 175, 55, 0.3)', margin: '0 auto 24px auto' }} />
                    <p style={{
                        color: 'rgba(74, 74, 74, 0.85)',
                        fontSize: '15px', lineHeight: 2.0,
                        fontFamily: '"Noto Serif JP", serif',
                        margin: 0,
                        textAlign: 'center'
                    }}>
                        LumiNineでは、生年月日からライフパスナンバーなどの重要な数字を計算し、あなたに最適なパワーストーンやアドバイスを提供します。
                    </p>
                </div>

            </main>
        </div>
    );
}
