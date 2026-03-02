'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useState, useEffect, useCallback } from 'react';
import { Button, Table, TextInput, Group, Text, Paper, Checkbox } from '@mantine/core';
import { notifications } from '@mantine/notifications';

type SolarStartsData = {
  id: number;
  year: number;
  datetime: string;
  created_at: string;
  updated_at: string;
};

export default function SolarStartsDataPage() {
  const [data, setData] = useState<SolarStartsData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showTimestamps, setShowTimestamps] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/admin/solar-starts', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!response.ok) {
        throw new Error('データの取得に失敗しました');
      }
      const data = await response.json();
      setData(data);
      setError(null);
    } catch (error) {
      setError(error instanceof Error ? error.message : '不明なエラーが発生しました');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleEdit = (id: number) => {
    setEditingId(id);
  };

  const handleSave = async (id: number) => {
    try {
      const itemToUpdate = data.find(item => item.id === id);
      if (!itemToUpdate) return;

      const token = localStorage.getItem('token');
      const response = await fetch(`/api/admin/solar-starts/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(itemToUpdate),
      });

      if (!response.ok) throw new Error('データの更新に失敗しました');
      
      setEditingId(null);
      notifications.show({
        title: '成功',
        message: 'データを更新しました',
        color: 'green',
      });
      setError(null);
    } catch (error) {
      setError(error instanceof Error ? error.message : '不明なエラーが発生しました');
      notifications.show({
        title: 'エラー',
        message: error instanceof Error ? error.message : '不明なエラーが発生しました',
        color: 'red',
      });
    }
  };

  const handleCancel = () => {
    setEditingId(null);
  };

  const handleChange = (id: number, field: keyof SolarStartsData, value: string | number) => {
    setData(prevData =>
      prevData.map(item =>
        item.id === id ? { ...item, [field]: value } : item
      )
    );
  };

  return (
    <div className="container mx-auto py-10">
      <Card className="shadow-lg">
        <CardHeader className="bg-gray-50">
          <CardTitle>立春データ管理</CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          {error && (
            <Paper p="md" mb="md" withBorder radius="md" style={{ backgroundColor: '#FEE2E2', borderColor: '#F87171' }}>
              <Text c="red" fw={500}>エラー: {error}</Text>
            </Paper>
          )}
          
          <Group justify="flex-end" mb="md">
            <Checkbox
              label="作成日時・更新日時を表示"
              checked={showTimestamps}
              onChange={(event) => setShowTimestamps(event.currentTarget.checked)}
            />
          </Group>
          
          {isLoading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
          ) : (
            <Table striped highlightOnHover withTableBorder withColumnBorders>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th style={{ textAlign: 'center' }}>ID</Table.Th>
                  <Table.Th style={{ textAlign: 'center' }}>年</Table.Th>
                  <Table.Th style={{ textAlign: 'center' }}>日付</Table.Th>
                  {showTimestamps && (
                    <>
                      <Table.Th style={{ textAlign: 'center' }}>作成日時</Table.Th>
                      <Table.Th style={{ textAlign: 'center' }}>更新日時</Table.Th>
                    </>
                  )}
                  <Table.Th style={{ textAlign: 'center' }}>操作</Table.Th>
                </Table.Tr>
              </Table.Thead>
              <Table.Tbody>
                {data.map((item) => (
                  <Table.Tr key={item.id}>
                    <Table.Td style={{ textAlign: 'center' }}>{item.id}</Table.Td>
                    <Table.Td style={{ textAlign: 'center' }}>
                      {editingId === item.id ? (
                        <TextInput
                          type="number"
                          value={item.year}
                          style={{ maxWidth: '100px', margin: '0 auto' }}
                          onChange={(e) => handleChange(item.id, 'year', parseInt(e.target.value))}
                        />
                      ) : (
                        item.year
                      )}
                    </Table.Td>
                    <Table.Td style={{ textAlign: 'center' }}>
                      {editingId === item.id ? (
                        <TextInput
                          value={item.datetime}
                          style={{ maxWidth: '150px', margin: '0 auto' }}
                          onChange={(e) => handleChange(item.id, 'datetime', e.target.value)}
                        />
                      ) : (
                        item.datetime
                      )}
                    </Table.Td>
                    {showTimestamps && (
                      <>
                        <Table.Td style={{ textAlign: 'center' }}>{item.created_at}</Table.Td>
                        <Table.Td style={{ textAlign: 'center' }}>{item.updated_at}</Table.Td>
                      </>
                    )}
                    <Table.Td style={{ textAlign: 'center' }}>
                      {editingId === item.id ? (
                        <Group gap="xs" justify="center">
                          <Button size="xs" color="green" onClick={() => handleSave(item.id)}>保存</Button>
                          <Button size="xs" color="gray" onClick={handleCancel}>キャンセル</Button>
                        </Group>
                      ) : (
                        <Button size="xs" onClick={() => handleEdit(item.id)}>編集</Button>
                      )}
                    </Table.Td>
                  </Table.Tr>
                ))}
              </Table.Tbody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  );
} 