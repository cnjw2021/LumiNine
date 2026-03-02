import React, { useState } from 'react';
import { Button, Card, Text, Group, Alert, Table, Paper, Title, Badge, Loader, NumberInput, Stack } from '@mantine/core';
import axios from 'axios';
import { AxiosError } from 'axios';

interface DailyAstrologyData {
  id: number;
  date: string;
  zodiac: string;
  star_number: number;
}

const ManageDailyAstrology: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{
    status: 'success' | 'error';
    message: string;
  } | null>(null);
  const [debugInfo, setDebugInfo] = useState<string>('');
  const [astrologyData, setAstrologyData] = useState<DailyAstrologyData[]>([]);
  const [dataLoading, setDataLoading] = useState(false);
  const [startYear, setStartYear] = useState<number | null>(null);
  const [endYear, setEndYear] = useState<number | null>(null);
  const [searchYear, setSearchYear] = useState<number>(new Date().getFullYear());

  const starNames = [
    '一白水星', '二黒土星', '三碧木星', '四緑木星', '五黄土星',
    '六白金星', '七赤金星', '八白土星', '九紫火星'
  ];

  const handleInitialize = async () => {
    if (!startYear || !endYear || startYear > endYear) {
      alert('開始年と終了年を正しく入力してください');
      return;
    }
    
    if (startYear < 1900 || endYear > 2052) {
      alert('初期化できる年度は1900年から2052年までです');
      return;
    }

    if (!window.confirm(`${startYear}年から${endYear}年のデータを初期化しますか？\n既存のデータは削除されます。`)) {
      return;
    }

    setLoading(true);
    setResult(null);
    setDebugInfo('');
    setAstrologyData([]);

    try {
      // axiosを直接使用してトークンを手動で設定
      const token = localStorage.getItem('token');
      setDebugInfo(`使用するトークン: ${token ? token.substring(0, 10) + '...' : 'なし'}`);

      const response = await axios.post(`/api/admin/initialize-astrology-data/${startYear}/${endYear}`, {}, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      setResult({
        status: 'success',
        message: response.data.message || '初期化が完了しました',
      });
      setDebugInfo(prevDebug => `${prevDebug}\n応答ステータス: ${response.status}\n応答データ: ${JSON.stringify(response.data)}`);

      // 初期化成功後、データを取得
      fetchAstrologyData();
    } catch (error) {
      const axiosError = error as AxiosError<{ message: string }>;
      setResult({
        status: 'error',
        message: axiosError.response?.data?.message || '初期化中にエラーが発生しました',
      });
      
      // 詳細なエラー情報を記録
      let errorDetails = `エラーステータス: ${axiosError.response?.status || 'なし'}\n`;
      errorDetails += `エラーメッセージ: ${axiosError.message}\n`;
      if (axiosError.response?.data) {
        errorDetails += `応答データ: ${JSON.stringify(axiosError.response.data)}\n`;
      }
      setDebugInfo(prevDebug => `${prevDebug}\n${errorDetails}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchAstrologyData = async (year = startYear) => {
    setDataLoading(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/admin/daily-astrology', {
        params: {
          year: year,
          limit: 365
        },
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      setAstrologyData(response.data || []);
    } catch (error) {
      console.error('データの取得に失敗しました:', error);
    } finally {
      setDataLoading(false);
    }
  };

  // 日付をフォーマットする関数
  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ja-JP', { year: 'numeric', month: '2-digit', day: '2-digit' });
  };

  return (
    <Card shadow="sm" padding="lg" radius="md" withBorder>
      <Card.Section withBorder inheritPadding py="xs">
        <Text fw={500} size="lg">干支・九星データ初期化</Text>
      </Card.Section>

      <Text size="sm" c="dimmed" mt="md" mb="md">
        指定した年の干支と九星のデータを初期化します。
        既存のデータは削除されます。
      </Text>

      {/* データ検索セクション */}
      <Card withBorder mb="lg">
        <Card.Section withBorder inheritPadding py="xs" bg="blue.1">
          <Text fw={500} size="md">データ検索</Text>
        </Card.Section>
        <Card.Section withBorder p="md">
          <Group align="flex-end">
            <NumberInput
              label="検索年度"
              value={searchYear}
              onChange={(value: number | string) => typeof value === 'number' && setSearchYear(value)}
              min={1900}
              max={2052}
              required
            />
            <Button
              variant="outline"
              color="blue"
              onClick={() => {
                void fetchAstrologyData(searchYear);
              }}
              loading={dataLoading}
            >
              データを検索
            </Button>
          </Group>
          <Text size="xs" c="dimmed" mt="xs">
            ※既に登録されている年度のデータを検索します
          </Text>
        </Card.Section>
      </Card>

      {/* データ初期化セクション */}
      <Card withBorder mb="lg">
        <Card.Section withBorder inheritPadding py="xs" bg="red.1">
          <Text fw={500} size="md">データ初期化</Text>
        </Card.Section>
        <Card.Section withBorder p="md">
          <Stack mb="md">
            <Group align="flex-end">
              <NumberInput
                label="開始年"
                value={startYear || undefined}
                onChange={(value: number | string) => typeof value === 'number' && setStartYear(value)}
                min={1900}
                max={2052}
                placeholder="開始年を入力"
                required
              />
              <NumberInput
                label="終了年"
                value={endYear || undefined}
                onChange={(value: number | string) => typeof value === 'number' && setEndYear(value)}
                min={1900}
                max={2052}
                placeholder="終了年を入力"
                required
              />
            </Group>
            <Text size="xs" c="dimmed">
              ※複数年を指定する場合は、開始年と終了年を入力してください。
              年数が多いと処理に時間がかかります。
            </Text>
            <Text size="xs" c="dimmed">
              ※初期化できる年度は1900年から2052年までです。
            </Text>
          </Stack>
        </Card.Section>
      </Card>

      <Group mt="md">
        <Button
          variant="filled"
          color="blue"
          onClick={handleInitialize}
          loading={loading}
          disabled={!startYear || !endYear || startYear > endYear}
        >
          {loading ? '初期化中...' : 'データを初期化'}
        </Button>
        
        {result?.status === 'success' && !dataLoading && astrologyData.length === 0 && (
          <Button variant="outline" color="green" onClick={() => void fetchAstrologyData()}>
            データを表示
          </Button>
        )}
      </Group>

      {result && (
        <Alert color={result.status === 'success' ? 'teal' : 'red'} mt="md">
          {result.message}
        </Alert>
      )}

      {debugInfo && (
        <Alert color="blue" mt="md" withCloseButton={false} title="デバッグ情報">
          <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
            {debugInfo}
          </pre>
        </Alert>
      )}
      
      {dataLoading ? (
        <Group justify="center" mt="xl">
          <Loader />
          <Text>データを読み込み中...</Text>
        </Group>
      ) : astrologyData.length > 0 && (
        <Paper mt="xl" p="md" withBorder>
          <Title order={4} mb="md">{astrologyData[0] ? new Date(astrologyData[0].date).getFullYear() : searchYear}年データ（全{astrologyData.length}日分）</Title>
          
          <Group grow align="flex-start">
            {/* 1〜6月のデータ */}
            <div>
              <Title order={5} mb="sm" ta="center">1月〜6月</Title>
              <Table striped highlightOnHover withTableBorder withColumnBorders>
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th style={{ textAlign: 'center' }}>日付</Table.Th>
                    <Table.Th style={{ textAlign: 'center' }}>干支</Table.Th>
                    <Table.Th style={{ textAlign: 'center' }}>九星</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {astrologyData
                    .filter(item => {
                      const date = new Date(item.date);
                      const month = date.getMonth() + 1; // getMonth()は0から始まるので+1
                      return month >= 1 && month <= 6;
                    })
                    .map((item) => (
                      <Table.Tr key={item.id}>
                        <Table.Td style={{ textAlign: 'center' }}>{formatDate(item.date)}</Table.Td>
                        <Table.Td style={{ textAlign: 'center' }}>{item.zodiac}</Table.Td>
                        <Table.Td style={{ textAlign: 'center' }}>
                          <Badge color={getStarColor(item.star_number)} size="lg">
                            {item.star_number}. {starNames[item.star_number - 1]}
                          </Badge>
                        </Table.Td>
                      </Table.Tr>
                    ))}
                </Table.Tbody>
              </Table>
            </div>

            {/* 7〜12月のデータ */}
            <div>
              <Title order={5} mb="sm" ta="center">7月〜12月</Title>
              <Table striped highlightOnHover withTableBorder withColumnBorders>
                <Table.Thead>
                  <Table.Tr>
                    <Table.Th style={{ textAlign: 'center' }}>日付</Table.Th>
                    <Table.Th style={{ textAlign: 'center' }}>干支</Table.Th>
                    <Table.Th style={{ textAlign: 'center' }}>九星</Table.Th>
                  </Table.Tr>
                </Table.Thead>
                <Table.Tbody>
                  {astrologyData
                    .filter(item => {
                      const date = new Date(item.date);
                      const month = date.getMonth() + 1;
                      return month >= 7 && month <= 12;
                    })
                    .map((item) => (
                      <Table.Tr key={item.id}>
                        <Table.Td style={{ textAlign: 'center' }}>{formatDate(item.date)}</Table.Td>
                        <Table.Td style={{ textAlign: 'center' }}>{item.zodiac}</Table.Td>
                        <Table.Td style={{ textAlign: 'center' }}>
                          <Badge color={getStarColor(item.star_number)} size="lg">
                            {item.star_number}. {starNames[item.star_number - 1]}
                          </Badge>
                        </Table.Td>
                      </Table.Tr>
                    ))}
                </Table.Tbody>
              </Table>
            </div>
          </Group>
        </Paper>
      )}
    </Card>
  );
};

// 星番号に基づいて色を返す関数
function getStarColor(starNumber: number): string {
  const colors = [
    'blue', // 1: 一白水星
    'dark',  // 2: 二黒土星
    'green', // 3: 三碧木星
    'teal',  // 4: 四緑木星
    'yellow', // 5: 五黄土星
    'gray',  // 6: 六白金星
    'red',   // 7: 七赤金星
    'violet', // 8: 八白土星
    'pink'   // 9: 九紫火星
  ];
  return colors[starNumber - 1] || 'blue';
}

export default ManageDailyAstrology; 