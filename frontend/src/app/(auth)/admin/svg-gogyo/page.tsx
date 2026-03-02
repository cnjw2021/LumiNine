'use client';

import React, { useRef, useState } from 'react';
import { Title, Text, Box, Group, Button, Slider, Card, Stack, Grid, ActionIcon, Badge, Alert } from '@mantine/core';
import { IconDownload, IconSettings, IconInfoCircle } from '@tabler/icons-react';
import { useAuth } from '@/contexts/auth/AuthContext';
import FiveElementsCycle from '@/components/features/visualization/FiveElementsCycle';

export default function SvgGogyoPage() {
  const auth = useAuth();
  const svgRef = useRef<HTMLDivElement>(null);
  const [size, setSize] = useState(600);
  const [isDownloading, setIsDownloading] = useState<boolean>(false);
  const [isPngDownloading, setIsPngDownloading] = useState<boolean>(false);
  const [pngQuality, setPngQuality] = useState(2);
  const previewSize = Math.min(size, 600);

  const handleSVGDownload = async () => {
    setIsDownloading(true);
    try {
      const svgElement = svgRef.current?.querySelector('svg');
      if (!svgElement) throw new Error('SVG element not found');

      // SVGをディープクローン
      const clonedSvg = svgElement.cloneNode(true) as SVGElement;
      
      // 画像要素を探してインライン化
      const images = clonedSvg.getElementsByTagName('image');
      await Promise.all(Array.from(images).map(async (img) => {
        const href = img.getAttribute('href') || img.getAttribute('xlink:href');
        if (href) {
          // 画像をフェッチしてBase64に変換
          const response = await fetch(href);
          const blob = await response.blob();
          const base64 = await new Promise<string>((resolve) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result as string);
            reader.readAsDataURL(blob);
          });
          img.setAttribute('href', base64);
        }
      }));

      // インライン化したSVGをシリアライズ
      const svgData = new XMLSerializer().serializeToString(clonedSvg);
      const blob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
      const url = URL.createObjectURL(blob);

      const link = document.createElement('a');
      link.href = url;
      link.download = `五行図_${size}px.svg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('SVG download failed:', error);
    } finally {
      setIsDownloading(false);
    }
  };

  const handlePNGDownload = async () => {
    setIsPngDownloading(true);
    try {
      const svgElement = svgRef.current?.querySelector('svg');
      if (!svgElement) throw new Error('SVG element not found');

      // SVGをディープクローン
      const clonedSvg = svgElement.cloneNode(true) as SVGElement;
      
      // 画像要素を探してインライン化
      const images = clonedSvg.getElementsByTagName('image');
      await Promise.all(Array.from(images).map(async (img) => {
        const href = img.getAttribute('href') || img.getAttribute('xlink:href');
        if (href) {
          // 画像をフェッチしてBase64に変換
          const response = await fetch(href);
          const blob = await response.blob();
          const base64 = await new Promise<string>((resolve) => {
            const reader = new FileReader();
            reader.onloadend = () => resolve(reader.result as string);
            reader.readAsDataURL(blob);
          });
          img.setAttribute('href', base64);
        }
      }));

      // インライン化したSVGをシリアライズ
      const svgData = new XMLSerializer().serializeToString(clonedSvg);
      const svgBlob = new Blob([svgData], { type: 'image/svg+xml;charset=utf-8' });
      const svgUrl = URL.createObjectURL(svgBlob);

      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      if (!ctx) throw new Error('Canvas context not available');

      // 高品質な出力のための設定
      canvas.width = size * pngQuality;
      canvas.height = size * pngQuality;
      ctx.imageSmoothingEnabled = true;
      ctx.imageSmoothingQuality = 'high';

      // 背景を白で塗りつぶし
      ctx.fillStyle = '#FFFFFF';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // SVGを画像として読み込み
      const img = new Image();
      img.src = svgUrl;

      await new Promise((resolve, reject) => {
        img.onload = () => {
          ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
          URL.revokeObjectURL(svgUrl);
          resolve(null);
        };
        img.onerror = (error) => {
          URL.revokeObjectURL(svgUrl);
          reject(error);
        };
      });

      // 最高品質でPNGとして保存
      const pngUrl = canvas.toDataURL('image/png', 1.0);
      const link = document.createElement('a');
      link.href = pngUrl;
      link.download = `五行図_${size}px_${pngQuality}x.png`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('PNG download failed:', error);
    } finally {
      setIsPngDownloading(false);
    }
  };

  // superuser以外はアクセス拒否
  if (!auth.isSuperuser) {
    return (
      <Box>
        <Alert icon={<IconInfoCircle />} color="red" title="アクセス権限がありません">
          この機能はスーパーユーザーのみが利用できます。
        </Alert>
      </Box>
    );
  }

  const previewComponent = (
    <div 
      ref={svgRef}
      style={{ 
        width: '100%',
        height: 'auto',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        margin: '0 auto',
        aspectRatio: '1 / 1'
      }}
    >
      <FiveElementsCycle
        size={previewSize}
      />
    </div>
  );

  return (
    <Box style={{ maxWidth: '1200px', margin: '20px auto', padding: '20px 0' }}>
      <Title order={2} mb={20} style={{ fontSize: '1.5rem', fontWeight: 700, color: '#1A202C', whiteSpace: 'nowrap' }}>
        SVG五行図ダウンロード
      </Title>

      <Grid gutter="xl">
        {/* プレビューエリア */}
        <Grid.Col span={12}>
          <Card 
            shadow="sm" 
            radius="lg" 
            p="1%"
            style={{ 
              background: 'linear-gradient(135deg, #fff 0%, #f7fafc 100%)',
              border: '1px solid rgba(0,0,0,0.05)'
            }}
          >
            <Box style={{ 
              display: 'flex', 
              justifyContent: 'center', 
              alignItems: 'center',
              width: '100%',
              padding: '1%',
              aspectRatio: '1 / 1',
              position: 'relative'
            }}>
              <Box style={{ 
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%) scale(0.95)',
                width: '100%',
                height: '100%',
                display: 'flex',
                justifyContent: 'center',
                alignItems: 'center'
              }}>
                {previewComponent}
              </Box>
            </Box>
          </Card>
        </Grid.Col>

        {/* 設定パネル */}
        <Grid.Col span={12}>
          <Card 
            shadow="sm" 
            radius="lg" 
            p={30}
            style={{ 
              background: 'linear-gradient(135deg, #fff 0%, #f7fafc 100%)',
              border: '1px solid rgba(0,0,0,0.05)'
            }}
          >
            <Stack gap="xl">
              <Group justify="space-between" align="center" mb={10}>
                <Box>
                  <Text fw={700} size="lg">設定</Text>
                  <Text size="sm" c="dimmed" mt={5}>画像のサイズと品質を調整できます</Text>
                </Box>
                <ActionIcon variant="light" color="gray" size="lg" radius="xl">
                  <IconSettings size={20} />
                </ActionIcon>
              </Group>

              <Box>
                <Grid gutter={40}>
                  {/* サイズ設定 */}
                  <Grid.Col span={6}>
                    <Box>
                      <Group justify="space-between" mb={15}>
                        <Text fw={500} size="sm">サイズ</Text>
                        <Badge size="md" radius="xl" variant="light" px={15}>{size}px</Badge>
                      </Group>
                      <Box px={5}>
                        <Slider
                          value={size}
                          onChange={setSize}
                          min={300}
                          max={1000}
                          step={50}
                          marks={[
                            { value: 300, label: '300px' },
                            { value: 600, label: '600px' },
                            { value: 1000, label: '1000px' }
                          ]}
                          styles={(theme) => ({
                            root: {
                              padding: '10px 0'
                            },
                            track: {
                              backgroundColor: theme.colors.gray[2],
                              height: 6,
                              borderRadius: 3
                            },
                            bar: {
                              background: `linear-gradient(90deg, ${theme.colors.pink[4]} 0%, ${theme.colors.pink[6]} 100%)`,
                              height: 6,
                              borderRadius: 3
                            },
                            thumb: {
                              width: 20,
                              height: 20,
                              backgroundColor: 'white',
                              borderWidth: 2,
                              borderColor: theme.colors.pink[5],
                              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                              transition: 'transform 0.2s ease',
                              ':hover': {
                                transform: 'scale(1.1)',
                                boxShadow: '0 4px 8px rgba(0,0,0,0.15)'
                              }
                            },
                            mark: {
                              width: 6,
                              height: 6,
                              borderRadius: '50%',
                              transform: 'translateX(-50%) translateY(-50%)',
                              borderColor: theme.colors.gray[4]
                            },
                            markLabel: {
                              fontSize: theme.fontSizes.xs,
                              marginTop: 8,
                              color: theme.colors.gray[6]
                            }
                          })}
                        />
                      </Box>
                    </Box>
                  </Grid.Col>

                  {/* PNG品質設定 */}
                  <Grid.Col span={6}>
                    <Box>
                      <Group justify="space-between" mb={15}>
                        <Text fw={500} size="sm">PNG品質</Text>
                        <Badge size="md" radius="xl" variant="light" px={15}>{pngQuality}x</Badge>
                      </Group>
                      <Box px={5}>
                        <Slider
                          value={pngQuality}
                          onChange={setPngQuality}
                          min={1}
                          max={3}
                          step={1}
                          marks={[
                            { value: 1, label: '標準' },
                            { value: 2, label: '高品質' },
                            { value: 3, label: '印刷用' }
                          ]}
                          styles={(theme) => ({
                            root: {
                              padding: '10px 0'
                            },
                            track: {
                              backgroundColor: theme.colors.gray[2],
                              height: 6,
                              borderRadius: 3
                            },
                            bar: {
                              background: `linear-gradient(90deg, ${theme.colors.pink[4]} 0%, ${theme.colors.pink[6]} 100%)`,
                              height: 6,
                              borderRadius: 3
                            },
                            thumb: {
                              width: 20,
                              height: 20,
                              backgroundColor: 'white',
                              borderWidth: 2,
                              borderColor: theme.colors.pink[5],
                              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
                              transition: 'transform 0.2s ease',
                              ':hover': {
                                transform: 'scale(1.1)',
                                boxShadow: '0 4px 8px rgba(0,0,0,0.15)'
                              }
                            },
                            mark: {
                              width: 6,
                              height: 6,
                              borderRadius: '50%',
                              transform: 'translateX(-50%) translateY(-50%)',
                              borderColor: theme.colors.gray[4]
                            },
                            markLabel: {
                              fontSize: theme.fontSizes.xs,
                              marginTop: 8,
                              color: theme.colors.gray[6]
                            }
                          })}
                        />
                      </Box>
                    </Box>
                  </Grid.Col>
                </Grid>
              </Box>

              <Grid gutter={20} mt={10}>
                <Grid.Col span={6}>
                  <Button
                    fullWidth
                    size="lg"
                    radius="md"
                    leftSection={<IconDownload size={20} />}
                    variant="gradient"
                    gradient={{ from: '#FF69B4', to: '#FF1493', deg: 45 }}
                    style={{
                      boxShadow: '0 4px 14px rgba(255, 105, 180, 0.25)',
                      transition: 'all 0.2s ease',
                    }}
                    styles={{
                      root: {
                        ':hover': {
                          transform: 'translateY(-2px)',
                          boxShadow: '0 6px 20px rgba(255, 105, 180, 0.35)',
                        }
                      }
                    }}
                    onClick={handleSVGDownload}
                    loading={isDownloading}
                  >
                    SVGダウンロード
                  </Button>
                </Grid.Col>

                <Grid.Col span={6}>
                  <Button
                    fullWidth
                    size="lg"
                    radius="md"
                    leftSection={<IconDownload size={20} />}
                    variant="gradient"
                    gradient={{ from: '#FF69B4', to: '#FF1493', deg: 45 }}
                    style={{
                      boxShadow: '0 4px 14px rgba(255, 105, 180, 0.25)',
                      transition: 'all 0.2s ease',
                    }}
                    styles={{
                      root: {
                        ':hover': {
                          transform: 'translateY(-2px)',
                          boxShadow: '0 6px 20px rgba(255, 105, 180, 0.35)',
                        }
                      }
                    }}
                    onClick={handlePNGDownload}
                    loading={isPngDownloading}
                  >
                    PNGダウンロード
                  </Button>
                </Grid.Col>
              </Grid>
            </Stack>
          </Card>
        </Grid.Col>
      </Grid>
    </Box>
  );
} 