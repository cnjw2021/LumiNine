'use client';

import React, { useEffect, useState } from 'react';
import { Container, Tabs, Title, Text, Loader, Accordion, Box, Flex, Badge, Group } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import api from '@/utils/api';

// 星データの型定義
interface Star {
  star_number: number;
  name_jp: string;
  name_en: string;
  element: string;
  description: string;
  created_at: string;
  updated_at: string;
}

// 月命星データの型定義
interface MonthStarReading {
  star_number: number;
  title: string;
  keywords: string;
  description: string;
}

// 星のカラーマップ
const starColorMap: Record<number, string> = {
  1: 'blue',    // 一白水星
  2: 'dark',    // 二黒土星
  3: 'teal',    // 三碧木星
  4: 'green',   // 四緑木星
  5: 'yellow',  // 五黄土星
  6: 'orange',  // 六白金星
  7: 'red',     // 七赤金星
  8: 'brown',   // 八白土星
  9: 'grape',   // 九紫火星
};

const StarsDataDisplay: React.FC = () => {
  const [stars, setStars] = useState<Star[]>([]);
  const [monthStarReadings, setMonthStarReadings] = useState<MonthStarReading[]>([]);
  const [starsLoading, setStarsLoading] = useState(true);
  const [monthStarsLoading, setMonthStarsLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<string | null>('stars');
  const [error, setError] = useState<string | null>(null);

  // 星データの取得
  useEffect(() => {
    const fetchStarsData = async () => {
      try {
        setStarsLoading(true);
        const response = await api.get('/nine-star/stars');
        setStars(response.data.stars || []);
        setError(null);
      } catch (err) {
        console.error('星データの取得中にエラーが発生しました:', err);
        setError('星データの取得に失敗しました');
        notifications.show({
          title: 'エラー',
          message: '星データの取得に失敗しました',
          color: 'red',
        });
      } finally {
        setStarsLoading(false);
      }
    };

    fetchStarsData();
  }, []);

  // 月命星データの取得
  useEffect(() => {
    const fetchMonthStarReadings = async () => {
      try {
        setMonthStarsLoading(true);
        const response = await api.get('/nine-star/month-star-readings');
        setMonthStarReadings(response.data.readings || []);
        setError(null);
      } catch (err) {
        console.error('月命星データの取得中にエラーが発生しました:', err);
        setError('月命星データの取得に失敗しました');
        notifications.show({
          title: 'エラー',
          message: '月命星データの取得に失敗しました',
          color: 'red',
        });
      } finally {
        setMonthStarsLoading(false);
      }
    };

    fetchMonthStarReadings();
  }, []);

  // 星名から対応する月命星データを取得
  const getMonthStarReadingById = (starNumber: number) => {
    return monthStarReadings.find(reading => reading.star_number === starNumber);
  };

  return (
    <Container size="lg" py="xl">
      <Title order={2} ta="center" mb="xl">九星気学データ</Title>
      
      <Tabs value={activeTab} onChange={setActiveTab} mb="xl">
        <Tabs.List grow>
          <Tabs.Tab value="stars">本命星情報</Tabs.Tab>
          <Tabs.Tab value="month-stars">月命星情報</Tabs.Tab>
        </Tabs.List>

        <Tabs.Panel value="stars">
          {starsLoading ? (
            <Flex align="center" justify="center" h={200}>
              <Loader size="lg" />
            </Flex>
          ) : error ? (
            <Text color="red" ta="center" my="xl">{error}</Text>
          ) : (
            <Accordion multiple variant="separated" mt="md">
              {stars.map((star) => (
                <Accordion.Item value={star.star_number.toString()} key={star.star_number}>
                  <Accordion.Control>
                    <Group gap="xs">
                      <Badge size="lg" color={starColorMap[star.star_number] || 'gray'}>{star.star_number}</Badge>
                      <Text fw={500}>{star.name_jp}</Text>
                    </Group>
                  </Accordion.Control>
                  <Accordion.Panel>
                    <Text mb="md" style={{ whiteSpace: 'pre-wrap' }}>{star.description}</Text>
                  </Accordion.Panel>
                </Accordion.Item>
              ))}
            </Accordion>
          )}
        </Tabs.Panel>

        <Tabs.Panel value="month-stars">
          {monthStarsLoading ? (
            <Flex align="center" justify="center" h={200}>
              <Loader size="lg" />
            </Flex>
          ) : error ? (
            <Text color="red" ta="center" my="xl">{error}</Text>
          ) : (
            <Accordion multiple variant="separated" mt="md">
              {stars.map((star) => {
                const monthStarReading = getMonthStarReadingById(star.star_number);
                if (!monthStarReading) return null;
                
                return (
                  <Accordion.Item value={star.star_number.toString()} key={star.star_number}>
                    <Accordion.Control>
                      <Group gap="xs">
                        <Badge size="lg" color={starColorMap[star.star_number] || 'gray'}>{star.star_number}</Badge>
                        <Text fw={500}>{star.name_jp}</Text>
                      </Group>
                    </Accordion.Control>
                    <Accordion.Panel>
                      <Box mb="md">
                        <Text fw={700} mb="xs">キーワード</Text>
                        <Badge variant="dot" mb="md">{monthStarReading.keywords}</Badge>
                      </Box>
                      <Text style={{ whiteSpace: 'pre-wrap' }}>{monthStarReading.description}</Text>
                    </Accordion.Panel>
                  </Accordion.Item>
                );
              })}
            </Accordion>
          )}
        </Tabs.Panel>
      </Tabs>
    </Container>
  );
};

export default StarsDataDisplay; 