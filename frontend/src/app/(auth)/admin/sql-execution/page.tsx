'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Group, Text, Paper, Badge, Loader, Accordion, Code, Table, Button } from '@mantine/core';
import { notifications } from '@mantine/notifications';
import api from '@/utils/api';

interface SqlFile {
  name: string;
  path: string;
  size: number;
  selected: boolean;
}

interface ExecutionResult {
  file: string;
  success: boolean;
  message: string;
  affectedRows?: number;
}

interface SqlFileResponse {
  name: string;
  path: string;
  size: number;
}

interface ApiErrorDetails {
  status?: number;
  statusText?: string;
  data?: unknown;
  url?: string;
  method?: string;
  message?: string;
}

interface ApiError extends Error {
  details?: ApiErrorDetails;
}

export default function SqlExecutionPage() {
  const [sqlFiles, setSqlFiles] = useState<SqlFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [executing, setExecuting] = useState(false);
  const [results, setResults] = useState<ExecutionResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSqlFiles();
  }, []);

  const fetchSqlFiles = async () => {
    try {
      setLoading(true);
      console.log('SQLファイル取得を開始します');
      
      const response = await api.get<SqlFileResponse[]>('/admin/db/sql-files');
      console.log('SQLファイル取得成功:', response);
      
      const files: SqlFile[] = response.data.map((file) => ({
        ...file,
        selected: false
      }));
      setSqlFiles(files);
      setError(null);
    } catch (error: unknown) {
      console.error('SQLファイル取得エラー:', error);
      
      // エラーの詳細情報をコンソールに出力
      if (error instanceof Error) {
        const apiError = error as ApiError;
        console.error('APIエラー詳細:', apiError.details);
        console.error('エラーメッセージ:', apiError.message);
        console.error('エラーの詳細情報:', JSON.stringify(apiError, null, 2));
      }
      
      let errorMessage = 'SQLファイルの取得に失敗しました';
      
      if (error instanceof Error) {
        const apiError = error as ApiError;
        if (apiError.details?.message) {
          errorMessage = apiError.details.message;
        } else if (apiError.message) {
          errorMessage = apiError.message;
        }
      }
      
      setError(`SQLファイルの取得に失敗しました: ${errorMessage}`);
      notifications.show({
        title: 'エラー',
        message: errorMessage,
        color: 'red',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleCheckboxChange = (index: number) => {
    console.log('Checkbox changed for index:', index, 'Array length:', sqlFiles.length);
    if (index >= 0 && index < sqlFiles.length) {
      setSqlFiles(prev => {
        const updated = [...prev];
        updated[index] = {
          ...updated[index],
          selected: !updated[index].selected
        };
        return updated;
      });
    } else {
      console.error('Invalid index:', index);
    }
  };

  const handleSelectByPrefix = (prefix: string) => {
    setSqlFiles(prev => {
      return prev.map(file => ({
        ...file,
        selected: file.name.startsWith(prefix)
      }));
    });
  };

  const handleSelectAll = (select: boolean) => {
    setSqlFiles(prev => {
      return prev.map(file => ({
        ...file,
        selected: select
      }));
    });
  };

  const executeSqlFiles = async () => {
    try {
      setExecuting(true);
      setResults([]);
      
      const selectedFiles = sqlFiles.filter(file => file.selected);
      console.log('選択されたファイル:', selectedFiles);
      
      if (selectedFiles.length === 0) {
        notifications.show({
          title: '注意',
          message: '実行するSQLファイルを選択してください',
          color: 'yellow',
        });
        return;
      }

      const filePaths = selectedFiles.map(file => file.path);
      console.log('実行するファイルパス:', filePaths);

      // 実際のリクエストURLをログに出力
      const fullUrl = api.getUri({ url: '/admin/db/execute-sql' });
      console.log('実際のリクエストURL:', fullUrl);
      console.log('送信するデータ:', { files: filePaths });

      console.log('API実行開始');
      const response = await api.post<{ results: ExecutionResult[] }>('/admin/db/execute-sql', { files: filePaths });
      console.log('API実行レスポンス全体:', response);
      console.log('API実行結果:', response.data);
      
      setResults(response.data.results);
      
      const successCount = response.data.results.filter((r) => r.success).length;
      notifications.show({
        title: '実行完了',
        message: `${successCount}/${selectedFiles.length} ファイルを実行しました`,
        color: successCount === selectedFiles.length ? 'green' : 'yellow',
      });
      
    } catch (error: unknown) {
      console.error('SQL実行エラー:', error);
      console.error('エラーの詳細情報:', JSON.stringify(error, null, 2));
      let errorMessage = 'SQLファイルの実行に失敗しました';
      
      if (error instanceof Error) {
        const apiError = error as ApiError;
        console.error('APIエラー詳細:', apiError.details);
        if (apiError.details?.message) {
          errorMessage = apiError.details.message;
        } else if (apiError.message) {
          errorMessage = apiError.message;
        }
      }
      
      setError(`SQLファイルの実行に失敗しました: ${errorMessage}`);
      notifications.show({
        title: 'エラー',
        message: errorMessage,
        color: 'red',
      });
    } finally {
      setExecuting(false);
    }
  };

  // ファイルをカテゴリごとにグループ化
  const groupedFiles = sqlFiles.reduce<Record<string, SqlFile[]>>((groups, file) => {
    // ファイル名のパターンから接頭辞を取得（例：000_, 100_, 200_など）
    const prefix = file.name.match(/^(\d+)_/)?.[1] || 'その他';
    
    // 接頭辞に基づいてカテゴリ名を決定
    let category;
    if (prefix === '000') category = 'テーブル作成';
    else if (prefix.startsWith('1')) category = '基本データ';
    else if (prefix.startsWith('2')) category = '鑑定データ';
    else if (prefix.startsWith('9')) category = 'システムデータ';
    else category = 'その他';
    
    if (!groups[category]) {
      groups[category] = [];
    }
    groups[category].push(file);
    return groups;
  }, {});

  return (
    <div className="container mx-auto py-10">
      <Card className="shadow-lg">
        <CardHeader className="bg-gray-50">
          <CardTitle>SQLファイル実行</CardTitle>
        </CardHeader>
        <CardContent className="p-6">
          {error && (
            <Paper p="md" mb="md" withBorder radius="md" style={{ backgroundColor: '#FEE2E2', borderColor: '#F87171' }}>
              <Text c="red" fw={500}>{error}</Text>
            </Paper>
          )}
          
          <Group mb="md">
            <Button onClick={() => fetchSqlFiles()} disabled={loading}>
              ファイル一覧を更新
            </Button>
            <Button 
              onClick={() => {
                console.log('実行ボタンがクリックされました');
                console.log('現在の選択状態:', sqlFiles.filter(f => f.selected));
                executeSqlFiles();
              }} 
              disabled={executing || sqlFiles.filter(f => f.selected).length === 0}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {executing ? (
                <>
                  <Loader size="xs" color="white" className="mr-2" />
                  実行中...
                </>
              ) : '選択したファイルを実行'}
            </Button>
          </Group>
          
          <Group mb="md">
            <Text fw={500}>クイック選択:</Text>
            <Badge 
              color="blue" 
              variant="outline" 
              style={{ cursor: 'pointer' }}
              onClick={() => handleSelectAll(true)}
            >
              すべて選択
            </Badge>
            <Badge 
              color="gray" 
              variant="outline" 
              style={{ cursor: 'pointer' }}
              onClick={() => handleSelectAll(false)}
            >
              すべて解除
            </Badge>
            <Badge 
              color="green" 
              variant="outline" 
              style={{ cursor: 'pointer' }}
              onClick={() => handleSelectByPrefix('200_')}
            >
              鑑定データのみ
            </Badge>
          </Group>
          
          {loading ? (
            <div className="flex justify-center items-center h-40">
              <Loader />
            </div>
          ) : (
            <>
              <Accordion variant="separated" mb="lg">
                {Object.entries(groupedFiles).map(([category, files]) => (
                  <Accordion.Item key={category} value={category}>
                    <Accordion.Control>
                      <Group>
                        <Text fw={600}>{category}</Text>
                        <Badge>{files.length}ファイル</Badge>
                        <Badge color="blue">{files.filter(f => f.selected).length}選択中</Badge>
                      </Group>
                    </Accordion.Control>
                    <Accordion.Panel>
                      <Table striped highlightOnHover>
                        <Table.Thead>
                          <Table.Tr>
                            <Table.Th style={{ width: 40 }}></Table.Th>
                            <Table.Th>ファイル名</Table.Th>
                            <Table.Th style={{ width: 100 }}>サイズ</Table.Th>
                            <Table.Th style={{ width: 100 }}>ステータス</Table.Th>
                          </Table.Tr>
                        </Table.Thead>
                        <Table.Tbody>
                          {files.map((file) => {
                            const fileIndex = sqlFiles.findIndex(f => f.path === file.path);
                            return (
                              <Table.Tr 
                                key={file.path}
                                className={`
                                  transition-colors duration-200
                                  ${file.selected ? 'bg-blue-50' : ''}
                                `}
                              >
                                <Table.Td>
                                  <input
                                    type="checkbox"
                                    id={`file-${file.path}`}
                                    checked={file.selected}
                                    onChange={() => {
                                      if (fileIndex !== -1) {
                                        handleCheckboxChange(fileIndex);
                                      }
                                    }}
                                    className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                                  />
                                </Table.Td>
                                <Table.Td>
                                  <div>
                                    <Text size="sm" fw={500}>{file.name}</Text>
                                    <Text size="xs" c="dimmed">{file.path}</Text>
                                  </div>
                                </Table.Td>
                                <Table.Td>
                                  <Text size="sm" c="dimmed">
                                    {file.size < 1024 
                                      ? `${file.size} バイト` 
                                      : `${(file.size / 1024).toFixed(1)} KB`
                                    }
                                  </Text>
                                </Table.Td>
                                <Table.Td>
                                  {file.selected && (
                                    <Badge 
                                      color="blue" 
                                      radius="sm" 
                                      size="sm"
                                    >
                                      選択中
                                    </Badge>
                                  )}
                                </Table.Td>
                              </Table.Tr>
                            );
                          })}
                        </Table.Tbody>
                      </Table>
                    </Accordion.Panel>
                  </Accordion.Item>
                ))}
              </Accordion>
              
              {results.length > 0 && (
                <div>
                  <Text fw={700} mb="md">実行結果</Text>
                  <Paper p="md" withBorder>
                    <Table>
                      <Table.Thead>
                        <Table.Tr>
                          <Table.Th>ファイル名</Table.Th>
                          <Table.Th>ステータス</Table.Th>
                          <Table.Th>影響行数</Table.Th>
                          <Table.Th>メッセージ</Table.Th>
                        </Table.Tr>
                      </Table.Thead>
                      <Table.Tbody>
                        {results.map((result, index) => (
                          <Table.Tr key={index}>
                            <Table.Td>
                              <Code>{result.file}</Code>
                            </Table.Td>
                            <Table.Td>
                              <Badge color={result.success ? 'green' : 'red'}>
                                {result.success ? '成功' : '失敗'}
                              </Badge>
                            </Table.Td>
                            <Table.Td>
                              {result.affectedRows !== undefined ? result.affectedRows : '-'}
                            </Table.Td>
                            <Table.Td>{result.message}</Table.Td>
                          </Table.Tr>
                        ))}
                      </Table.Tbody>
                    </Table>
                  </Paper>
                </div>
              )}
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
} 