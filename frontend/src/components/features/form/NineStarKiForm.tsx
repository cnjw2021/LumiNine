'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Button, Stack, Text, Title, Paper, TextInput, Radio, Group, NumberInput, Tabs, Divider, Box, Flex } from '@mantine/core';
import { IconUser, IconUsers } from '@tabler/icons-react';
import CustomDatePicker from '@/components/common/ui/Datepicker';
import api from '@/utils/api';
import { AxiosError } from 'axios';
import { Gender } from '@/stores/nineStarKiStore';
import dayjs from 'dayjs';
import 'dayjs/locale/ja';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/auth/AuthContext';

// 日本語ロケールを設定
dayjs.locale('ja');

// ローカルストレージキー
const STORAGE_KEY = 'ninestarki-result-data';
const COMPATIBILITY_STORAGE_KEY = 'ninestarki-compatibility-result-data';

// 占いタイプ
type FortuneType = 'normal' | 'compatibility';

// 入力データの型
export interface NineStarKiFormInput {
  birthdate: string;
  fullname: string;
  gender: Gender;
}

// APIエラーレスポンスの型
export interface ApiErrorResponse {
  error: string;
  message?: string;
}

// スタイル用の定数
const ACTIVE_TAB_STYLE = {
  backgroundColor: '#4BA3E3',
  color: 'white',
  fontWeight: 'bold' as const,
  padding: '10px',
  borderRadius: '4px 4px 0 0',
  fontSize: '0.9rem'
};

const INACTIVE_TAB_STYLE = {
  backgroundColor: '#F0F0F0',
  color: '#757575',
  fontWeight: 'bold' as const,
  padding: '10px',
  borderRadius: '4px 4px 0 0', 
  fontSize: '0.9rem'
};

interface NineStarKiFormProps {
  token: string;
}

