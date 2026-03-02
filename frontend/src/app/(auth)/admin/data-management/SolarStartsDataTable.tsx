'use client';

import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useToast } from '@/components/ui/use-toast';
import { Card, CardContent } from '@/components/ui/card';

type SolarStartData = {
  id: number;
  year: number;
  datetime: string;
  created_at: string;
  updated_at: string;
};

export function SolarStartsDataTable() {
  const [data, setData] = useState<SolarStartData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const { toast } = useToast();

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
    } catch (error) {
      toast({
        title: 'エラー',
        description: error instanceof Error ? error.message : '不明なエラーが発生しました',
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  }, [toast]);

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
      toast({
        title: '成功',
        description: 'データを更新しました',
      });
    } catch (error) {
      toast({
        title: 'エラー',
        description: error instanceof Error ? error.message : '不明なエラーが発生しました',
        variant: 'destructive',
      });
    }
  };

  const handleCancel = () => {
    setEditingId(null);
  };

  const handleChange = (id: number, field: keyof SolarStartData, value: string | number) => {
    setData(prevData =>
      prevData.map(item =>
        item.id === id ? { ...item, [field]: value } : item
      )
    );
  };

  if (isLoading) {
    return <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
    </div>;
  }

  return (
    <Card className="shadow-md">
      <CardContent className="p-6">
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-gray-100">
                <th className="font-bold text-center px-4 py-3 border-b-2 border-gray-300">ID</th>
                <th className="font-bold text-center px-4 py-3 border-b-2 border-gray-300">年</th>
                <th className="font-bold text-center px-4 py-3 border-b-2 border-gray-300">立春日時</th>
                <th className="font-bold text-center px-4 py-3 border-b-2 border-gray-300">作成日時</th>
                <th className="font-bold text-center px-4 py-3 border-b-2 border-gray-300">更新日時</th>
                <th className="font-bold text-center px-4 py-3 border-b-2 border-gray-300">操作</th>
              </tr>
            </thead>
            <tbody>
              {data.map((item) => (
                <tr key={item.id} className={item.id % 2 === 0 ? "bg-gray-50" : "bg-white"}>
                  <td className="text-center px-4 py-3 border-b border-gray-200">{item.id}</td>
                  <td className="text-center px-4 py-3 border-b border-gray-200">
                    {editingId === item.id ? (
                      <Input
                        type="number"
                        value={item.year}
                        className="max-w-[100px] mx-auto"
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange(item.id, 'year', parseInt(e.target.value))}
                      />
                    ) : (
                      item.year
                    )}
                  </td>
                  <td className="text-center px-4 py-3 border-b border-gray-200">
                    {editingId === item.id ? (
                      <Input
                        type="datetime-local"
                        value={item.datetime.slice(0, 16)}
                        className="max-w-[200px] mx-auto"
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange(item.id, 'datetime', e.target.value)}
                      />
                    ) : (
                      new Date(item.datetime).toLocaleString('ja-JP')
                    )}
                  </td>
                  <td className="text-center px-4 py-3 border-b border-gray-200">{new Date(item.created_at).toLocaleString('ja-JP')}</td>
                  <td className="text-center px-4 py-3 border-b border-gray-200">{new Date(item.updated_at).toLocaleString('ja-JP')}</td>
                  <td className="text-center px-4 py-3 border-b border-gray-200">
                    {editingId === item.id ? (
                      <div className="flex justify-center space-x-2">
                        <Button size="sm" className="bg-green-600 hover:bg-green-700" onClick={() => handleSave(item.id)}>保存</Button>
                        <Button size="sm" variant="outline" onClick={handleCancel}>キャンセル</Button>
                      </div>
                    ) : (
                      <Button size="sm" variant="outline" className="hover:bg-blue-50" onClick={() => handleEdit(item.id)}>
                        編集
                      </Button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </CardContent>
    </Card>
  );
} 