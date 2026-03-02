'use client';

import { Card, Title, Text, Box, Table } from '@mantine/core';
import { MovingDateInfo, WaterDrawingDateInfo, AuspiciousTableData } from '@/types/directionFortune';
import { groupDatesByMonthAndDirection, formatDays, formatWaterDays, MonthGroup, MonthDirectionGroup } from '@/utils/auspiciousTable';

interface AuspiciousDatesDisplayProps {
    title: string;
    description: string;
    dates: (MovingDateInfo | WaterDrawingDateInfo)[];
    tableData?: AuspiciousTableData;
    icon?: string;  // アイコンフロパティを追加
}

export default function AuspiciousDatesDisplay({ title, description, dates, tableData, icon }: AuspiciousDatesDisplayProps) {
    const directionOrder = ["東", "西", "南", "北", "北東", "北西", "南東", "南西"];

    const groupedDates = groupDatesByMonthAndDirection(dates, directionOrder);
    const hasTableData = Boolean(tableData && tableData.length > 0);

    return (
        <Card shadow="sm" p="lg" radius="md" withBorder style={{ height: '100%' }}>
            {/* 引越し吉日のタイトルと説明 */}
                            <Box style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '15px' }}>
                    {icon ? (
                        <span style={{ fontSize: '18px' }}>{icon}</span>
                    ) : (
                    <Box style={{ 
                        width: 10, 
                        height: 20, 
                        borderRadius: '50%', 
                        backgroundColor: title === "お水取り吉日" ? '#74b9ff' : '#82c91e' 
                    }} />
                )}
                <Title order={4} mb={0}>{title}</Title>
            </Box>
            
            <Text size="sm" mb={15}>
                {description}
            </Text>
            
            {/* 引越し吉日用の緑色背景の文言 */}
            {title === "引越し吉日" && (
                <Box mb={15} p={10} style={{ backgroundColor: 'rgba(40, 167, 69, 0.1)', borderRadius: '4px' }}>
                    <Text size="sm" fw={500} c="green.7">
                        この方位に引越しができると、南東：家庭運・人気運がスピーディーに上がります。
                    </Text>
                </Box>
            )}
            
            <Box>
                {hasTableData ? (
                    tableData!.map((yearData, index) => (
                        <Box key={yearData.year}>
                            <Box
                                mb="xs"
                                p={6}
                                style={{
                                    backgroundColor: '#f8f9fa',
                                    borderRadius: '4px',
                                    marginTop: index === 0 ? 0 : '8px'
                                }}
                            >
                                <Text size="sm" fw={600} ta="center">{yearData.year}年</Text>
                            </Box>
                            <Table
                                withTableBorder
                                withColumnBorders
                                highlightOnHover
                                style={{ tableLayout: 'fixed', width: '100%' }}
                            >
                                <Table.Thead style={{ backgroundColor: '#f8f9fa' }}>
                                    <Table.Tr>
                                        <Table.Th style={{ textAlign: 'center', padding: '3px 6px', width: 52 }}>月</Table.Th>
                                        {yearData.headers.map((dir) => (
                                            <Table.Th key={dir} style={{ textAlign: 'center', padding: '3px 6px' }}>{dir}</Table.Th>
                                        ))}
                                    </Table.Tr>
                                </Table.Thead>
                                <Table.Tbody>
                                    {yearData.rows.map((row) => (
                                        <Table.Tr key={`${yearData.year}-${row.month}`}>
                                            <Table.Td style={{ textAlign: 'center', padding: '3px 6px', width: 52 }}>{row.month}月</Table.Td>
                                            {yearData.headers.map((dir) => (
                                                <Table.Td
                                                    key={`${row.month}-${dir}`}
                                                    style={{ padding: '3px 6px', whiteSpace: 'normal', wordBreak: 'keep-all', textAlign: 'center' }}
                                                >
                                                    <Text size="sm">{row.cells[dir] || ''}</Text>
                                                </Table.Td>
                                            ))}
                                        </Table.Tr>
                                    ))}
                                </Table.Tbody>
                            </Table>
                        </Box>
                    ))
                ) : groupedDates.length > 0 ? (
                    (() => {
                        const yearGroups = new Map<number, MonthGroup[]>();
                        groupedDates.forEach((group) => {
                            if (!yearGroups.has(group.year)) {
                                yearGroups.set(group.year, []);
                            }
                            yearGroups.get(group.year)!.push(group);
                        });
                        const sortedYears = Array.from(yearGroups.keys()).sort();

                        return sortedYears.map((year) => {
                            const months = yearGroups.get(year)!;
                            const yearDirections: string[] = [];
                            months.forEach((monthGroup) => {
                                monthGroup.directions.forEach((dirGroup) => {
                                    if (!yearDirections.includes(dirGroup.direction)) {
                                        yearDirections.push(dirGroup.direction);
                                    }
                                });
                            });
                            const orderedYearDirections = directionOrder.filter((dir) => yearDirections.includes(dir));
                            yearDirections
                                .filter((dir) => !orderedYearDirections.includes(dir))
                                .sort()
                                .forEach((dir) => orderedYearDirections.push(dir));

                            return (
                            <Box key={year}>
                                <Box
                                    mb="xs"
                                    p="xs"
                                    style={{
                                        backgroundColor: '#f8f9fa',
                                        borderRadius: '4px',
                                        marginTop: year === sortedYears[0] ? 0 : '8px'
                                    }}
                                >
                                    <Text size="sm" fw={600} ta="center">{year}年</Text>
                                </Box>
                                <Table
                                    withTableBorder
                                    withColumnBorders
                                    highlightOnHover
                                    style={{ tableLayout: 'fixed', width: '100%' }}
                                >
                                    <Table.Thead style={{ backgroundColor: '#f8f9fa' }}>
                                        <Table.Tr>
                                            <Table.Th style={{ textAlign: 'center', padding: '3px 6px', width: 52 }}>月</Table.Th>
                                            {orderedYearDirections.map((dir) => (
                                                <Table.Th key={dir} style={{ textAlign: 'center', padding: '3px 6px' }}>{dir}</Table.Th>
                                            ))}
                                        </Table.Tr>
                                    </Table.Thead>
                                    <Table.Tbody>
                                        {months.map((monthGroup: MonthGroup) => {
                                            const directionMap = new Map<string, (MovingDateInfo | WaterDrawingDateInfo)[]>();
                                            monthGroup.directions.forEach((dirGroup: MonthDirectionGroup) => {
                                                directionMap.set(dirGroup.direction, dirGroup.dates);
                                            });
                                            return (
                                                <Table.Tr key={`${monthGroup.year}-${monthGroup.month}`}>
                                                    <Table.Td style={{ textAlign: 'center', padding: '3px 6px', width: 52 }}>{monthGroup.month}月</Table.Td>
                                                    {orderedYearDirections.map((dir) => {
                                                        const items = directionMap.get(dir) || [];
                                                        const text = title === "引越し吉日"
                                                            ? formatDays(items)
                                                            : formatWaterDays(items);
                                                        return (
                                                            <Table.Td
                                                                key={`${monthGroup.month}-${dir}`}
                                                                style={{ padding: '3px 6px', whiteSpace: 'normal', wordBreak: 'keep-all', textAlign: 'center' }}
                                                            >
                                                                <Text size="sm">{text}</Text>
                                                            </Table.Td>
                                                        );
                                                    })}
                                                </Table.Tr>
                                            );
                                        })}
                                    </Table.Tbody>
                                </Table>
                            </Box>
                        );
                        });
                    })()
                ) : (
                    <Text size="sm" c="dimmed" ta="center">データがありません</Text>
                )}
            </Box>
        </Card>
    );
}