const NineStarKiForm: React.FC<NineStarKiFormProps> = ({ token }) => {
  // Auth contextからスーパーユーザー権限を取得
  const { isSuperuser } = useAuth();
  const currentYear = new Date().getFullYear();
  
  // 占いタイプの状態
  const [fortuneType, setFortuneType] = useState<FortuneType>('normal');
  
  // タブのスタイル状態
  const [normalTabStyle, setNormalTabStyle] = useState(ACTIVE_TAB_STYLE);
  const [compatibilityTabStyle, setCompatibilityTabStyle] = useState(INACTIVE_TAB_STYLE);
  
  // タブ切り替え時にスタイルを更新
  useEffect(() => {
    if (fortuneType === 'normal') {
      setNormalTabStyle(ACTIVE_TAB_STYLE);
      setCompatibilityTabStyle(INACTIVE_TAB_STYLE);
    } else {
      setNormalTabStyle(INACTIVE_TAB_STYLE);
      setCompatibilityTabStyle(ACTIVE_TAB_STYLE);
    }
  }, [fortuneType]);
  
  // 共通の状態
  const [birthdate, setBirthdate] = useState<string>('');
  const [fullName, setFullName] = useState<string>('');
  const [gender, setGender] = useState<Gender>('male');
  const [targetYear, setTargetYear] = useState<number>(currentYear);
  
  // 相性鑑定用の状態
  const [partnerBirthdate, setPartnerBirthdate] = useState<string>('');
  const [partnerName, setPartnerName] = useState<string>('');
  const [partnerGender, setPartnerGender] = useState<Gender>('male');
  
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const birthdateInputRef = useRef<HTMLInputElement>(null);
  const router = useRouter();

  // 年度の入力チェック
  const handleYearChange = (value: string | number) => {
    // 入力がnullやundefinedの場合は処理しない
    if (value === null || value === undefined || value === '') return;
    
    // 数値に変換
    const numValue = typeof value === 'string' ? parseInt(value, 10) : value;
    
    // スーパーユーザーでなく、2026年以降が入力された場合
    if (!isSuperuser && numValue > currentYear) {
      setError(`${currentYear}年以降の鑑定はできません。現在の年に修正しました。`);
      setTargetYear(currentYear);
      
      // 3秒後にエラーメッセージを消す
      setTimeout(() => {
        setError(null);
      }, 3000);
    } else {
      if (error && error.includes('鑑定はできません')) {
        setError(null);
      }
      setTargetYear(numValue);
    }
  };

  // コンポーネントがマウントされたときに生年月日フィールドにフォーカスを当てる
  useEffect(() => {
    // 少し遅延させてフォーカスを設定（レンダリング完了後に確実に実行するため）
    const timer = setTimeout(() => {
      if (birthdateInputRef.current) {
        birthdateInputRef.current.focus();
      }
    }, 100);
    
    return () => clearTimeout(timer);
  }, []);

  const handleSubmit = async () => {
    // まず入力値をバリデーション
    if (fortuneType === 'normal') {
      // 生年月日のバリデーション
      if (!birthdate) {
        setError('生年月日を入力してください');
        return;
      }
      
      // 生年月日が未来の日付ではないかをチェック
      const [birthYear, birthMonth, birthDay] = birthdate.split('/');
      const birthDate = new Date(`${birthYear}-${birthMonth}-${birthDay}`);
      birthDate.setHours(0, 0, 0, 0); // 時間をリセット
      
      const today = new Date();
      today.setHours(0, 0, 0, 0); // 時間をリセット
      
      if (birthDate > today) {
        setError('生年月日は未来の日付を指定できません');
        return;
      }
      
      // 鑑定年が未来年ではないかをチェック（スーパーユーザー以外）
      if (!isSuperuser && targetYear > currentYear) {
        setError(`${currentYear}年より未来の年は鑑定できません`);
        setTargetYear(currentYear);
        return;
      }
      
      // 名前のバリデーション
      if (!fullName) {
        setError('氏名を入力してください');
        return;
      }
      
      await handleNormalSubmit();
    } else {
      // 相性鑑定の場合のバリデーション
      // あなたの生年月日
      if (!birthdate) {
        setError('あなたの生年月日を入力してください');
        return;
      }
      
      // 相手の生年月日
      if (!partnerBirthdate) {
        setError('相手の生年月日を入力してください');
        return;
      }
      
      // あなたの生年月日が未来ではないか
      const [birthYear, birthMonth, birthDay] = birthdate.split('/');
      const birthDate = new Date(`${birthYear}-${birthMonth}-${birthDay}`);
      birthDate.setHours(0, 0, 0, 0); // 時間をリセット
      
      const today = new Date();
      today.setHours(0, 0, 0, 0); // 時間をリセット
      
      if (birthDate > today) {
        setError('あなたの生年月日は未来の日付を指定できません');
        return;
      }
      
      // 相手の生年月日が未来ではないか
      const [partnerYear, partnerMonth, partnerDay] = partnerBirthdate.split('/');
      const partnerDate = new Date(`${partnerYear}-${partnerMonth}-${partnerDay}`);
      partnerDate.setHours(0, 0, 0, 0); // 時間をリセット
      
      if (partnerDate > today) {
        setError('相手の生年月日は未来の日付を指定できません');
        return;
      }
      
      await handleCompatibilitySubmit();
    }
  };

  const handleNormalSubmit = async () => {
    // バリデーションは親のhandleSubmitで済んでいるので不要
    setIsLoading(true);
    try {
      // 日付の文字列を組み合わせる
      const birthdateParts = birthdate.split('/');
      if (birthdateParts.length !== 3) {
        setError('生年月日の形式が正しくありません');
        setIsLoading(false);
        return;
      }
      
      const [year, month, day] = birthdateParts;
      
      // ISO形式の日時文字列を作成（正午を指定）
      const birthDateTimeISO = `${year}-${month}-${day} 12:00`;
      
      const response = await api.post('/nine-star/calculate', {
        birth_datetime: birthDateTimeISO,
        target_year: targetYear
      }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      if (response.data) {
        try {
          // ローカルストレージの使用可能性をチェック
          try {
            // 書き込みテスト
            localStorage.setItem('test-storage', 'test');
            localStorage.removeItem('test-storage');
          } catch (storageAccessError) {
            console.error('ローカルストレージアクセスエラー:', storageAccessError);
            setError('ブラウザのストレージ設定が制限されています。プライベートブラウジングやCookieの設定を確認してください。');
            setIsLoading(false);
            return;
          }
          
          // 計算結果をローカルストレージに保存
          const userData = {
            result: response.data,
            fullName,
            birthdate,
            gender,
            targetYear,
            isCompatibilityReading: false
          };
          
          // 既存のデータを削除して新しいデータを保存
          localStorage.removeItem(STORAGE_KEY);
          localStorage.removeItem(COMPATIBILITY_STORAGE_KEY);
          localStorage.setItem(STORAGE_KEY, JSON.stringify(userData));
          
          // Next.jsのルーターを使用してページ遷移 (ローディングは遷移後に自動で解除)
          router.push(`/result?t=${Date.now()}`);
        } catch (storageError) {
          console.error('データ保存エラー:', storageError);
          setError('結果の保存中にエラーが発生しました');
          setIsLoading(false);
        }
      } else {
        setError('鑑定結果が返されませんでした');
        setIsLoading(false);
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof AxiosError 
        ? err.response?.data?.error || '鑑定中にエラーが発生しました'
        : '鑑定中にエラーが発生しました';
      setError(errorMessage);
      setIsLoading(false);
    }
  };
  
  const handleCompatibilitySubmit = async () => {
    // バリデーションは親のhandleSubmitで済んでいるので不要
    setIsLoading(true);
    try {
      // 自分の生年月日から本命星を計算
      const birthdateParts = birthdate.split('/');
      if (birthdateParts.length !== 3) {
        setError('生年月日の形式が正しくありません');
        setIsLoading(false);
        return;
      }
      
      const [year, month, day] = birthdateParts;
      
      // ISO形式の日時文字列を作成
      const birthDateTimeISO = `${year}-${month}-${day} 12:00`;
      
      // まず本命星を計算
      const calculateResponse = await api.post('/nine-star/calculate', {
        birth_datetime: birthDateTimeISO,
        gender
      }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      // 相手の生年月日から本命星を計算
      const partnerBirthdateParts = partnerBirthdate.split('/');
      if (partnerBirthdateParts.length !== 3) {
        setError('相手の生年月日の形式が正しくありません');
        setIsLoading(false);
        return;
      }
      
      const [partnerYear, partnerMonth, partnerDay] = partnerBirthdateParts;
      
      // 相手の本命星を計算
      const partnerBirthDateTimeISO = `${partnerYear}-${partnerMonth}-${partnerDay} 12:00`;
      const partnerCalculateResponse = await api.post('/nine-star/calculate', {
        birth_datetime: partnerBirthDateTimeISO,
        gender: partnerGender
      }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      // 本命星と月の情報を取得
      const mainStarNumber = calculateResponse.data.main_star.star_number;
      const mainBirthMonth = parseInt(month, 10);
      const targetStarNumber = partnerCalculateResponse.data.main_star.star_number;
      const targetBirthMonth = parseInt(partnerMonth, 10);
      
      // 相性鑑定APIを呼び出す
      const compatibilityResponse = await api.post('/compatibility', {
        main_star: mainStarNumber,
        target_star: targetStarNumber,
        main_birth_month: mainBirthMonth,
        target_birth_month: targetBirthMonth,
        is_male: partnerGender === 'male'
      }, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      if (compatibilityResponse.data) {
        try {
          // ローカルストレージの使用可能性をチェック
          localStorage.setItem('test-storage', 'test');
          localStorage.removeItem('test-storage');
          
          // 相性鑑定結果をローカルストレージに保存
          const compatibilityData = {
            result: compatibilityResponse.data,
            mainPerson: {
              name: fullName || 'あなた',
              star: calculateResponse.data.main_star,
              birthdate
            },
            targetPerson: {
              name: partnerName || '相手',
              star: partnerCalculateResponse.data.main_star,
              birthdate: partnerBirthdate
            },
            gender: partnerGender
          };
          
          // 本人の鑑定結果も保存
          const userData = {
            result: calculateResponse.data,
            fullName,
            birthdate,
            gender,
            isCompatibilityReading: true,
          };
          
          // 保存
          localStorage.removeItem(COMPATIBILITY_STORAGE_KEY);
          localStorage.setItem(COMPATIBILITY_STORAGE_KEY, JSON.stringify(compatibilityData));
          
          localStorage.removeItem(STORAGE_KEY);
          localStorage.setItem(STORAGE_KEY, JSON.stringify(userData));
          
          // 結果ページに遷移（通常鑑定ページに変更）
          router.push(`/result?t=${Date.now()}`);
        } catch (storageError) {
          console.error('データ保存エラー:', storageError);
          setError('結果の保存中にエラーが発生しました');
          setIsLoading(false);
        }
      } else {
        setError('相性鑑定結果が返されませんでした');
        setIsLoading(false);
      }
    } catch (err: unknown) {
      const errorMessage = err instanceof AxiosError 
        ? err.response?.data?.error || '相性鑑定中にエラーが発生しました'
        : '相性鑑定中にエラーが発生しました';
      setError(errorMessage);
      setIsLoading(false);
    }
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
          backgroundColor: 'rgba(255, 255, 255, 0.9)',
          border: '2px solid #4BA3E3',
          borderRadius: '15px',
          width: '100%',
          maxWidth: '400px'
        }}
      >
        <Stack gap={0} align="center" mb={{ base: 'xs', sm: 'md' }}>
          <Title order={1} ta="center" c="#4BA3E3" style={{ fontSize: '1.8rem', whiteSpace: 'nowrap' }}>九星気学占い</Title>
        </Stack>
        
        <Tabs 
          value={fortuneType}
          onChange={(value) => setFortuneType(value as FortuneType)}
          color="#4BA3E3"
          variant="default"
          radius="md"
          mb={{ base: 'xs', sm: 'md' }}
        >
          <Tabs.List grow style={{ backgroundColor: 'transparent', border: 'none', gap: '5px' }}>
            <Tabs.Tab 
              value="normal" 
              leftSection={<IconUser size={16} />}
              style={normalTabStyle}
            >
              通常鑑定
            </Tabs.Tab>
            <Tabs.Tab 
              value="compatibility" 
              leftSection={<IconUsers size={16} />}
              style={compatibilityTabStyle}
            >
              相性鑑定
            </Tabs.Tab>
          </Tabs.List>
        </Tabs>
        
        <Stack w="100%" gap="xs" styles={{ root: { gap: 'var(--mantine-spacing-xs)' } }}>
          {/* 相性鑑定の場合は縦並びレイアウト */}
          {fortuneType === 'compatibility' ? (
            <Stack gap="xs">
              {/* あなたの情報 */}
              <Box>
                <Text fw="bold" size="sm" style={{ backgroundColor: '#e6f2ff', padding: '3px 8px', borderRadius: '4px' }}>あなたの情報</Text>
                <Divider mt={0} mb={5} />
                
                <Stack gap="xs" mt={5}>
                  <Flex align="center" gap="xs">
                    <Box style={{ width: '90px' }}>
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
                    <Box style={{ width: '90px' }}>
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
                              borderColor: '#4BA3E3'
                            },
                            height: '30px',
                            minHeight: '30px'
                          }
                        }}
                      />
                    </Box>
                  </Flex>
                </Stack>
              </Box>

              {/* 相手の情報 */}
              <Box mt={5}>
                <Text fw="bold" size="sm" style={{ backgroundColor: '#fff0f0', padding: '3px 8px', borderRadius: '4px' }}>相手の情報</Text>
                <Divider mt={0} mb={5} />
                
                <Stack gap="xs" mt={5}>
                  <Flex align="center" gap="xs">
                    <Box style={{ width: '90px' }}>
                      <Text size="sm" fw={500}>生年月日</Text>
                      <Text size="xs" c="dimmed">(/は自動で入力)</Text>
                    </Box>
                    <Box style={{ flexGrow: 1 }}>
                      <CustomDatePicker 
                        value={partnerBirthdate}
                        onChange={(date) => {
                          setPartnerBirthdate(date);
                        }}
                        label=""
                        disabled={isLoading}
                      />
                    </Box>
                  </Flex>
                  
                  <Flex align="center" gap="xs">
                    <Box style={{ width: '90px' }}>
                      <Text size="sm" fw={500}>氏名</Text>
                    </Box>
                    <Box style={{ flexGrow: 1 }}>
                      <TextInput
                        label=""
                        placeholder="例: 佐藤 花子"
                        value={partnerName}
                        onChange={(e) => setPartnerName(e.currentTarget.value)}
                        size="xs"
                        disabled={isLoading}
                        style={{ flexGrow: 1 }}
                        styles={{
                          input: {
                            '&:focus': {
                              borderColor: '#4BA3E3'
                            },
                            height: '30px',
                            minHeight: '30px'
                          }
                        }}
                      />
                    </Box>
                  </Flex>

                  <Flex align="center" gap="xs">
                    <Box style={{ width: '90px' }}>
                      <Text size="sm" fw={500}>性別</Text>
                    </Box>
                    <Box style={{ flexGrow: 1 }}>
                      <Radio.Group
                        value={partnerGender}
                        onChange={(value) => setPartnerGender(value as Gender)}
                      >
                        <Group mt={0}>
                          <Radio value="male" label="男性" disabled={isLoading} size="xs" />
                          <Radio value="female" label="女性" disabled={isLoading} size="xs" />
                        </Group>
                      </Radio.Group>
                    </Box>
                  </Flex>
                </Stack>
              </Box>
            </Stack>
          ) : (
            /* 通常鑑定の場合は1カラムレイアウト */
            <Box>
              <Text fw="bold" size="sm" style={{ backgroundColor: '#e6f2ff', padding: '3px 8px', borderRadius: '4px' }}>あなたの情報</Text>
              <Divider mt={0} mb={5} />
              
              <Stack gap="xs" mt={5}>
                <Flex align="center" gap="xs">
                  <Box style={{ width: '90px' }}>
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
                  <Box style={{ width: '90px' }}>
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
                            borderColor: '#4BA3E3'
                          },
                          height: '30px',
                          minHeight: '30px'
                        }
                      }}
                    />
                  </Box>
                </Flex>

                <Flex align="center" gap="xs">
                  <Box style={{ width: '90px' }}>
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
                  <Box style={{ width: '90px' }}>
                    <Text size="sm" fw={500}>鑑定年</Text>
                    {!isSuperuser && <Text size="xs" c="dimmed">({currentYear}年まで)</Text>}
                  </Box>
                  <Box style={{ flexGrow: 1 }}>
                    <NumberInput
                      placeholder={currentYear.toString()}
                      value={targetYear}
                      onChange={handleYearChange}
                      min={1900}
                      max={isSuperuser ? 2100 : 3000}
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
          )}

          {error && (
            <Text c="red" size="xs" ta="center">
              {error}
            </Text>
          )}

          <Button
            size="md"
            variant="gradient"
            gradient={{ from: '#4BA3E3', to: '#FFE45C' }}
            onClick={handleSubmit}
            mt={{ base: 'sm', sm: 'md' }}
            loading={isLoading}
            disabled={isLoading}
            loaderProps={{ color: '#4BA3E3', size: 'sm' }}
          >
            {isLoading ? '鑑定中...' : fortuneType === 'normal' ? '占い結果を見る' : '相性を鑑定する'}
          </Button>
        </Stack>
      </Paper>
    </Stack>
  );
};

export default NineStarKiForm;
