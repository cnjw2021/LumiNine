'use client';

import React, { useEffect, useState } from 'react';
import { Container, Title, Text, Paper, Divider, Group, Stack, Badge, Button, Loader, Center } from '@mantine/core';
import { useRouter } from 'next/navigation';
import { IconHeart, IconHeartBroken, IconChevronLeft } from '@tabler/icons-react';

// ローカルストレージキー
const COMPATIBILITY_STORAGE_KEY = 'ninestarki-compatibility-result-data';

// 相性鑑定結果の型
interface CompatibilityResult {
  main_star: number;
  target_star: number;
  main_birth_month: number;
  target_birth_month: number;
  is_male: boolean;
  symbols: string;
  pattern_code: string;
  readings: {
    [theme: string]: {
      id: number;
      pattern_code: string;
      theme: string;
      title: string;
      content: string;
      created_at: string;
      updated_at: string;
    }
  };
}

interface PersonInfo {
  name: string;
  star: {
    star_number: number;
    star_name: string;
    star_element: string;
    star_kanji: string;
    star_attribute: string;
  };
  birthdate: string;
}

interface CompatibilityData {
  result: CompatibilityResult;
  mainPerson: PersonInfo;
  targetPerson: PersonInfo;
  gender: 'male' | 'female';
}

const CompatibilityResultPage: React.FC = () => {
  const [compatibilityData, setCompatibilityData] = useState<CompatibilityData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();

  useEffect(() => {
    try {
      // ローカルストレージからデータを取得
      const storedData = localStorage.getItem(COMPATIBILITY_STORAGE_KEY);
      if (!storedData) {
        setError('相性鑑定結果が見つかりません。もう一度鑑定してください。');
        setLoading(false);
        return;
      }

      const parsedData = JSON.parse(storedData) as CompatibilityData;
      setCompatibilityData(parsedData);
      setLoading(false);
    } catch (err) {
      console.error('結果データの読み込みエラー:', err);
      setError('結果データの読み込み中にエラーが発生しました。');
      setLoading(false);
    }
  }, []);

  const handleBackToForm = () => {
    router.push('/');
  };

  // シンボルに基づく相性レベルを取得する関数
  const getCompatibilityLevel = (symbols: string): { level: string; color: string; icon: React.ReactNode } => {
    if (symbols.includes('★')) {
      return { 
        level: '最高', 
        color: 'pink', 
        icon: <IconHeart size={16} style={{ color: '#FF2D55' }} />
      };
    } else if (symbols.includes('○') || symbols.includes('◎')) {
      return { 
        level: '良好', 
        color: 'green', 
        icon: <IconHeart size={16} style={{ color: '#4CD964' }} />
      };
    } else if (symbols.includes('Ｐ') || symbols.includes('Ｆ')) {
      return { 
        level: '普通', 
        color: 'blue', 
        icon: <IconHeart size={16} style={{ color: '#007AFF' }} />
      };
    } else if (symbols.includes('Ｎ')) {
      return { 
        level: '普通', 
        color: 'yellow', 
        icon: <IconHeart size={16} style={{ color: '#FFCC00' }} />
      };
    } else {
      return { 
        level: '注意', 
        color: 'red', 
        icon: <IconHeartBroken size={16} style={{ color: '#FF3B30' }} />
      };
    }
  };

  if (loading) {
    return (
      <Container size="sm" p="md">
        <Center style={{ height: '80vh' }}>
          <Stack align="center" gap="md">
            <Loader size="lg" color="#4BA3E3" />
            <Text>鑑定結果を読み込んでいます...</Text>
          </Stack>
        </Center>
      </Container>
    );
  }

  if (error) {
    return (
      <Container size="sm" p="md">
        <Paper shadow="md" p="xl" radius="md" withBorder>
          <Stack align="center" gap="md">
            <Title order={2} ta="center" c="red">エラーが発生しました</Title>
            <Text ta="center">{error}</Text>
            <Button 
              leftSection={<IconChevronLeft size={16} />}
              variant="light" 
              color="blue" 
              onClick={handleBackToForm}
            >
              入力フォームに戻る
            </Button>
          </Stack>
        </Paper>
      </Container>
    );
  }

  if (!compatibilityData) {
    return (
      <Container size="sm" p="md">
        <Paper shadow="md" p="xl" radius="md" withBorder>
          <Stack align="center" gap="md">
            <Title order={2} ta="center">データが見つかりません</Title>
            <Text ta="center">相性鑑定結果が見つかりません。もう一度鑑定してください。</Text>
            <Button 
              leftSection={<IconChevronLeft size={16} />}
              variant="light" 
              color="blue" 
              onClick={handleBackToForm}
            >
              入力フォームに戻る
            </Button>
          </Stack>
        </Paper>
      </Container>
    );
  }

  const { result, mainPerson, targetPerson } = compatibilityData;
  const compatibilityLevel = getCompatibilityLevel(result.symbols);

  return (
    <Container size="md" p={{ base: 'xs', sm: 'md' }}>
      <Stack gap="lg">
        <Button 
          leftSection={<IconChevronLeft size={16} />}
          variant="light" 
          color="blue" 
          onClick={handleBackToForm}
          mb="md"
        >
          入力フォームに戻る
        </Button>

        <Paper shadow="md" p={{ base: 'md', sm: 'xl' }} radius="md" withBorder>
          <Stack gap="md">
            <Title order={1} ta="center" size="h2" c="#4BA3E3">相性鑑定結果</Title>
            
            <Group justify="center" gap="xs">
              <Badge size="xl" color={compatibilityLevel.color} variant="light" leftSection={compatibilityLevel.icon}>
                相性レベル：{compatibilityLevel.level}
              </Badge>
            </Group>
            
            {result.readings && Object.keys(result.readings).length > 0 ? (
              <Stack gap="md">
                {/* テーマ名とその内容を表示 */}
                {Object.entries(result.readings).map(([theme, reading]) => {
                  // テーマの日本語名を取得
                  const themeLabel = {
                    'energy': '関係のエネルギー強度',
                    'emotional': '感情面・精神面の調和',
                    'challenge': '課題と学びの可能性',
                    'relationship_type': '適した関係性',
                    'stability': '長期的な安定性'
                  }[theme] || theme;
                  
                  return (
                    <Paper key={theme} p="md" radius="md" bg="#f8f9fa" withBorder>
                      <Title order={3} size="h4" c="#4BA3E3" mb="sm">{themeLabel}</Title>
                      <Text style={{ whiteSpace: 'pre-wrap' }}>{reading.content}</Text>
                    </Paper>
                  );
                })}
              </Stack>
            ) : (
              <Paper p="md" radius="md" bg="#f8f9fa" withBorder>
                <Text ta="center">鑑定結果が見つかりません。</Text>
              </Paper>
            )}
            
            <Divider my="md" />
            
            <Group justify="apart" wrap="nowrap" align="flex-start">
              <Stack gap="xs" style={{ flex: 1 }}>
                <Title order={3} size="h5">{mainPerson.name}</Title>
                <Text size="sm">生年月日: {mainPerson.birthdate}</Text>
                <Paper p="sm" radius="md" withBorder bg="#f1f3f5">
                  <Stack gap={5}>
                    <Text fw={700}>{mainPerson.star.star_kanji}（{mainPerson.star.star_number}番）</Text>
                    <Text size="sm">五行: {mainPerson.star.star_element}</Text>
                    <Text size="sm">特性: {mainPerson.star.star_attribute}</Text>
                  </Stack>
                </Paper>
              </Stack>
              
              <div style={{ display: 'flex', alignItems: 'center', padding: '0 1rem' }}>
                <Text fw={700} size="xl">×</Text>
              </div>
              
              <Stack gap="xs" style={{ flex: 1 }}>
                <Title order={3} size="h5">{targetPerson.name}</Title>
                <Text size="sm">生年月日: {targetPerson.birthdate}</Text>
                <Paper p="sm" radius="md" withBorder bg="#f1f3f5">
                  <Stack gap={5}>
                    <Text fw={700}>{targetPerson.star.star_kanji}（{targetPerson.star.star_number}番）</Text>
                    <Text size="sm">五行: {targetPerson.star.star_element}</Text>
                    <Text size="sm">特性: {targetPerson.star.star_attribute}</Text>
                  </Stack>
                </Paper>
              </Stack>
            </Group>
            
            <Divider my="md" />
            
            <Stack gap="xs">
              <Text size="sm" c="dimmed">相性記号: {result.symbols}</Text>
              <Text size="sm" c="dimmed">パターンコード: {result.pattern_code}</Text>
            </Stack>
          </Stack>
        </Paper>
      </Stack>
    </Container>
  );
};

export default CompatibilityResultPage; 