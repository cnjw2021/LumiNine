'use client';

import React, { useEffect, useState } from 'react';
import { Container, Title, Loader, Text, Center, Paper, Box, Group, Button, Flex, Badge } from '@mantine/core';
import { useNineStarKiStore } from '@/stores/nineStarKiStore';
import MainStarWithInfo from './MainStarWithInfo';
import api from '@/utils/api';

// 星の型定義
interface Star {
  id?: number;
  number: number;
  name_jp: string;
  name_en?: string;
  element?: string;
  description?: string;
  keywords?: string;
  title?: string;     // 特性タイトルを追加
  advice?: string;    // アドバイスを追加
}

// 月命星読みの型定義
interface MonthStarReading {
  id: number;
  star_number: number;
  title: string;
  keywords: string;
  description: string;
}

// 日命星読みの型定義
interface DailyStarReading {
  id: number;
  star_number: number;
  title: string;
  keywords: string | null;
  description: string;
  advice: string | null;
}

const MainStarInfoExample: React.FC = () => {
  const { result } = useNineStarKiStore();
  const [loading, setLoading] = useState(true);
  const [starData, setStarData] = useState<Star | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedStarNumber, setSelectedStarNumber] = useState<number | null>(null);
  const [, setMonthStarReading] = useState<MonthStarReading | null>(null);
  const [, setDailyStarReading] = useState<DailyStarReading | null>(null);
  const [starType, setStarType] = useState<'main' | 'month' | 'day'>('main');

  // カンマ区切りのキーワード文字列を処理する関数
  const processKeywords = (keywordsStr: string | null | undefined): string => {
    if (!keywordsStr) return '';
    // カンマと読点を「・」に置き換えて整形
    return keywordsStr.replace(/[,、]/g, '・').trim();
  };

  // 星選択ハンドラを拡張して月命星・日命星の読み情報も取得
  const handleStarSelect = async (starNumber: number, type: 'main' | 'month' | 'day' = 'main') => {
    setSelectedStarNumber(starNumber);
    setStarType(type);
    setLoading(true);
    try {
      // 基本星データを取得
      const response = await api.get(`/nine-star/stars?star_number=${starNumber}`);
      
      if (response.data && response.data.length > 0) {
        // 星データの基本情報をセット
        const baseStarData = {
          number: response.data[0].star_number,
          name_jp: response.data[0].name_jp,
          name_en: response.data[0].name_en,
          element: response.data[0].element,
          description: response.data[0].description,
          keywords: response.data[0].keywords
        };
        
        // 月命星の場合は月命星読みデータも取得
        if (type === 'month') {
          const monthReadingResponse = await api.get(`/nine-star/month-star-readings?star_number=${starNumber}`);
          if (monthReadingResponse.data && monthReadingResponse.data.length > 0) {
            setMonthStarReading(monthReadingResponse.data[0]);
            // 月命星読みで星データを更新
            setStarData({
              ...baseStarData,
              description: monthReadingResponse.data[0].description,
              keywords: processKeywords(monthReadingResponse.data[0].keywords),
              title: monthReadingResponse.data[0].title
            });
          } else {
            setStarData(baseStarData);
            setMonthStarReading(null);
          }
        } 
        // 日命星の場合はバックエンドから日命星読みデータを取得
        else if (type === 'day') {
          try {
            // サンプルの生年月日を作成（1990年1月1日）
            // 実際のアプリでは特定の誕生日に基づいて日命星読みを取得する
            const sampleBirthDate = '1990-01-01';
            
            // 日命星読みデータを取得
            const dailyStarResponse = await api.get(`/nine-star/daily-star-reading?birth_date=${sampleBirthDate}&override_star=${starNumber}`);
            
            if (dailyStarResponse.data && dailyStarResponse.data.day_reading) {
              const dayReading = dailyStarResponse.data.day_reading;
              setDailyStarReading(dayReading);
              
              // 日命星読みで星データを更新
              setStarData({
                ...baseStarData,
                description: dayReading.description,
                keywords: processKeywords(dayReading.keywords),
                title: dayReading.title,
                advice: dayReading.advice || ''
              });
            } else {
              console.warn('日命星読みデータが取得できませんでした。基本情報を表示します。');
              setStarData(baseStarData);
              setDailyStarReading(null);
            }
          } catch (error) {
            console.error('日命星読みデータの取得に失敗しました:', error);
            // APIからの取得に失敗した場合でも表示できるよう基本情報を使用
            setStarData(baseStarData);
            setDailyStarReading(null);
          }
        }
        // 本命星の場合は基本情報のみ
        else {
          setStarData(baseStarData);
          setMonthStarReading(null);
          setDailyStarReading(null);
        }
      } else {
        setError('スターデータが見つかりませんでした');
      }
    } catch (error) {
      console.error('スターデータの取得に失敗しました:', error);
      setError('スターデータの取得に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const fetchStarData = async () => {
      try {
        setLoading(true);
        
        // resultからmain_starが取得できる場合は直接使用
        if (result && result.main_star) {
          // 事前にStarオブジェクトを作成
          const initialStarData: Star = {
            number: result.main_star.star_number,
            name_jp: result.main_star.name_jp,
            name_en: result.main_star.name_en || '',
            element: result.main_star.element,
            keywords: processKeywords(result.main_star.keywords)
          };
          
          // 先に基本データをセット
          setStarData(initialStarData);
          setSelectedStarNumber(result.main_star.star_number);
          
          // 詳細説明を取得するためにAPI呼び出し
          const response = await api.get(`/nine-star/stars?star_number=${result.main_star.star_number}`);
          if (response.data && response.data.length > 0) {
            // 完全なオブジェクトとして更新
            setStarData({
              ...initialStarData,
              description: response.data[0].description,
              keywords: processKeywords(response.data[0].keywords || initialStarData.keywords)
            });
          }
        } 
        // resultがない場合はサンプルデータを表示（開発用）
        else {
          // 本命星のデータを取得（例として一白水星を使用）
          const sampleStarNum = 1;
          const response = await api.get(`/nine-star/stars?star_number=${sampleStarNum}`);
          
          if (response.data && response.data.length > 0) {
            const data = response.data[0];
            setStarData({
              id: data.id,
              number: data.star_number,
              name_jp: data.name_jp,
              name_en: data.name_en,
              element: data.element,
              description: data.description,
              keywords: processKeywords(data.keywords)
            });
            setSelectedStarNumber(sampleStarNum);
          } else {
            setError('星データが見つかりませんでした');
          }
        }
      } catch (err) {
        console.error('星データの取得中にエラーが発生しました:', err);
        setError('データの取得に失敗しました');
      } finally {
        setLoading(false);
      }
    };

    fetchStarData();
  }, [result]);

  if (loading) {
    return (
      <Center my="xl">
        <Loader size="md" />
      </Center>
    );
  }

  if (error) {
    return (
      <Paper shadow="sm" p="md" withBorder>
        <Text c="red" ta="center">{error}</Text>
      </Paper>
    );
  }

  // 星番号に基づいて色を返す関数
  const getStarColor = (starNumber: number): string => {
    const colors = [
      '#3490dc',  // 1: 一白水星
      '#2d3748',  // 2: 二黒土星
      '#38a169',  // 3: 三碧木星
      '#319795',  // 4: 四緑木星
      '#ecc94b',  // 5: 五黄土星
      '#a0aec0',  // 6: 六白金星
      '#e53e3e',  // 7: 七赤金星
      '#805ad5',  // 8: 八白土星
      '#ed64a6'   // 9: 九紫火星
    ];
    return colors[starNumber - 1] || '#3490dc';
  };

  return (
    <Container 
      fluid 
      p={0}
      m={0}
      style={{ 
        width: '100%', 
        maxWidth: '100%', 
        padding: 0,
        margin: 0
      }}
    >
      <Group 
        justify="center" 
        mb={{ base: 'xs', sm: 'md' }} 
        gap="xs" 
        style={{ padding: '0', flexDirection: 'column', alignItems: 'center' }}
      >
        <Title 
          order={2} 
          c="#4A5568"
          style={{ 
            fontSize: 'clamp(1.1rem, 3vw, 1.8rem)',
            padding: '8px 10px',
            textAlign: 'center',
            width: '100%',
            wordBreak: 'break-word',
            overflowWrap: 'break-word',
            whiteSpace: 'normal',
            lineHeight: 1.3,
            boxSizing: 'border-box'
          }}
        >
          鑑定結果
        </Title>
        
        {/* 選択された星の数字を大きく表示するセクション追加 */}
        {selectedStarNumber && (
          <Box 
            mb="md" 
            style={{ 
              width: '100%', 
              maxWidth: '320px',
              margin: '10px auto'
            }}
          >
            <Paper
              radius="md"
              p="md"
              bg={`${getStarColor(selectedStarNumber)}10`}
              style={{
                border: `2px solid ${getStarColor(selectedStarNumber)}70`,
                textAlign: 'center',
                position: 'relative',
                overflow: 'hidden'
              }}
            >
              <Flex align="center" justify="center" gap="lg">
                <Text
                  size="3rem"
                  fw={800}
                  c={getStarColor(selectedStarNumber)}
                  lh={1}
                  style={{
                    textShadow: '0px 2px 4px rgba(0,0,0,0.1)',
                    margin: 0
                  }}
                >
                  {selectedStarNumber}
                </Text>
                <Box>
                  <Text size="xs" fw={600} c="dimmed" mb={5}>
                    {starType === 'main' ? '本命星' : 
                     starType === 'month' ? '月命星' : '日命星'}
                  </Text>
                  <Badge
                    size="lg"
                    color={getStarColor(selectedStarNumber)}
                    radius="sm"
                    variant="filled"
                    style={{
                      fontWeight: 600,
                      fontSize: '0.8rem',
                      background: getStarColor(selectedStarNumber)
                    }}
                  >
                    {starData?.name_jp}
                  </Badge>
                </Box>
              </Flex>
            </Paper>
          </Box>
        )}
        
        {/* 星タイプの選択ボタン */}
        <Group gap="xs" mb="sm">
          <Button
            size="xs"
            variant={starType === 'main' ? 'filled' : 'outline'}
            color="blue"
            onClick={() => selectedStarNumber && handleStarSelect(selectedStarNumber, 'main')}
          >
            本命星
          </Button>
          <Button
            size="xs"
            variant={starType === 'month' ? 'filled' : 'outline'}
            color="cyan"
            onClick={() => selectedStarNumber && handleStarSelect(selectedStarNumber, 'month')}
          >
            月命星
          </Button>
          <Button
            size="xs"
            variant={starType === 'day' ? 'filled' : 'outline'}
            color="green"
            onClick={() => selectedStarNumber && handleStarSelect(selectedStarNumber, 'day')}
          >
            日命星
          </Button>
        </Group>

        {/* 星番号選択 */}
        <Group gap="xs">
          {[1, 2, 3, 4, 5, 6, 7, 8, 9].map((num) => (
            <Button
              key={num}
              size="xs"
              radius="xl"
              variant={selectedStarNumber === num ? "filled" : "outline"}
              color={getStarColor(num)}
              onClick={() => handleStarSelect(num, starType)}
              style={{ 
                minWidth: '28px',
                height: '28px',
                padding: '0',
                fontWeight: 'bold'
              }}
            >
              {num}
            </Button>
          ))}
        </Group>
      </Group>
      
      {starData && (
        <Box 
          p={0}
          style={{ 
            width: '100%', 
            padding: 0,
            margin: 0
          }}
        >
          <MainStarWithInfo 
            star={starData} 
            title={
              starType === 'main' ? "本命星（性格・運命の流れ）" :
              starType === 'month' ? "月命星（環境・対人関係）" :
              "日命星（行動・思考パターン）"
            }
            isMonthStar={starType === 'month'}
            isDayStar={starType === 'day'}
          />
        </Box>
      )}
    </Container>
  );
};

export default MainStarInfoExample; 