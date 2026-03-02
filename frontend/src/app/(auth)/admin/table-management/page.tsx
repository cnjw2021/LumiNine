'use client';

import { useState, useEffect } from 'react';
import { 
  Title, 
  Text, 
  Group, 
  Button, 
  Alert, 
  Modal, 
  Stack,
  Accordion,
  Badge,
  Code,
  Loader,
  Box
} from '@mantine/core';
import { IconAlertCircle, IconRefresh, IconDatabase, IconCheck } from '@tabler/icons-react';
import { useDisclosure } from '@mantine/hooks';
import axios from 'axios';
import { notifications } from '@mantine/notifications';
import api from '../../../../utils/api';

interface TableDefinition {
  name: string;
  comment: string;
  definition: string;
}

export default function TableManagementPage() {
  const [tables, setTables] = useState<TableDefinition[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTable, setSelectedTable] = useState<TableDefinition | null>(null);
  const [isRecreating, setIsRecreating] = useState(false);
  const [opened, { open, close }] = useDisclosure(false);

  useEffect(() => {
    fetchTables();
  }, []);

  const fetchTables = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await api.get('/admin/tables');
      setTables(response.data.tables);
    } catch (err) {
      setError(axios.isAxiosError(err) ? 
        err.response?.data?.error || 'テーブル一覧の取得に失敗しました' : 
        'テーブル一覧の取得に失敗しました');
      console.error('Failed to fetch tables:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRecreateTable = async () => {
    if (!selectedTable) return;
    
    setIsRecreating(true);
    try {
      await api.post(`/admin/tables/${selectedTable.name}/recreate`);
      notifications.show({
        title: '成功',
        message: `テーブル ${selectedTable.name} を再作成しました`,
        color: 'green',
        icon: <IconCheck size={18} />,
        autoClose: 5000
      });
      close();
    } catch (err) {
      notifications.show({
        title: 'エラー',
        message: axios.isAxiosError(err) ? 
          err.response?.data?.error || 'テーブルの再作成に失敗しました' : 
          'テーブルの再作成に失敗しました',
        color: 'red',
        icon: <IconAlertCircle size={18} />,
        autoClose: 5000
      });
      console.error('Failed to recreate table:', err);
    } finally {
      setIsRecreating(false);
    }
  };

  const openRecreateModal = (table: TableDefinition) => {
    setSelectedTable(table);
    open();
  };

  return (
    <>
      <Title order={2} mb="md">テーブル管理</Title>
      <Text mb="xl">
        データベースのテーブルを再作成（DROP & CREATE）することができます。
        データは全て削除されるため、注意して操作してください。
      </Text>

      {error && (
        <Alert icon={<IconAlertCircle size={16} />} title="エラー" color="red" mb="md">
          {error}
        </Alert>
      )}

      <Group mb="md">
        <Button 
          leftSection={<IconRefresh size={16} />} 
          onClick={fetchTables} 
          variant="outline"
          disabled={loading}
        >
          更新
        </Button>
      </Group>

      {loading ? (
        <Box style={{ display: 'flex', justifyContent: 'center', padding: '2rem' }}>
          <Loader size="lg" />
        </Box>
      ) : (
        <Accordion variant="separated">
          {tables.map((table) => (
            <Accordion.Item key={table.name} value={table.name}>
              <Accordion.Control>
                <Group>
                  <IconDatabase size={16} />
                  <Text fw={500}>{table.name}</Text>
                  <Badge color="blue" variant="light">{table.comment}</Badge>
                </Group>
              </Accordion.Control>
              <Accordion.Panel>
                <Stack>
                  <Title order={5}>テーブル定義</Title>
                  <Code block style={{ maxHeight: '200px', overflow: 'auto' }}>
                    {table.definition}
                  </Code>
                  <Group justify="flex-end">
                    <Button 
                      color="red"
                      onClick={() => openRecreateModal(table)}
                      leftSection={<IconRefresh size={16} />}
                    >
                      テーブルを再作成
                    </Button>
                  </Group>
                </Stack>
              </Accordion.Panel>
            </Accordion.Item>
          ))}
        </Accordion>
      )}

      <Modal 
        opened={opened} 
        onClose={close} 
        title="テーブルの再作成"
        centered
      >
        <Text mb="md">
          テーブル <strong>{selectedTable?.name}</strong> を再作成します。
          テーブル内のデータは全て削除されます。
          よろしいですか？
        </Text>
        <Group justify="flex-end">
          <Button variant="outline" onClick={close} disabled={isRecreating}>
            キャンセル
          </Button>
          <Button 
            color="red" 
            onClick={handleRecreateTable} 
            loading={isRecreating}
          >
            再作成
          </Button>
        </Group>
      </Modal>
    </>
  );
} 