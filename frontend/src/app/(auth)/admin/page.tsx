'use client';

import React from 'react';
import { Title, Text, Card, SimpleGrid, Container, Group, Badge, Box } from '@mantine/core';
import { useAuth } from '@/contexts/auth/AuthContext';
import { IconUser, IconDatabase, IconServer, IconCalendar, IconDownload } from '@tabler/icons-react';

export default function AdminDashboard() {
  const { isAdmin, isSuperuser } = useAuth();

  const features = [
    {
      title: 'ユーザー管理',
      description: 'ユーザーの追加、編集、削除を行います',
      icon: IconUser,
      link: '/admin/users',
      color: 'blue',
      superuserOnly: true
    },
    {
      title: '九星データ管理',
      description: '九星気学データの管理を行います',
      icon: IconDatabase,
      link: '/admin/nine-star',
      color: 'green',
      superuserOnly: false
    },
    {
      title: 'SVG九星盤ダウンロード',
      description: '高品質なSVG形式の九星盤を生成・ダウンロードできます',
      icon: IconDownload,
      link: '/admin/svg-kyusei',
      color: 'violet',
      superuserOnly: true
    },
    {
      title: '引っ越し吉日管理',
      description: '引っ越しに良い日の情報を管理します',
      icon: IconCalendar,
      link: '/admin/moving-dates',
      color: 'cyan',
      superuserOnly: false
    },
    {
      title: '年単位の干支・九星データ初期化',
      description: '指定年の全日付について、干支と九星のデータを初期化します',
      icon: IconCalendar,
      link: '/admin/initialize-astrology',
      color: 'grape',
      superuserOnly: false
    },
    {
      title: 'SQLファイル実行',
      description: 'SQLファイルの実行を行います',
      icon: IconServer,
      link: '/admin/sql-execution',
      color: 'orange',
      superuserOnly: false
    },
    {
      title: 'テーブル管理',
      description: 'データベーステーブルの管理を行います',
      icon: IconDatabase,
      link: '/admin/table-management',
      color: 'red',
      superuserOnly: false
    }
  ];

  return (
    <Container size="lg" py="xl">
      <Title order={2} mb="md">管理者ダッシュボード</Title>
      
      <Box mb="xl">
        <Text mb="xs">ログイン情報:</Text>
        <Group>
          <Badge color={isAdmin ? 'pink' : 'gray'}>管理者</Badge>
          <Badge color={isSuperuser ? 'pink' : 'gray'}>スーパーユーザー</Badge>
        </Group>
      </Box>
      
      <Text mb="lg">以下のメニューから管理機能にアクセスできます：</Text>
      
      <SimpleGrid 
        cols={{ base: 1, xs: 1, sm: 2, md: 2, lg: 3 }} 
        spacing="lg"
      >
        {features
          .filter(feature => !feature.superuserOnly || isSuperuser)
          .map((feature) => (
            <Card 
              key={feature.title} 
              shadow="sm" 
              p="lg"
              radius="md" 
              withBorder
              component="a"
              href={feature.link}
              style={{ 
                textDecoration: 'none', 
                color: 'inherit',
                transition: 'transform 0.2s ease, box-shadow 0.2s ease',
                cursor: 'pointer',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: '0 10px 20px rgba(0, 0, 0, 0.1)'
                }
              }}
            >
              <Group mb="md">
                <feature.icon size={24} color={`var(--mantine-color-${feature.color}-6)`} />
                <Title order={4} size="h4">{feature.title}</Title>
              </Group>
              <Text size="sm" c="dimmed" style={{ 
                fontSize: 'var(--mantine-font-size-sm)',
                '@media (minWidth: 48em)': {
                  fontSize: 'var(--mantine-font-size-md)'
                }
              }}>
                {feature.description}
              </Text>
            </Card>
          ))}
      </SimpleGrid>
    </Container>
  );
} 