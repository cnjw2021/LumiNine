'use client';

import React from 'react';
import MovingAuspiciousDatesManager from '@/components/admin/MovingAuspiciousDatesManager';
import { Container, Title, Paper, Text, Box } from '@mantine/core';

export default function MovingDatesPage() {
  return (
    <Container size="lg" py="xl">
      <Title order={2} mb="lg">引っ越し吉日管理</Title>
      
      <Paper shadow="xs" p="xl" withBorder mb="xl">
        <Text mb="md">
          ここでは引っ越しに適した日を管理することができます。九星気学に基づく吉日情報を年度ごとに登録・編集できます。
        </Text>
      </Paper>
      
      <Box>
        <MovingAuspiciousDatesManager />
      </Box>
    </Container>
  );
} 