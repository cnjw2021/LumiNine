'use client';

import React from 'react';
import { Title, Text, Card, SimpleGrid, Container, Group, Badge, Box } from '@mantine/core';
import { useAuth } from '@/contexts/auth/AuthContext';
import { IconUser } from '@tabler/icons-react';
import { COLORS, FONTS, CARD as CARD_TOKENS } from '@/utils/theme';

export default function AdminDashboard() {
  const { isAdmin, isSuperuser } = useAuth();

  const features = [
    {
      title: 'ユーザー管理',
      description: 'ユーザーの追加、編集、削除を行います',
      icon: IconUser,
      link: '/admin/users',
      superuserOnly: true
    }
  ];

  return (
    <Container size="lg" py="xl">
      <Title
        order={2}
        mb="md"
        c={COLORS.text}
        style={{ fontFamily: FONTS.title }}
      >
        管理者ダッシュボード
      </Title>

      <Box mb="xl">
        <Text mb="xs" c={COLORS.text}>ログイン情報:</Text>
        <Group>
          <Badge
            color={isAdmin ? 'yellow' : 'gray'}
            variant="light"
            style={{ borderColor: isAdmin ? COLORS.accent : undefined }}
          >
            管理者
          </Badge>
          <Badge
            color={isSuperuser ? 'yellow' : 'gray'}
            variant="light"
            style={{ borderColor: isSuperuser ? COLORS.accent : undefined }}
          >
            スーパーユーザー
          </Badge>
        </Group>
      </Box>

      <Text mb="lg" c={COLORS.text}>以下のメニューから管理機能에 アクセスできます：</Text>

      <SimpleGrid
        cols={{ base: 1, xs: 1, sm: 2, md: 2, lg: 3 }}
        spacing="lg"
      >
        {features
          .filter(feature => !feature.superuserOnly || isSuperuser)
          .map((feature) => (
            <Card
              key={feature.title}
              shadow="none"
              p="lg"
              radius={CARD_TOKENS.borderRadius}
              component="a"
              href={feature.link}
              style={{
                textDecoration: 'none',
                color: 'inherit',
                backgroundColor: COLORS.cardBg,
                border: CARD_TOKENS.border,
                boxShadow: CARD_TOKENS.boxShadow,
                transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                cursor: 'pointer',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: '0 10px 30px -5px rgba(212, 175, 55, 0.1)'
                }
              }}
            >
              <Group mb="md">
                <feature.icon size={24} color={COLORS.accent} />
                <Title order={4} size="h4" style={{ fontFamily: FONTS.title, color: COLORS.text }}>
                  {feature.title}
                </Title>
              </Group>
              <Text size="sm" c={COLORS.textDimmed}>
                {feature.description}
              </Text>
            </Card>
          ))}
      </SimpleGrid>
    </Container>
  );
}