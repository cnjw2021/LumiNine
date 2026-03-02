'use client';

import { Box, Badge, Tooltip, Card, Text, Title } from '@mantine/core';
import Image from 'next/image';
import { DirectionFortuneStatus, DirectionStatus } from '@/types/directionFortune';

interface DirectionDisplayProps {
  direction: string;
  status: DirectionStatus;
  position: { top: string; left: string };
}

interface DirectionBoardProps {
  directionFortuneStatus: DirectionFortuneStatus | null;
  yearlyStar: number | null;
  targetYear: number;
}

const DirectionDisplay = ({ status, position }: DirectionDisplayProps) => {
    const isAuspicious = status.is_auspicious === true;
    const isInauspicious = status.is_auspicious === false;

    return (
        <Box style={{ ...position, position: 'absolute', width: '16%', height: '16%', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 6 }}>
            {isAuspicious && (
                <Badge size="md" color="green">
                    {/* {status.compatibility_level === "BEST" ? "大吉" : status.compatibility_level === "BETTER" ? "中吉" : "小吉"} */}
                    吉
                </Badge>
            )}
            {isInauspicious && (
                <Tooltip label={(status.reason || "凶方位").split(',').join('\n')} position="top" withArrow multiline w={150}>
                    <Badge size="md" color="red">凶</Badge>
                </Tooltip>
            )}
        </Box>
    );
};

export default function DirectionBoard({ directionFortuneStatus, yearlyStar, targetYear }: DirectionBoardProps) {
    const starToUse = yearlyStar || 0;
    const chartPath = `/images/main_star/${starToUse}.svg`;
    
    // 各方位のスタイルを定義
    const positions: { [key: string]: { top: string; left: string } } = {
        south: { top: 'calc(50% - 62% - 8%)', left: 'calc(50% - 8%)' },
        north: { top: 'calc(50% + 62% - 8%)', left: 'calc(50% - 8%)' },
        east: { top: 'calc(50% - 8%)', left: 'calc(50% - 62% - 8%)' },
        west: { top: 'calc(50% - 8%)', left: 'calc(50% + 62% - 8%)' },
        southeast: { top: 'calc(50% - 43% - 8%)', left: 'calc(50% - 43% - 8%)' },
        southwest: { top: 'calc(50% - 43% - 8%)', left: 'calc(50% + 43% - 8%)' },
        northeast: { top: 'calc(50% + 43% - 8%)', left: 'calc(50% - 43% - 8%)' },
        northwest: { top: 'calc(50% + 43% - 8%)', left: 'calc(50% + 43% - 8%)' },
    };

    return (
        <Card shadow="sm" p="lg" radius="md" withBorder>
            {/* 九星盤のタイトル */}
            <Title order={4} ta="center" mb="md">方位の吉凶</Title>
            
            <Box style={{ width: '100%', maxWidth: '400px', position: 'relative', aspectRatio: '1/1', margin: 'auto' }}>
                <Image src={chartPath} alt={`${yearlyStar}年の九星盤`} fill style={{ objectFit: 'contain' }} priority />
                {directionFortuneStatus && (
                    <Box style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' }}>
                        <Box style={{ width: '80%', height: '80%', position: 'relative', margin: '10%' }}>
                            {Object.entries(directionFortuneStatus).map(([direction, status]) => (
                                <DirectionDisplay key={direction} direction={direction} status={status} position={positions[direction] || { top: '0%', left: '0%' }} />
                            ))}
                        </Box>
                    </Box>
                )}
            </Box>
            
            {/* 九星盤の下の説明文 */}
            <Text size="sm" c="dimmed" ta="center" mt="md" style={{ lineHeight: '1.6' }}>
                中央の星は{targetYear}年の年盤星。方位ごとの「吉」「凶」表示を参考に、運気を高める行動方向を選びましょう。
            </Text>
        </Card>
    );
}