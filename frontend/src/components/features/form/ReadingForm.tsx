'use client';

import React from 'react';
import { Button, Stack, Text, Title, Paper, TextInput, Radio, Group, NumberInput, Divider, Box, Flex } from '@mantine/core';
import CustomDatePicker from '@/components/common/ui/Datepicker';
import { Gender } from '@/types';
import { useAuth } from '@/contexts/auth/AuthContext';
import { COLORS, FONTS, BUTTON } from '@/utils/theme';
import { useReadingForm } from '@/hooks/useReadingForm';
import { useReadingSubmit } from '@/hooks/useReadingSubmit';
import { MIN_TARGET_YEAR, MAX_YEAR_SUPERUSER, MAX_YEAR_NORMAL } from './readingFormConstants';

/**
 * 鑑定入力フォーム
 *
 * SRP: フォームUIの描画のみを担当
 *      状態管理は useReadingForm、送信処理は useReadingSubmit に委譲
 */

interface ReadingFormProps {
  token: string;
}

/** フォームフィールドのラベル幅 */
const LABEL_WIDTH = '90px';

const ReadingForm: React.FC<ReadingFormProps> = ({ token }) => {
  const { isSuperuser } = useAuth();
  const currentYear = new Date().getFullYear();

  const {
    birthdate, setBirthdate,
    fullName, setFullName,
    gender, setGender,
    targetYear,
    error, setError,
    birthdateInputRef,
    handleYearChange,
  } = useReadingForm({ isSuperuser, currentYear });

  const { isLoading, handleSubmit } = useReadingSubmit({ token, isSuperuser, currentYear });

  const onSubmit = () => {
    handleSubmit({ birthdate, fullName, gender, targetYear }, setError);
  };

  return (
    <Stack p={{ base: 'xs', sm: 'xl' }} align="center" style={{
      width: '100%',
      margin: '0 auto',
      position: 'relative'
    }}>
      <Paper
        shadow="md"
        p={{ base: 'xs', sm: 'md' }}
        radius="md"
        style={{
          backgroundColor: 'rgba(255, 255, 255, 0.95)',
          border: '1px solid rgba(212, 175, 55, 0.15)',
          borderRadius: '16px',
          width: '100%',
          maxWidth: '400px',
          boxShadow: '0 5px 20px -5px rgba(0, 0, 0, 0.03)'
        }}
      >
        <Stack gap={0} align="center" mb={{ base: 'xs', sm: 'md' }}>
          <Title order={1} ta="center" c={COLORS.text} style={{ fontSize: '1.8rem', whiteSpace: 'nowrap', fontFamily: FONTS.title, fontWeight: 'normal', letterSpacing: '0.05em' }}>パーソナルストーン鑑定</Title>
        </Stack>

        <Stack w="100%" gap="xs" styles={{ root: { gap: 'var(--mantine-spacing-xs)' } }}>
          <Box>
            <Divider mt={0} mb={5} />

            <Stack gap="xs" mt={5}>
              <Flex align="center" gap="xs">
                <Box style={{ width: LABEL_WIDTH }}>
                  <Text size="sm" fw={500}>生年月日</Text>
                  <Text size="xs" c="dimmed">(/は自動で入力)</Text>
                </Box>
                <Box style={{ flexGrow: 1 }}>
                  <CustomDatePicker
                    ref={birthdateInputRef}
                    value={birthdate}
                    onChange={setBirthdate}
                    label=""
                    disabled={isLoading}
                  />
                </Box>
              </Flex>

              <Flex align="center" gap="xs">
                <Box style={{ width: LABEL_WIDTH }}>
                  <Text size="sm" fw={500}>氏名</Text>
                </Box>
                <Box style={{ flexGrow: 1 }}>
                  <TextInput
                    label=""
                    placeholder="例: 山田 太郎"
                    value={fullName}
                    onChange={(e) => setFullName(e.currentTarget.value)}
                    size="xs"
                    disabled={isLoading}
                    style={{ flexGrow: 1 }}
                    styles={{
                      input: {
                        '&:focus': {
                          borderColor: COLORS.accent
                        },
                        height: '30px',
                        minHeight: '30px'
                      }
                    }}
                  />
                </Box>
              </Flex>

              <Flex align="center" gap="xs">
                <Box style={{ width: LABEL_WIDTH }}>
                  <Text size="sm" fw={500}>性別</Text>
                </Box>
                <Box style={{ flexGrow: 1 }}>
                  <Radio.Group
                    value={gender}
                    onChange={(value) => setGender(value as Gender)}
                  >
                    <Group mt={0}>
                      <Radio value="male" label="男性" disabled={isLoading} size="xs" />
                      <Radio value="female" label="女性" disabled={isLoading} size="xs" />
                    </Group>
                  </Radio.Group>
                </Box>
              </Flex>

              <Flex align="center" gap="xs">
                <Box style={{ width: LABEL_WIDTH }}>
                  <Text size="sm" fw={500}>鑑定年</Text>
                  {!isSuperuser && <Text size="xs" c="dimmed">({currentYear}年まで)</Text>}
                </Box>
                <Box style={{ flexGrow: 1 }}>
                  <NumberInput
                    placeholder={currentYear.toString()}
                    value={targetYear}
                    onChange={handleYearChange}
                    min={MIN_TARGET_YEAR}
                    max={isSuperuser ? MAX_YEAR_SUPERUSER : MAX_YEAR_NORMAL}
                    required
                    size="xs"
                    style={{ flexGrow: 1 }}
                    styles={{
                      input: {
                        height: '30px',
                        minHeight: '30px'
                      }
                    }}
                  />
                </Box>
              </Flex>
            </Stack>
          </Box>

          {error && (
            <Text c="red" size="xs" ta="center">
              {error}
            </Text>
          )}

          <Button
            size="md"
            onClick={onSubmit}
            mt={{ base: 'sm', sm: 'md' }}
            loading={isLoading}
            disabled={isLoading}
            loaderProps={{ color: 'white', size: 'sm' }}
            style={{
              ...BUTTON.primary,
              cursor: 'pointer',
              transition: 'all 0.3s ease',
            }}
          >
            {isLoading ? '鑑定中...' : '鑑定結果を見る'}
          </Button>
        </Stack>
      </Paper>
    </Stack>
  );
};

export default ReadingForm;
