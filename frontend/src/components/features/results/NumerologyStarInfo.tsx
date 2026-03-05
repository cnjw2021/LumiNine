'use client';

import React from 'react';
import { Paper, Title, Box, Text, Card, Group, Badge, Stack, Divider } from '@mantine/core';
import { NumerologyResult } from '@/types/stars';

interface NumerologyStarInfoProps {
  numerology: NumerologyResult;
}

/**
 * 数秘術ライフパスナンバーの特性を表示するコンポーネント。
 */
const NumerologyStarInfo: React.FC<NumerologyStarInfoProps> = ({ numerology }) => {
  // 数秘術専用グラデーションカラー
  const primaryColor = '#667eea';
  const secondaryColor = '#764ba2';
  const gradient = `linear-gradient(135deg, ${primaryColor}15, ${secondaryColor}10, ${primaryColor}20)`;

  return (
    <Paper
      shadow="sm"
      p={0}
      radius="md"
      style={{
        background: 'linear-gradient(to bottom right, rgba(255,255,255,0.98), rgba(245,247,250,0.9))',
        backdropFilter: 'blur(12px)',
        border: '1px solid rgba(209, 213, 219, 0.5)',
        position: 'relative',
        width: '100%',
        margin: 0,
        padding: 0,
        boxSizing: 'border-box',
        overflow: 'hidden'
      }}
    >
      <Box style={{ position: 'relative', zIndex: 1, width: '100%', padding: 0 }}>
        {/* タイトル */}
        <Title
          order={2}
          mb={{ base: 'xs', sm: 'sm' }}
          ta="center"
          style={{
            color: '#2d3748',
            fontSize: 'clamp(0.9rem, 2.5vw, 1.4rem)',
            fontWeight: 700,
            letterSpacing: '0.01em',
            padding: '12px 16px',
            textAlign: 'center',
            width: '100%',
            wordBreak: 'break-word',
            overflowWrap: 'break-word',
            whiteSpace: 'normal',
            lineHeight: 1.4,
            boxSizing: 'border-box',
            hyphens: 'auto',
            borderBottom: '1px solid rgba(209, 213, 219, 0.8)'
          }}
        >
          🌟 数秘術<br />ライフパスナンバー
        </Title>

        {/* メインコンテンツエリア */}
        <Card
          shadow="xs"
          p="md"
          radius={0}
          style={{
            background: gradient,
            backdropFilter: 'blur(8px)',
            border: 0,
            borderTop: `1px solid ${primaryColor}20`,
            borderBottom: `1px solid ${primaryColor}20`,
            marginBottom: 0,
            width: '100%',
            padding: '16px'
          }}
        >
          <Stack gap="md" align="center">
            {/* ナンバーと惑星 */}
            <Group justify="center" align="center" gap="md">
              <Badge
                size="lg"
                radius="xl"
                variant="filled"
                style={{
                  fontSize: '1.8rem',
                  padding: '0.2rem 0.6rem',
                  fontWeight: 700,
                  boxShadow: `0 4px 12px ${primaryColor}40`,
                  height: '56px',
                  minWidth: '56px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: `linear-gradient(135deg, ${primaryColor} 0%, ${secondaryColor} 100%)`
                }}
              >
                {numerology.life_path_number}
              </Badge>

              <Badge
                size="lg"
                radius="md"
                variant="outline"
                style={{
                  padding: '0.25rem 0.8rem',
                  fontSize: '1rem',
                  fontWeight: 500,
                  border: `2px solid ${primaryColor}40`,
                  background: `${primaryColor}10`,
                  color: '#333'
                }}
              >
                支配惑星：{numerology.planet_name}（{numerology.planet.charAt(0).toUpperCase() + numerology.planet.slice(1)}）
              </Badge>
            </Group>

            {/* キーワードバッジ */}
            <Group gap="xs" style={{ flexWrap: 'wrap', justifyContent: 'center' }}>
              {numerology.keywords.map((kw, index) => (
                <Badge
                  key={index}
                  color={primaryColor}
                  size="md"
                  radius="sm"
                  variant="light"
                  style={{
                    fontSize: '0.75rem',
                    fontWeight: 500,
                    opacity: 0.95,
                    padding: '0.3rem 0.6rem',
                    margin: '0.15rem 0.1rem',
                    color: '#333',
                    backgroundColor: `${primaryColor}15`,
                    border: `1px solid ${primaryColor}30`
                  }}
                >
                  {kw}
                </Badge>
              ))}
            </Group>
          </Stack>
        </Card>

        {/* 特性説明セクション */}
        <Card
          shadow="md"
          p={{ base: 'md', sm: 'lg' }}
          radius={0}
          style={{
            background: gradient,
            border: 0,
            borderTop: `1px solid ${primaryColor}30`,
            boxShadow: `0 10px 20px -15px ${primaryColor}25`,
            position: 'relative',
            overflow: 'hidden',
            width: '100%',
            padding: '20px'
          }}
        >
          {/* 説明文 */}
          <Title order={3} mb="sm" style={{
            color: '#2d3748',
            borderBottom: `2px solid ${primaryColor}30`,
            paddingBottom: '10px',
            fontSize: 'clamp(1rem, 2.2vw, 1.2rem)',
            fontWeight: 600,
            letterSpacing: '0.02em',
            position: 'relative',
            zIndex: 1
          }}>
            ナンバー {numerology.life_path_number} の特性
          </Title>

          <Text
            size="sm"
            className="paragraph-text"
            style={{
              whiteSpace: 'pre-wrap',
              lineHeight: '1.8',
              color: '#2d3748',
              fontSize: 'clamp(0.9rem, 1.8vw, 1rem)',
              position: 'relative',
              zIndex: 1
            }}
          >
            {numerology.description}
          </Text>

          <Divider my="lg" />

          {/* 強み・弱み */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            {/* 強み */}
            <Card
              p="sm"
              radius="md"
              style={{
                backgroundColor: '#f0fff4',
                border: '1px solid #c6f6d5',
              }}
            >
              <Text fw={600} mb="xs" style={{ fontSize: '0.8rem', color: '#38a169' }}>
                ✦ 強み
              </Text>
              <ul style={{ margin: 0, padding: '0 0 0 16px', listStyleType: 'disc' }}>
                {numerology.strengths.map((s, i) => (
                  <li key={i} style={{ fontSize: '0.75rem', color: '#2f855a', lineHeight: 1.5 }}>{s}</li>
                ))}
              </ul>
            </Card>

            {/* 注意点 */}
            <Card
              p="sm"
              radius="md"
              style={{
                backgroundColor: '#fff5f5',
                border: '1px solid #fed7d7',
              }}
            >
              <Text fw={600} mb="xs" style={{ fontSize: '0.8rem', color: '#e53e3e' }}>
                ✦ 注意点
              </Text>
              <ul style={{ margin: 0, padding: '0 0 0 16px', listStyleType: 'disc' }}>
                {numerology.weaknesses.map((w, i) => (
                  <li key={i} style={{ fontSize: '0.75rem', color: '#c53030', lineHeight: 1.5 }}>{w}</li>
                ))}
              </ul>
            </Card>
          </div>
        </Card>
      </Box>
    </Paper>
  );
};

export default NumerologyStarInfo;
