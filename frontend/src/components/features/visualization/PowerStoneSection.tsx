'use client';

import React from 'react';
import { Paper, Loader, Center, Text } from '@mantine/core';
import { usePowerStoneData } from '@/hooks/usePowerStoneData';
import PowerStoneCard from './PowerStoneCard';

/**
 * パワーストーン推薦セクション — 完全独立コンポーネント。
 *
 * DirectionFortune とは分離されており、
 * ResultFortuneSection や任意のページで自由に配置・表示制御が可能。
 *
 * birthDate を渡すと 6~7-Layer 応答を取得しリッチなカードを表示する。
 * targetYear を追加で渡すと yearly(年運石) を含む 7-Layer になる。
 */
interface PowerStoneSectionProps {
    mainStar: number;
    monthStar: number;
    targetYear?: number;
    birthDate?: string;
}

const PowerStoneSection: React.FC<PowerStoneSectionProps> = ({ mainStar, monthStar, targetYear, birthDate }) => {
    const { loading, powerStones, error } = usePowerStoneData(mainStar, monthStar, targetYear, birthDate);

    if (loading) {
        return (
            <Paper shadow="xs" p="md" withBorder radius="md">
                <Center py="md">
                    <Loader size="sm" />
                    <Text size="sm" c="dimmed" ml="sm">パワーストーンを読み込み中...</Text>
                </Center>
            </Paper>
        );
    }

    if (error || !powerStones) {
        return null; // エラーやデータなしの場合は何も表示しない
    }

    return <PowerStoneCard powerStones={powerStones} targetYear={targetYear} />;
};

export default PowerStoneSection;
