'use client';

import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';

type NineStarData = {
  id: number;
  star_number: number;
  name: string;
  element: string;
  created_at: string;
  updated_at: string;
};

export function NineStarDataTable() {
  const [data, setData] = useState<NineStarData[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

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
      setSuccessMessage('データを更新しました');
      setTimeout(() => setSuccessMessage(null), 3000);
      setError(null);
    } catch (error) {
      setError(error instanceof Error ? error.message : '不明なエラーが発生しました');
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

  if (isLoading) {
    return <div className="flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
    </div>;
  }

  return (
    <Card className="shadow-sm border-0">
      <CardContent className="p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">九星データ</h2>
          <Button
            onClick={fetchData}
            disabled={isLoading}
            className="bg-blue-500 hover:bg-blue-600"
          >
            {isLoading ? 'Loading...' : '更新'}
          </Button>
        </div>
        
        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded-md mb-4">
            {error}
          </div>
        )}
        
        {successMessage && (
          <div className="bg-green-50 text-green-600 p-3 rounded-md mb-4">
            {successMessage}
          </div>
        )}
        
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-gray-100">
                <th className="font-bold text-center px-4 py-3 border-b-2 border-gray-300">ID</th>
                <th className="font-bold text-center px-4 py-3 border-b-2 border-gray-300">番号</th>
                <th className="font-bold text-center px-4 py-3 border-b-2 border-gray-300">名前</th>
                <th className="font-bold text-center px-4 py-3 border-b-2 border-gray-300">五行</th>
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
                        value={item.star_number.toString()}
                        className="max-w-[80px] mx-auto"
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
                          handleChange(item.id, 'star_number', parseInt(e.target.value, 10))
                        }
                      />
                    ) : (
                      item.star_number
                    )}
                  </td>
                  <td className="text-center px-4 py-3 border-b border-gray-200">
                    {editingId === item.id ? (
                      <Input
                        value={item.name}
                        className="max-w-[150px] mx-auto"
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
                          handleChange(item.id, 'name', e.target.value)
                        }
                      />
                    ) : (
                      item.name
                    )}
                  </td>
                  <td className="text-center px-4 py-3 border-b border-gray-200">
                    {editingId === item.id ? (
                      <Input
                        value={item.element}
                        className="max-w-[80px] mx-auto"
                        onChange={(e: React.ChangeEvent<HTMLInputElement>) => 
                          handleChange(item.id, 'element', e.target.value)
                        }
                      />
                    ) : (
                      item.element
                    )}
                  </td>
                  <td className="text-center px-4 py-3 border-b border-gray-200">
                    {new Date(item.created_at).toLocaleString('ja-JP')}
                  </td>
                  <td className="text-center px-4 py-3 border-b border-gray-200">
                    {new Date(item.updated_at).toLocaleString('ja-JP')}
                  </td>
                  <td className="text-center px-4 py-3 border-b border-gray-200">
                    {editingId === item.id ? (
                      <div className="flex justify-center space-x-2">
                        <Button
                          onClick={() => handleSave(item.id)}
                          className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 text-xs"
                        >
                          保存
                        </Button>
                        <Button
                          onClick={handleCancel}
                          className="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 text-xs"
                        >
                          キャンセル
                        </Button>
                      </div>
                    ) : (
                      <Button
                        onClick={() => handleEdit(item.id)}
                        className="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 text-xs"
                      >
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