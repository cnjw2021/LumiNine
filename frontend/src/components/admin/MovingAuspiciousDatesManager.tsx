import React, { useState, useEffect, useCallback } from 'react';
import { 
  Table, 
  Button, 
  TextInput, 
  Modal, 
  Group, 
  Text, 
  ActionIcon, 
  Select, 
  Box,
  Paper,
  Textarea,
  Alert,
  Stack,
  Checkbox
} from '@mantine/core';
import { IconPlus, IconEdit, IconTrash, IconUpload, IconTrashX } from '@tabler/icons-react';
import { useDisclosure } from '@mantine/hooks';

// シンプルな型定義
interface MovingDate {
  id?: number;
  year: number;
  date: Date | string;
  description: string;
  direction?: string;
}

// 現在の年度を取得（4月始まり）
const getCurrentYear = (): number => {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth() + 1;
  return month >= 4 ? year : year - 1;
};

// 年度選択用のデータ作成
const getYearOptions = (): { value: string; label: string }[] => {
  const currentYear = getCurrentYear();
  return Array.from({ length: 10 }, (_, i) => currentYear - 4 + i).map(year => ({
    value: year.toString(),
    label: `${year}年度`
  }));
};

// 日付をフォーマット
const formatDate = (date: Date | string): string => {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleDateString('ja-JP', { year: 'numeric', month: 'long', day: 'numeric' });
};

// 月・日のオプション生成用関数
const getMonthOptions = (): { value: string; label: string }[] => {
  return Array.from({ length: 12 }, (_, i) => i + 1).map(month => ({
    value: month.toString(),
    label: `${month}月`
  }));
};

const getDayOptions = (year: number, month: number): { value: string; label: string }[] => {
  // 月の最終日を取得
  const lastDay = new Date(year, month, 0).getDate();
  return Array.from({ length: lastDay }, (_, i) => i + 1).map(day => ({
    value: day.toString(),
    label: `${day}日`
  }));
};

