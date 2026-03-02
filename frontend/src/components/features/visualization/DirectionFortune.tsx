'use client';

import { Grid, Paper, Loader, Center, Card, Title, Text, Box } from '@mantine/core';
import { useDirectionFortuneData } from '@/hooks/useDirectionFortuneData';
import DirectionBoard from './DirectionBoard';
import AuspiciousDatesDisplay from './AuspiciousDatesDisplay';

interface DirectionFortuneProps {
  mainStar: number;
  monthStar: number;
  title: string;
  targetYear: number;
}

export default function DirectionFortune({ mainStar, monthStar, title, targetYear }: DirectionFortuneProps) {
    // 1. データロジックをフックから取得
    const {
        loading,
        directionFortuneStatus,
        yearlyStar,
        zodiac,
        springStartDate,
        springEndDate,
        movingDates,
        waterDrawingDates,
        movingTable,
        waterDrawingTable
    } = useDirectionFortuneData(mainStar, monthStar, targetYear);

    // ローディング中の表示
    if (loading) {
        return (
            <Center style={{ height: '400px' }}>
                <Loader />
            </Center>
        );
    }

    // 2. 取得したデータを各表示コンポーネントにpropsとして渡してレイアウト
    return (
        <Paper p={0} style={{ backgroundColor: 'transparent' }}>
            {/* 全体のタイトルを上部に配置 */}
            <Box mb="lg" ta="center">
                <Title order={2} mb="xs">{title}（{zodiac}） 場所の運気</Title>
                <Text size="sm" c="dimmed">
                    {springStartDate} {springEndDate && `〜 ${springEndDate}`}
                </Text>
            </Box>
            
            <Grid>
                <Grid.Col span={{ base: 12, md: 6 }}>
                    <DirectionBoard 
                        directionFortuneStatus={directionFortuneStatus}
                        yearlyStar={yearlyStar}
                        targetYear={targetYear}
                    />
                </Grid.Col>
                <Grid.Col span={{ base: 12, md: 6 }}>
                    <Card shadow="sm" p="lg" radius="md" withBorder style={{ height: '100%' }}>
                        <Title order={4} mb="md">方位運活用ガイド</Title>
                        <Text size="sm" c="dimmed" mb="lg">
                            引越し・就職・重要な買い物には吉方位と吉日を選ぶことで運気を最大化できます
                        </Text>
                        
                        <Box mb="md">
                            <Title order={5} mb="sm">方位運の活かし方</Title>
                            <Text size="sm" mb="xs">• 引越しや旅行は【吉方位】に向かって行うと成功率が高まります</Text>
                            <Text size="sm" mb="xs">• 重要な商談や契約は吉方位に向かって行うと成功率が高まります</Text>
                        </Box>
                        
                        <Box mb="md">
                            <Title order={5} mb="sm">避けるべき方位</Title>
                            <Box p="md" style={{ backgroundColor: '#fff5f5', border: '1px solid #fed7d7', borderRadius: '4px' }}>
                                <Text size="sm" c="red.7" fw={500}>
                                    【凶】方位への引越しや長期滞在は避けましょう。これらの方位は{targetYear}年のあなたにとって相性が良くありません。
                                </Text>
                            </Box>
                        </Box>
                        
                        <Text size="xs" c="dimmed" mt="lg">
                            ※ 実際にお引越しをされるときには、正確な方位を確認しますので必ずご相談ください。
                        </Text>
                    </Card>
                </Grid.Col>
                <Grid.Col span={{ base: 12, md: 6 }}>
                    <AuspiciousDatesDisplay 
                        title="引越し吉日"
                        description="引越しは運気に強く影響します。吉方位での引越しは良い準備が不可欠です。"
                        dates={movingDates}
                        tableData={movingTable}
                        icon="🏠"
                    />
                </Grid.Col>
                <Grid.Col span={{ base: 12, md: 6 }}>
                    <AuspiciousDatesDisplay 
                        title="お水取り吉日"
                        description="お水取りは金運や仕事運を上げる風水術。良い方位を選んで運気の流れを良くしましょう。"
                        dates={waterDrawingDates}
                        tableData={waterDrawingTable}
                        icon="💧"
                    />
                </Grid.Col>
            </Grid>
        </Paper>
    );
}