'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useState, useEffect, useCallback } from 'react';
import { Button, Table, TextInput, Group, Text, Paper, Checkbox } from '@mantine/core';
import { notifications } from '@mantine/notifications';

type NineStarData = {
  id: number;
  star_number: number;
  name: string;
  element: string;
  created_at: string;
  updated_at: string;
};

export default function NineStarDataPage() {
  const [data, setData] = useState<NineStarData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showTimestamps, setShowTimestamps] = useState(false);

  const fetchData = useCallback(async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('/api/admin/stars', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!response.ok) {
        throw new Error('データの取得に失敗しました');
      }
      const json = await response.json();
      setData(json.stars || []);
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
      const response = await fetch(`/api/admin/stars/${id}`, {
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

  const handleChange = (id: number, field: keyof NineStarData, value: string | number) => {
    setData(prevData =>
      prevData.map(item =>
        item.id === id ? { ...item, [field]: value } : item
      )
    );
  };

  return (
    <div className="container mx-auto py-6">
      <Card className="w-full mb-6">
        <CardHeader>
          <CardTitle>九星データ管理</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-4 flex justify-between items-center">
            <Button onClick={fetchData} loading={isLoading}>更新</Button>
            <Checkbox 
              label="タイムスタンプを表示" 
              checked={showTimestamps} 
              onChange={(event) => setShowTimestamps(event.currentTarget.checked)} 
            />
          </div>
          
          {error && (
            <Paper p="md" mb="md" withBorder style={{ backgroundColor: 'rgba(255, 0, 0, 0.1)' }}>
              <Text c="red">{error}</Text>
            </Paper>
          )}
          
          {isLoading ? (
            <div className="flex justify-center items-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            </div>
          ) : (
            <Table striped highlightOnHover withTableBorder withColumnBorders>
              <Table.Thead>
                <Table.Tr>
                  <Table.Th style={{ textAlign: 'center' }}>ID</Table.Th>
                  <Table.Th style={{ textAlign: 'center' }}>番号</Table.Th>
                  <Table.Th style={{ textAlign: 'center' }}>名前</Table.Th>
                  <Table.Th style={{ textAlign: 'center' }}>五行</Table.Th>
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
                          value={item.star_number}
                          type="number"
                          style={{ maxWidth: '80px', margin: '0 auto' }}
                          onChange={(e) => handleChange(item.id, 'star_number', parseInt(e.target.value, 10))}
                        />
                      ) : (
                        item.star_number
                      )}
                    </Table.Td>
                    <Table.Td style={{ textAlign: 'center' }}>
                      {editingId === item.id ? (
                        <TextInput
                          value={item.name}
                          style={{ maxWidth: '150px', margin: '0 auto' }}
                          onChange={(e) => handleChange(item.id, 'name', e.target.value)}
                        />
                      ) : (
                        item.name
                      )}
                    </Table.Td>
                    <Table.Td style={{ textAlign: 'center' }}>
                      {editingId === item.id ? (
                        <TextInput
                          value={item.element}
                          style={{ maxWidth: '80px', margin: '0 auto' }}
                          onChange={(e) => handleChange(item.id, 'element', e.target.value)}
                        />
                      ) : (
                        item.element
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