const MovingAuspiciousDatesManager: React.FC = () => {
  // 状態管理
  const [dates, setDates] = useState<MovingDate[]>([]);
  const [loading, setLoading] = useState(true);
  const [startYear, setStartYear] = useState(getCurrentYear().toString());
  const [endYear, setEndYear] = useState(getCurrentYear().toString());
  const [year, setYear] = useState(getCurrentYear().toString()); // 一括追加用
  const [selectedDate, setSelectedDate] = useState<MovingDate | null>(null);
  
  // チェックボックス用の状態
  const [selectedItems, setSelectedItems] = useState<number[]>([]);
  const [selectAll, setSelectAll] = useState(false);
  
  // 日付選択用の状態
  const [selectedYear, setSelectedYear] = useState<string>(new Date().getFullYear().toString());
  const [selectedMonth, setSelectedMonth] = useState<string>((new Date().getMonth() + 1).toString());
  const [selectedDay, setSelectedDay] = useState<string>(new Date().getDate().toString());
  const [description, setDescription] = useState('');
  const [direction, setDirection] = useState('');
  
  // 一括追加用の状態
  const [bulkDates, setBulkDates] = useState<string>('');
  const [bulkDescription, setBulkDescription] = useState<string>('');
  const [bulkDirection, setBulkDirection] = useState<string>('');
  const [bulkAddResult, setBulkAddResult] = useState<{
    success: number, 
    errors: string[], 
    deletedCount?: number
  }>({success: 0, errors: [], deletedCount: 0});
  
  // モーダル制御
  const [addModalOpened, { open: openAddModal, close: closeAddModal }] = useDisclosure(false);
  const [editModalOpened, { open: openEditModal, close: closeEditModal }] = useDisclosure(false);
  const [deleteModalOpened, { open: openDeleteModal, close: closeDeleteModal }] = useDisclosure(false);
  const [bulkAddModalOpened, { open: openBulkAddModal, close: closeBulkAddModal }] = useDisclosure(false);

  // データ取得
  const fetchDates = useCallback(async () => {
    setLoading(true);
    // チェックボックスの選択状態をリセット
    setSelectedItems([]);
    setSelectAll(false);
    
    try {
      // 認証トークンの取得
      const token = localStorage.getItem('token');
      
      // 範囲検索のクエリパラメータを構築
      const yearQuery = startYear === endYear 
        ? `year=${startYear}` 
        : `start_year=${startYear}&end_year=${endYear}`;
      
      // 実際のAPIを呼び出す
      const response = await fetch(`/api/moving-dates?${yearQuery}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('データの取得に失敗しました');
      }
      
      const data = await response.json();
      setDates(data);
    } catch (error) {
      console.error('Error fetching data:', error);
      // エラー時は空の配列にする
      setDates([]);
    } finally {
      setLoading(false);
    }
  }, [startYear, endYear, setDates, setLoading, setSelectedItems, setSelectAll]);

  // 年度変更時に再取得
  useEffect(() => {
    fetchDates();
  }, [fetchDates]);

  // 編集ダイアログを開く
  const handleEdit = (date: MovingDate) => {
    setSelectedDate(date);
    const dateObj = new Date(date.date);
    setSelectedYear(dateObj.getFullYear().toString());
    setSelectedMonth((dateObj.getMonth() + 1).toString());
    setSelectedDay(dateObj.getDate().toString());
    setDescription(date.description);
    setDirection(date.direction || '');
    openEditModal();
  };

  // 削除ダイアログを開く
  const handleDelete = (date: MovingDate) => {
    setSelectedDate(date);
    openDeleteModal();
  };

  // 追加ダイアログを開く
  const handleAdd = () => {
    const today = new Date();
    setSelectedYear(today.getFullYear().toString());
    setSelectedMonth((today.getMonth() + 1).toString());
    setSelectedDay(today.getDate().toString());
    setDescription('');
    setDirection('');
    openAddModal();
  };
  
  // 一括追加ダイアログを開く
  const handleBulkAdd = () => {
    setBulkDates('');
    setBulkDescription('');
    setBulkDirection('');
    setBulkAddResult({success: 0, errors: [], deletedCount: 0});
    openBulkAddModal();
  };

  // モーダルを閉じる処理
  const handleCloseBulkAddModal = () => {
    // モーダルを閉じる前に結果表示をリセット
    setBulkAddResult({success: 0, errors: [], deletedCount: 0});
    closeBulkAddModal();
  };

  // 現在選択されている日付を生成
  const getCurrentSelectedDate = (): Date => {
    return new Date(
      parseInt(selectedYear),
      parseInt(selectedMonth) - 1,
      parseInt(selectedDay)
    );
  };
  
  // 日付をYYYY-MM-DD形式に変換（タイムゾーン考慮）
  const formatDateForAPI = (date: Date): string => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  // 追加処理
  const handleSaveNew = async () => {
    const newDate = getCurrentSelectedDate();
    
    const dateData = {
      year: Number(year),
      date: formatDateForAPI(newDate), // タイムゾーンを考慮した形式に変換
      description: description,
      direction: direction
    };
    
    try {
      // 認証トークンの取得
      const token = localStorage.getItem('token');
      
      // 実際のAPIを呼び出す
      const response = await fetch('/api/moving-dates', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(dateData),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'データの登録に失敗しました');
      }
      
      // 登録成功したら再取得
      fetchDates();
      closeAddModal();
    } catch (error) {
      console.error('Error saving data:', error);
      alert(error instanceof Error ? error.message : 'データの登録に失敗しました');
    }
  };

  // 編集保存処理
  const handleSaveEdit = async () => {
    if (!selectedDate || !selectedDate.id) return;
    
    const newDate = getCurrentSelectedDate();
    
    const dateData = {
      year: Number(year),
      date: formatDateForAPI(newDate), // タイムゾーンを考慮した形式に変換
      description: description,
      direction: direction
    };
    
    try {
      // 認証トークンの取得
      const token = localStorage.getItem('token');
      
      console.log(`更新リクエスト: ID=${selectedDate.id}, データ=`, dateData);
      
      // 実際のAPIを呼び出す
      const response = await fetch(`/api/moving-dates/${selectedDate.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify(dateData),
      });
      
      console.log(`応答ステータス: ${response.status}`);
      
      const responseData = await response.json();
      console.log('応答データ:', responseData);
      
      if (!response.ok) {
        throw new Error(responseData.error || 'データの更新に失敗しました');
      }
      
      // 更新成功したら再取得
      fetchDates();
      closeEditModal();
    } catch (error) {
      console.error('Error updating data:', error);
      alert(error instanceof Error ? error.message : 'データの更新に失敗しました');
    }
  };

  // 削除処理
  const handleConfirmDelete = async () => {
    if (!selectedDate || !selectedDate.id) return;
    
    try {
      // 認証トークンの取得
      const token = localStorage.getItem('token');
      
      // 実際のAPIを呼び出す
      const response = await fetch(`/api/moving-dates/${selectedDate.id}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || 'データの削除に失敗しました');
      }
      
      // 削除成功したら再取得
      fetchDates();
      closeDeleteModal();
    } catch (error) {
      console.error('Error deleting data:', error);
      alert(error instanceof Error ? error.message : 'データの削除に失敗しました');
    }
  };
  
  // 一括追加処理
  const handleBulkSave = async () => {
    if (!bulkDates.trim()) {
      alert('日付を入力してください');
      return;
    }
    
    if (!window.confirm(`${year}年度の既存のデータをすべて削除して新しく登録します。よろしいですか？`)) {
      return;
    }
    
    // 認証トークンの取得
    const token = localStorage.getItem('token');
    
    // 結果表示をリセット
    setBulkAddResult({success: 0, errors: [], deletedCount: 0});
    
    // 成功数とエラーのリセット
    const result = {success: 0, errors: [] as string[], deletedCount: 0};
    
    try {
      // まず選択した年度のデータを全て削除
      setLoading(true);
      
      // 選択した年度のデータを取得
      const response = await fetch(`/api/moving-dates?year=${year}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('データの取得に失敗しました');
      }
      
      const existingData = await response.json();
      
      // 既存データの削除
      for (const item of existingData) {
        if (item.id) {
          const deleteResponse = await fetch(`/api/moving-dates/${item.id}`, {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          
          if (!deleteResponse.ok) {
            result.errors.push(`ID:${item.id}の削除に失敗しました`);
          } else {
            result.deletedCount++;
          }
        }
      }
      
      // 日付のパース（カンマ、スペース、改行で区切る）
      const lines = bulkDates.split(/[\n]+/).map(line => line.trim()).filter(line => line);
      
      // 各行ごとに処理
      for (const line of lines) {
        // 現在の月を保持
        let currentMonth: number | null = null;
        
        // 行を月/日形式か、カンマ区切りの日で分割
        const parts = line.split(/[,、\s]+/).map(part => part.trim()).filter(part => part);
        
        for (const part of parts) {
          try {
            // 月/日形式かチェック
            if (/^\d{1,2}\/\d{1,2}$/.test(part)) {
              // M/D形式: 4/11
              const [month, day] = part.split('/').map(Number);
              
              // 月と日の範囲チェック
              if (month < 1 || month > 12 || day < 1 || day > 31) {
                result.errors.push(`無効な日付範囲: ${part}`);
                continue;
              }
              
              // 現在の月を更新
              currentMonth = month;
              
              // 日付オブジェクト作成
              const dateObj = new Date(parseInt(year), month - 1, day);
              
              // リクエストデータ作成
              const dateData = {
                year: parseInt(year),
                date: formatDateForAPI(dateObj),
                description: bulkDescription,
                direction: bulkDirection
              };
              
              // APIリクエスト送信
              const response = await fetch('/api/moving-dates', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(dateData),
              });
              
              if (!response.ok) {
                const errorData = await response.json();
                result.errors.push(`${part}: ${errorData.error || 'データの登録に失敗しました'}`);
                continue;
              }
              
              // 成功カウントアップ
              result.success++;
              
            } else if (/^\d{1,2}$/.test(part) && currentMonth !== null) {
              // 日のみの形式（前に月が指定されている場合）: 20, 25
              const day = parseInt(part);
              
              // 日の範囲チェック
              if (day < 1 || day > 31) {
                result.errors.push(`無効な日付範囲: ${part}`);
                continue;
              }
              
              // 日付オブジェクト作成
              const dateObj = new Date(parseInt(year), currentMonth - 1, day);
              
              // リクエストデータ作成
              const dateData = {
                year: parseInt(year),
                date: formatDateForAPI(dateObj),
                description: bulkDescription,
                direction: bulkDirection
              };
              
              // APIリクエスト送信
              const response = await fetch('/api/moving-dates', {
                method: 'POST',
                headers: {
                  'Content-Type': 'application/json',
                  'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify(dateData),
              });
              
              if (!response.ok) {
                const errorData = await response.json();
                result.errors.push(`${currentMonth}/${part}: ${errorData.error || 'データの登録に失敗しました'}`);
                continue;
              }
              
              // 成功カウントアップ
              result.success++;
              
            } else {
              // その他のフォーマットはエラーとする
              result.errors.push(`無効な日付形式: ${part} - M/D形式(例: 4/11)で入力してください`);
            }
          } catch (error) {
            result.errors.push(`${part}: ${error instanceof Error ? error.message : '不明なエラー'}`);
          }
        }
      }
    } catch (error) {
      result.errors.push(`処理エラー: ${error instanceof Error ? error.message : '不明なエラー'}`);
    } finally {
      setLoading(false);
    }
    
    // データを再取得
    fetchDates();
    
    // 結果表示
    console.log('登録結果:', result);
    setBulkAddResult({
      success: result.success,
      errors: result.errors,
      deletedCount: result.deletedCount
    });
  };

  // 日の選択肢を生成
  const dayOptions = getDayOptions(
    parseInt(selectedYear), 
    parseInt(selectedMonth)
  );

  // 年選択のオプション
  const yearOptions = Array.from(
    { length: 10 }, 
    (_, i) => (getCurrentYear() - 2 + i).toString()
  ).map(year => ({
    value: year,
    label: `${year}年`
  }));

  // チェックボックスの選択ハンドラ
  const handleItemSelect = (id: number | undefined) => {
    if (!id) return;
    
    setSelectedItems(prev => {
      if (prev.includes(id)) {
        return prev.filter(item => item !== id);
      } else {
        return [...prev, id];
      }
    });
  };
  
  // すべて選択/解除のハンドラ
  const handleSelectAll = () => {
    if (selectAll) {
      setSelectedItems([]);
    } else {
      const allIds = dates.map(date => date.id).filter(id => id !== undefined) as number[];
      setSelectedItems(allIds);
    }
    setSelectAll(!selectAll);
  };
  
  // 選択した項目をすべて削除
  const handleDeleteSelected = async () => {
    if (selectedItems.length === 0) {
      alert('削除する項目が選択されていません');
      return;
    }
    
    if (!window.confirm(`選択した${selectedItems.length}件のデータを削除しますか？`)) {
      return;
    }
    
    setLoading(true);
    
    try {
      // 認証トークンの取得
      const token = localStorage.getItem('token');
      
      // 選択した項目を削除
      let deleteCount = 0;
      const errors: string[] = [];
      
      for (const id of selectedItems) {
        const response = await fetch(`/api/moving-dates/${id}`, {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (response.ok) {
          deleteCount++;
        } else {
          errors.push(`ID:${id}の削除に失敗しました`);
        }
      }
      
      // 結果の表示
      if (errors.length > 0) {
        alert(`${deleteCount}件の削除に成功し、${errors.length}件の削除に失敗しました。\n${errors.join('\n')}`);
      } else {
        alert(`${deleteCount}件のデータを削除しました。`);
      }
      
      // データを再取得
      fetchDates();
      
      // 選択状態をリセット
      setSelectedItems([]);
      setSelectAll(false);
      
    } catch (error) {
      console.error('Error deleting data:', error);
      alert(error instanceof Error ? error.message : 'データの削除に失敗しました');
    } finally {
      setLoading(false);
    }
  };

  // 成功メッセージの表示コンポーネント
  const SuccessMessage = ({ count }: { count: number }) => (
    <div>{count}件の日付を登録しました</div>
  );

  return (
    <Box>
      <Group justify="space-between" mb="md" align="flex-end">
        <Group align="flex-end">
          <Select
            label="開始年度"
            value={startYear}
            onChange={(value) => value && setStartYear(value)}
            data={getYearOptions()}
            style={{ width: 120 }}
          />
          <Text size="sm" style={{ marginBottom: '10px' }}>〜</Text>
          <Select
            label="終了年度"
            value={endYear}
            onChange={(value) => {
              if (value) {
                if (parseInt(value) < parseInt(startYear)) {
                  setStartYear(value); // 終了年度が開始年度より小さい場合、開始年度も更新
                }
                setEndYear(value);
              }
            }}
            data={getYearOptions()}
            style={{ width: 120 }}
          />
        </Group>
        <Group>
          {selectedItems.length > 0 && (
            <Button 
              variant="filled" 
              color="red" 
              leftSection={<IconTrashX size={14} />}
              onClick={handleDeleteSelected}
            >
              選択した{selectedItems.length}件を削除
            </Button>
          )}
          <Button 
            variant="outline"
            leftSection={<IconUpload size={14} />} 
            onClick={handleBulkAdd}
          >
            一括登録
          </Button>
          <Button 
            leftSection={<IconPlus size={14} />} 
            onClick={handleAdd}
          >
            吉日を追加
          </Button>
        </Group>
      </Group>

      <Paper withBorder p="md">
        {loading ? (
          <Text>データ読み込み中...</Text>
        ) : (
          <Table>
            <Table.Thead>
              <Table.Tr>
                <Table.Th style={{ width: 40 }}>
                  <Checkbox
                    checked={selectAll}
                    onChange={handleSelectAll}
                    indeterminate={selectedItems.length > 0 && selectedItems.length < dates.length}
                  />
                </Table.Th>
                <Table.Th style={{ width: 60 }}>No.</Table.Th>
                <Table.Th>日付</Table.Th>
                <Table.Th>方位</Table.Th>
                <Table.Th>説明</Table.Th>
                <Table.Th style={{ width: 120, textAlign: 'right' }}>操作</Table.Th>
              </Table.Tr>
            </Table.Thead>
            <Table.Tbody>
              {dates.length === 0 ? (
                <Table.Tr>
                  <Table.Td colSpan={6} style={{ textAlign: 'center' }}>
                    登録されている引っ越し吉日はありません
                  </Table.Td>
                </Table.Tr>
              ) : (
                dates.map((date, index) => (
                  <Table.Tr key={date.id}>
                    <Table.Td>
                      <Checkbox
                        checked={date.id ? selectedItems.includes(date.id) : false}
                        onChange={() => handleItemSelect(date.id)}
                      />
                    </Table.Td>
                    <Table.Td>{index + 1}</Table.Td>
                    <Table.Td>{formatDate(date.date)}</Table.Td>
                    <Table.Td>{date.direction || ''}</Table.Td>
                    <Table.Td>{date.description}</Table.Td>
                    <Table.Td style={{ textAlign: 'right' }}>
                      <Group gap="xs" justify="flex-end">
                        <ActionIcon 
                          variant="subtle" 
                          color="blue" 
                          onClick={() => handleEdit(date)}
                        >
                          <IconEdit size={16} />
                        </ActionIcon>
                        <ActionIcon 
                          variant="subtle" 
                          color="red" 
                          onClick={() => handleDelete(date)}
                        >
                          <IconTrash size={16} />
                        </ActionIcon>
                      </Group>
                    </Table.Td>
                  </Table.Tr>
                ))
              )}
            </Table.Tbody>
          </Table>
        )}
      </Paper>

      {/* 追加モーダル */}
      <Modal opened={addModalOpened} onClose={closeAddModal} title="引っ越し吉日の追加">
        <Group mb="md" grow>
          <Select
            label="年"
            data={yearOptions}
            value={selectedYear}
            onChange={(value) => value && setSelectedYear(value)}
            required
          />
          <Select
            label="月"
            data={getMonthOptions()}
            value={selectedMonth}
            onChange={(value) => {
              if (value) {
                setSelectedMonth(value);
                // 日数が変わる可能性があるので、選択中の日が新しい月の範囲外なら1日にリセット
                const lastDay = new Date(parseInt(selectedYear), parseInt(value), 0).getDate();
                if (parseInt(selectedDay) > lastDay) {
                  setSelectedDay('1');
                }
              }
            }}
            required
          />
          <Select
            label="日"
            data={dayOptions}
            value={selectedDay}
            onChange={(value) => value && setSelectedDay(value)}
            required
          />
        </Group>
        <TextInput
          label="説明"
          placeholder="引っ越し吉日の説明"
          value={description}
          onChange={(e) => setDescription(e.currentTarget.value)}
          mb="md"
        />
        <TextInput
          label="方位"
          placeholder="引っ越し吉日の方位"
          value={direction}
          onChange={(e) => setDirection(e.currentTarget.value)}
          mb="md"
        />
        <Group justify="flex-end">
          <Button variant="outline" onClick={closeAddModal}>キャンセル</Button>
          <Button onClick={handleSaveNew}>追加</Button>
        </Group>
      </Modal>

      {/* 編集モーダル */}
      <Modal opened={editModalOpened} onClose={closeEditModal} title="引っ越し吉日の編集">
        <Group mb="md" grow>
          <Select
            label="年"
            data={yearOptions}
            value={selectedYear}
            onChange={(value) => value && setSelectedYear(value)}
            required
          />
          <Select
            label="月"
            data={getMonthOptions()}
            value={selectedMonth}
            onChange={(value) => {
              if (value) {
                setSelectedMonth(value);
                // 日数が変わる可能性があるので、選択中の日が新しい月の範囲外なら1日にリセット
                const lastDay = new Date(parseInt(selectedYear), parseInt(value), 0).getDate();
                if (parseInt(selectedDay) > lastDay) {
                  setSelectedDay('1');
                }
              }
            }}
            required
          />
          <Select
            label="日"
            data={dayOptions}
            value={selectedDay}
            onChange={(value) => value && setSelectedDay(value)}
            required
          />
        </Group>
        <TextInput
          label="説明"
          placeholder="引っ越し吉日の説明"
          value={description}
          onChange={(e) => setDescription(e.currentTarget.value)}
          mb="md"
        />
        <TextInput
          label="方位"
          placeholder="引っ越し吉日の方位"
          value={direction}
          onChange={(e) => setDirection(e.currentTarget.value)}
          mb="md"
        />
        <Group justify="flex-end">
          <Button variant="outline" onClick={closeEditModal}>キャンセル</Button>
          <Button onClick={handleSaveEdit}>更新</Button>
        </Group>
      </Modal>

      {/* 削除確認モーダル */}
      <Modal opened={deleteModalOpened} onClose={closeDeleteModal} title="削除の確認">
        <Text mb="lg">
          {selectedDate && formatDate(selectedDate.date)}の引っ越し吉日を削除しますか？
        </Text>
        <Group justify="flex-end">
          <Button variant="outline" onClick={closeDeleteModal}>キャンセル</Button>
          <Button color="red" onClick={handleConfirmDelete}>削除</Button>
        </Group>
      </Modal>
      
      {/* 一括追加モーダル */}
      <Modal 
        opened={bulkAddModalOpened} 
        onClose={handleCloseBulkAddModal} 
        title="引っ越し吉日の一括追加" 
        size="md"
      >
        <Stack>
          <Text size="sm" c="dimmed" fw="bold" color="red">
            注意: 既存データは全て削除されます
          </Text>
          <Text size="sm" c="dimmed" component="div">
            <strong>入力形式:</strong>
            <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
              <li>「月/日、日、日」形式：4/11、20、25（4月11日、4月20日、4月25日）</li>
              <li>「月/日」だけも可能：4/11、5/7、7/8</li>
              <li>行を分けると別々の月として処理：4/11、20 (改行) 5/7、16、25</li>
            </ul>
          </Text>
          
          <Group grow mb="md">
            <Select
              label="年度"
              value={year}
              onChange={(value) => value && setYear(value)}
              data={getYearOptions()}
            />
            
            <TextInput
              label="方位"
              placeholder="すべての日付に適用する方位"
              value={bulkDirection}
              onChange={(e) => setBulkDirection(e.currentTarget.value)}
            />
          </Group>
          
          <TextInput
            label="説明"
            placeholder="すべての日付に適用する説明"
            value={bulkDescription}
            onChange={(e) => setBulkDescription(e.currentTarget.value)}
            mb="md"
          />
          
          <Textarea
            label="日付の一覧"
            placeholder="例: 4/11, 4/20, 5/7, 5/16, 5/25"
            value={bulkDates}
            onChange={(e) => setBulkDates(e.currentTarget.value)}
            minRows={4}
            mb="md"
            autosize
          />
          
          {bulkAddResult.success > 0 && (
            <Alert color="green" title="登録成功">
              <SuccessMessage count={bulkAddResult.success} />
              {bulkAddResult.deletedCount && bulkAddResult.deletedCount > 0 ? (
                <Text size="sm" mt="xs">※ {year}年度の既存データ{bulkAddResult.deletedCount}件を削除しました</Text>
              ) : null}
            </Alert>
          )}
          
          {bulkAddResult.errors.length > 0 && (
            <Alert color="red" title="登録エラー">
              <Text size="sm" mb="xs">エラー内容:</Text>
              <ul style={{ margin: 0, paddingLeft: '1.5rem' }}>
                {bulkAddResult.errors.map((err, i) => (
                  <li key={i}>{err}</li>
                ))}
              </ul>
            </Alert>
          )}
          
          <Group justify="flex-end">
            <Button variant="outline" onClick={handleCloseBulkAddModal}>閉じる</Button>
            <Button onClick={handleBulkSave} color="red">一括登録</Button>
          </Group>
        </Stack>
      </Modal>
    </Box>
  );
};

export default MovingAuspiciousDatesManager; 