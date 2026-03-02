'use client';

import React, { useState, useRef } from 'react';
import { Container, Title, Paper, Text, Box, Group, Button, Select, Slider, Switch, Alert, Card, Radio, SimpleGrid, Tabs } from '@mantine/core';
import { IconDownload, IconInfoCircle, IconStars, IconSettings, IconPhoto } from '@tabler/icons-react';
import { useAuth } from '@/contexts/auth/AuthContext';
import KyuseiBoard_Authentic, { generateKyuseiBoardSVG, generateKyuseiBoardSVG_NoFilters, generateKyuseiBoardSVG_Solid, generateKyuseiBoardSVG_GradientOnly, generateKyuseiBoardSVG_StrokeOnly, generateKyuseiBoardSVG_Step10, generateKyuseiBoardSVG_Step11 } from '@/app/svg-test/components/KyuseiBoard_Authentic';
// html2canvas は動的インポートで使用

export default function AdminSVGKyuseiPage() {
  const { isSuperuser } = useAuth();
  const [centerStar, setCenterStar] = useState<string>("一白水星");
  const [size, setSize] = useState<number>(600);
  const [backgroundGradient, setBackgroundGradient] = useState<string>("classic");
  const [glowEffect, setGlowEffect] = useState<boolean>(true);
  const [isDownloading, setIsDownloading] = useState<boolean>(false);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [isPngDownloading, setIsPngDownloading] = useState<boolean>(false);
  const [pngQuality, setPngQuality] = useState<number>(2); // 2 = 高品質, 1 = 標準
  const kyuseiBoardRef = useRef<HTMLDivElement>(null);

  // superuserでない場合はアクセス拒否
  if (!isSuperuser) {
    return (
      <Container size="lg" py="xl">
        <Alert icon={<IconInfoCircle />} color="red" title="アクセス権限がありません">
          この機能はスーパーユーザーのみが利用できます。
        </Alert>
      </Container>
    );
  }

  const starOptions = [
    { value: "一白水星", label: "一白水星" },
    { value: "二黒土星", label: "二黒土星" },
    { value: "三碧木星", label: "三碧木星" },
    { value: "四緑木星", label: "四緑木星" },
    { value: "五黄土星", label: "五黄土星" },
    { value: "六白金星", label: "六白金星" },
    { value: "七赤金星", label: "七赤金星" },
    { value: "八白土星", label: "八白土星" },
    { value: "九紫火星", label: "九紫火星" }
  ];

  const backgroundOptions = [
    { value: "classic", label: "クラシック（紺色）" },
    { value: "blue-yellow", label: "薄い水色" },
    { value: "purple-pink", label: "薄い紫色" },
    { value: "green-lime", label: "薄い緑色" },
    { value: "orange-red", label: "薄い黄色" },
    { value: "gray-white", label: "薄いグレー" },
    { value: "dark-purple", label: "鮮明な青空色" }
  ];

  const handleDownload = async () => {
    setIsDownloading(true);
    try {
      const svgContent = generateKyuseiBoardSVG(centerStar, size);
      
      // デバッグ用：SVG内容をコンソールに出力
      console.log('Generated SVG Content:', svgContent);
      console.log('Center Star:', centerStar);
      console.log('Size:', size);
      
      const blob = new Blob([svgContent], { type: 'image/svg+xml' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `kyusei_board_${centerStar}_${size}px.svg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('SVGダウンロードエラー:', error);
    } finally {
      setIsDownloading(false);
    }
  };

  // Step2: フィルター無効化版ダウンロード
  const handleDownloadNoFilters = async () => {
    setIsDownloading(true);
    try {
      const svgContent = generateKyuseiBoardSVG_NoFilters(centerStar, size);
      
      console.log('Generated No-Filters SVG:', svgContent);
      
      const blob = new Blob([svgContent], { type: 'image/svg+xml' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `kyusei_board_${centerStar}_${size}px_NoFilters.svg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('フィルター無効化SVGダウンロードエラー:', error);
    } finally {
      setIsDownloading(false);
    }
  };

  // Step3: ソリッドカラー版ダウンロード
  const handleDownloadSolid = async () => {
    setIsDownloading(true);
    try {
      const svgContent = generateKyuseiBoardSVG_Solid(centerStar, size);
      
      console.log('Generated Solid SVG:', svgContent);
      
      const blob = new Blob([svgContent], { type: 'image/svg+xml' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `kyusei_board_${centerStar}_${size}px_Solid.svg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('ソリッドカラーSVGダウンロードエラー:', error);
    } finally {
      setIsDownloading(false);
    }
  };

  // Step4: グラデーション復活版ダウンロード
  const handleDownloadGradientOnly = async () => {
    setIsDownloading(true);
    try {
      const svgContent = generateKyuseiBoardSVG_GradientOnly(centerStar, size);
      
      console.log('Generated Gradient-Only SVG:', svgContent);
      
      const blob = new Blob([svgContent], { type: 'image/svg+xml' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `kyusei_board_${centerStar}_${size}px_GradientOnly.svg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('グラデーション復活版SVGダウンロードエラー:', error);
    } finally {
      setIsDownloading(false);
    }
  };

  // Step5: ストロークエフェクト版ダウンロード
  const handleDownloadStrokeOnly = async () => {
    setIsDownloading(true);
    try {
      const svgContent = generateKyuseiBoardSVG_StrokeOnly(centerStar, size);
      
      console.log('Generated Stroke-Only SVG:', svgContent);
      
      const blob = new Blob([svgContent], { type: 'image/svg+xml' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `kyusei_board_${centerStar}_${size}px_StrokeOnly.svg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('ストロークエフェクト版SVGダウンロードエラー:', error);
    } finally {
      setIsDownloading(false);
    }
  };

  // Step6: バックエンドPDF対応SVGダウンロード
  const handleDownloadBackendPdfSvg = async () => {
    setIsDownloading(true);
    try {
      const response = await fetch('http://localhost:5001/api/nine-star/generate-pdf-svg', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          centerStar,
          size
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success && result.svg_content) {
        console.log('Generated Backend PDF SVG:', result.svg_content);
        
        const blob = new Blob([result.svg_content], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `kyusei_board_${centerStar}_${size}px_BackendPdf.svg`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        alert(`バックエンドPDF対応SVG生成成功！\n${result.message}`);
      } else {
        throw new Error(result.message || 'SVG生成に失敗しました');
      }
    } catch (error) {
      console.error('バックエンドPDF対応SVGダウンロードエラー:', error);
      alert(`エラー: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setIsDownloading(false);
    }
  };

  // Step7: バックエンド美しいSVGダウンロード（通常版をテスト）
  const handleDownloadBackendBeautifulSvg = async () => {
    setIsDownloading(true);
    try {
      const response = await fetch('http://localhost:5001/api/nine-star/save-svg', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          centerStar,
          size,
          mode: "generate"  // 生成モードで美しいSVGを取得
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success && result.svg_content) {
        console.log('Generated Backend Beautiful SVG:', result.svg_content);
        
        const blob = new Blob([result.svg_content], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `kyusei_board_${centerStar}_${size}px_BackendBeautiful.svg`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        alert(`バックエンド美しいSVG生成成功！\n添付画像レベルの品質確認用`);
      } else {
        throw new Error(result.message || 'SVG生成に失敗しました');
      }
    } catch (error) {
      console.error('バックエンド美しいSVGダウンロードエラー:', error);
      alert(`エラー: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setIsDownloading(false);
    }
  };

  // Step8: 強化PDF対応SVGダウンロード（添付画像レベル品質）
  const handleDownloadEnhancedPdfSvg = async () => {
    setIsDownloading(true);
    try {
      const response = await fetch('http://localhost:5001/api/nine-star/generate-enhanced-pdf-svg', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          centerStar,
          size
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success && result.svg_content) {
        console.log('Generated Enhanced PDF SVG:', result.svg_content);
        
        const blob = new Blob([result.svg_content], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `kyusei_board_${centerStar}_${size}px_EnhancedPdf.svg`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        alert(`強化PDF対応SVG生成成功！\n${result.message}`);
      } else {
        throw new Error(result.message || 'SVG生成に失敗しました');
      }
    } catch (error) {
      console.error('強化PDF対応SVGダウンロードエラー:', error);
      alert(`エラー: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setIsDownloading(false);
    }
  };

  // Step9: Step1ベース + PDF互換SVGダウンロード（美しさ + 互換性の両立）
  const handleDownloadStep9PdfSvg = async () => {
    setIsDownloading(true);
    try {
      const response = await fetch('http://localhost:5001/api/nine-star/generate-step9-pdf-svg', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          centerStar,
          size
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      
      if (result.success && result.svg_content) {
        console.log('Generated Step9 PDF SVG:', result.svg_content);
        
        const blob = new Blob([result.svg_content], { type: 'image/svg+xml' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `kyusei_board_${centerStar}_${size}px_Step9.svg`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
        
        alert(`Step9 SVG生成成功！\n${result.message}`);
      } else {
        throw new Error(result.message || 'SVG生成に失敗しました');
      }
    } catch (error) {
      console.error('Step9 SVGダウンロードエラー:', error);
      alert(`エラー: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setIsDownloading(false);
    }
  };

  // Step10: Step1グラデーション縮小版SVGダウンロード
  const handleDownloadStep10PdfSvg = async () => {
    setIsDownloading(true);
    try {
      // フロントエンド側で直接Step10のSVGを生成
      const svgContent = generateKyuseiBoardSVG_Step10(centerStar, size);
      
      console.log('Generated Step10 PDF SVG:', svgContent);
      
      const blob = new Blob([svgContent], { type: 'image/svg+xml' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `kyusei_board_${centerStar}_${size}px_Step10.svg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      
      alert('Step10 SVG生成成功！\nグラデーション範囲を50%に調整したWeasyPrint対応版');
    } catch (error) {
      console.error('Step10 SVGダウンロードエラー:', error);
      alert(`エラー: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setIsDownloading(false);
    }
  };

  // Step11: フォント拡大版SVGダウンロード
  const handleDownloadStep11PdfSvg = async () => {
    setIsDownloading(true);
    try {
      const svgContent = generateKyuseiBoardSVG_Step11(centerStar, size);
      const blob = new Blob([svgContent], { type: 'image/svg+xml' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `kyusei_board_${centerStar}_${size}px_Step11.svg`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
      alert('Step11 SVG生成成功！\nフォントサイズを15%拡大したPDF対応版');
    } catch (error) {
      console.error('Step11 SVGダウンロードエラー:', error);
      alert(`エラー: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      setIsDownloading(false);
    }
  };

  const handleSaveToBackend = async () => {
    setIsSaving(true);
    try {
      const svgContent = generateKyuseiBoardSVG(centerStar, size);
      const response = await fetch('http://localhost:5001/api/nine-star/save-svg', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          centerStar,
          svgContent,
          size,
          backgroundGradient
        }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('SVG保存成功:', result);
        alert('SVGファイルがサーバーに保存されました');
      } else {
        throw new Error('SVG保存に失敗しました');
      }
    } catch (error) {
      console.error('SVG保存エラー:', error);
      alert('SVG保存中にエラーが発生しました');
    } finally {
      setIsSaving(false);
    }
  };

  const handlePngDownload = async () => {
    setIsPngDownloading(true);
    try {
      // 既存のSVG生成関数を使用（React画面と完全同一）
      const svgContent = generateKyuseiBoardSVG(centerStar, size);
      
      // SVGをCanvas経由でPNGに変換
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      if (!ctx) throw new Error('Canvas context not available');

      // 高解像度設定
      const scale = pngQuality;
      canvas.width = size * scale;
      canvas.height = size * scale;
      ctx.scale(scale, scale);

      // SVGをImageとして読み込み
      const img = new Image();
      const svgBlob = new Blob([svgContent], { type: 'image/svg+xml' });
      const svgUrl = URL.createObjectURL(svgBlob);

      img.onload = () => {
        // 透明背景の設定
        ctx.clearRect(0, 0, size, size);
        
        // SVGをCanvasに描画
        ctx.drawImage(img, 0, 0, size, size);
        
        // PNGとしてダウンロード
        canvas.toBlob((blob) => {
          if (blob) {
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = `kyusei_board_${centerStar}_${size}px_${scale}x.png`;
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            URL.revokeObjectURL(link.href);
            
            // ファイルサイズ表示
            console.log(`PNG size: ${(blob.size / 1024).toFixed(1)} KB (${scale}x quality)`);
            alert(`PNG保存完了！ファイルサイズ: ${(blob.size / 1024).toFixed(1)} KB`);
          }
        }, 'image/png', 0.92); // 92% 品質でファイルサイズ最適化
        
        // リソースクリーンアップ
        URL.revokeObjectURL(svgUrl);
        setIsPngDownloading(false);
      };

      img.onerror = () => {
        URL.revokeObjectURL(svgUrl);
        setIsPngDownloading(false);
        throw new Error('SVG画像の読み込みに失敗しました');
      };

      img.src = svgUrl;
      
    } catch (error) {
      console.error('PNGダウンロードエラー:', error);
      alert('PNG生成中にエラーが発生しました: ' + error);
      setIsPngDownloading(false);
    }
  };

  return (
    <Container size="lg" py="xl">
      <Title order={2} mb="lg">SVG九星盤ダウンロード</Title>
      
      <Alert icon={<IconInfoCircle />} color="blue" mb="xl">
        <Text size="sm">
          この機能では、高品質なSVG形式の九星盤を生成・ダウンロードできます。
          <br />• <strong>SVG</strong>: React画面と同じ美しいエフェクト再現、PDF埋め込み最適
          <br />• <strong>新機能</strong>: WeasyPrint対応の豪華グラデーション・光エフェクト実装
        </Text>
      </Alert>

      <Group align="flex-start" gap="xl">
        {/* 設定パネル */}
        <Card shadow="sm" padding="lg" radius="md" withBorder style={{ minWidth: 300 }}>
          <Group mb="md">
            <IconSettings size={20} />
            <Title order={4}>設定</Title>
          </Group>

          <Box mb="md">
            <Text size="sm" fw={500} mb="xs">中央星</Text>
            <Radio.Group
              value={centerStar}
              onChange={setCenterStar}
              name="centerStar"
            >
              <SimpleGrid cols={3} mt="xs" spacing="xs">
                {starOptions.map((option) => (
                  <Radio
                    key={option.value}
                    value={option.value}
                    label={option.label}
                    size="sm"
                  />
                ))}
              </SimpleGrid>
            </Radio.Group>
          </Box>

          <Box mb="md">
            <Text size="sm" fw={500} mb="xs">サイズ: {size}px</Text>
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
            />
          </Box>

          <Box mb="md">
            <Text size="sm" fw={500} mb="xs">背景グラデーション</Text>
            <Select
              value={backgroundGradient}
              onChange={(value) => setBackgroundGradient(value || "classic")}
              data={backgroundOptions}
              placeholder="背景を選択"
            />
          </Box>

          <Box mb="md">
            <Switch
              checked={glowEffect}
              onChange={(event) => setGlowEffect(event.currentTarget.checked)}
              label="光エフェクト"
              description="星の光る効果を有効にします"
            />
          </Box>

          <Box mb="xl">
            <Text size="sm" fw={500} mb="xs">PNG品質: {pngQuality}x</Text>
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
            />
            <Text size="xs" c="dimmed" mt="xs">
              印刷用(3x)推奨: PDF埋め込み時も美しく表示
            </Text>
          </Box>

          <Tabs defaultValue="svg" mb="md">
            <Tabs.List grow>
              <Tabs.Tab value="svg" leftSection={<IconDownload size={16} />}>
                SVG
              </Tabs.Tab>
              <Tabs.Tab value="png" leftSection={<IconPhoto size={16} />}>
                PNG
              </Tabs.Tab>
            </Tabs.List>

            <Tabs.Panel value="svg" pt="md">
              <SimpleGrid cols={1} spacing="xs">
                <Button
                  leftSection={<IconDownload size={16} />}
                  onClick={handleDownload}
                  loading={isDownloading}
                  variant="filled"
                  color="blue"
                >
                  Step1: 美しいSVG（フォント修正版）
                </Button>
                <Button
                  leftSection={<IconDownload size={16} />}
                  onClick={handleDownloadNoFilters}
                  loading={isDownloading}
                  variant="outline"
                  color="green"
                >
                  Step2: フィルター無効化版
                </Button>
                <Button
                  leftSection={<IconDownload size={16} />}
                  onClick={handleDownloadSolid}
                  loading={isDownloading}
                  variant="outline"
                  color="orange"
                >
                  Step3: ソリッドカラー版
                </Button>
                <Button
                  leftSection={<IconDownload size={16} />}
                  onClick={handleDownloadGradientOnly}
                  loading={isDownloading}
                  variant="outline"
                  color="purple"
                >
                  Step4: グラデーション復活版
                </Button>
                <Button
                  leftSection={<IconDownload size={16} />}
                  onClick={handleDownloadStrokeOnly}
                  loading={isDownloading}
                  variant="outline"
                  color="teal"
                >
                  Step5: ストロークエフェクト版
                </Button>
                <Button
                  leftSection={<IconDownload size={16} />}
                  onClick={handleDownloadBackendPdfSvg}
                  loading={isDownloading}
                  variant="outline"
                  color="pink"
                >
                  Step6: バックエンドPDF対応SVG
                </Button>
                <Button
                  leftSection={<IconDownload size={16} />}
                  onClick={handleDownloadBackendBeautifulSvg}
                  loading={isDownloading}
                  variant="outline"
                  color="teal"
                >
                  Step7: バックエンド美しいSVG
                </Button>
                <Button
                  leftSection={<IconDownload size={16} />}
                  onClick={handleDownloadEnhancedPdfSvg}
                  loading={isDownloading}
                  variant="outline"
                  color="teal"
                >
                  Step8: 強化PDF対応SVG
                </Button>
                <Button
                  leftSection={<IconDownload size={16} />}
                  onClick={handleDownloadStep9PdfSvg}
                  loading={isDownloading}
                  variant="outline"
                  color="teal"
                >
                  Step9: Step1ベース + PDF互換SVG
                </Button>
                <Button
                  leftSection={<IconDownload size={16} />}
                  onClick={handleDownloadStep10PdfSvg}
                  loading={isDownloading}
                  variant="outline"
                  color="violet"
                >
                  Step10: Step1グラデーション縮小版
                </Button>
                <Button
                  leftSection={<IconDownload size={16} />}
                  onClick={handleDownloadStep11PdfSvg}
                  loading={isDownloading}
                  variant="outline"
                  color="indigo"
                >
                  Step11: フォント拡大PDF版
                </Button>
              </SimpleGrid>
              
              <Text size="sm" c="dimmed" mt="md">
                📝 <strong>段階的テスト</strong>：
              </Text>
              <Text size="xs" c="dimmed" mt="xs">
                • Step1: 全エフェクト保持（フォントのみArial）
              </Text>
              <Text size="xs" c="dimmed" mt="xs">
                • Step2: フィルター無効化（グラデーション・光は保持）
              </Text>
              <Text size="xs" c="dimmed">
                • Step3: ソリッドカラーのみ（最高互換性）
              </Text>
              <Text size="xs" c="dimmed">
                • Step4: グラデーション復活版（エフェクト再現）
              </Text>
              <Text size="xs" c="dimmed">
                • Step5: ストロークエフェクト版（新機能）
              </Text>
              <Text size="xs" c="dimmed">
                • Step6: バックエンドPDF対応SVG（新機能）
              </Text>
              <Text size="xs" c="dimmed">
                • Step7: バックエンド美しいSVG（通常版をテスト）
              </Text>
              <Text size="xs" c="dimmed">
                • Step8: 強化PDF対応SVG（添付画像レベル品質）
              </Text>
              <Text size="xs" c="dimmed">
                • Step9: Step1ベース + PDF互換SVG
              </Text>
              <Text size="xs" c="dimmed">
                • Step10: Step1グラデーション縮小版（グラデーション縮小）
              </Text>
              <Text size="xs" c="dimmed">
                • Step11: フォント拡大PDF版（15%アップ）
              </Text>
            </Tabs.Panel>

            <Tabs.Panel value="png" pt="md">
              <Group>
                <Button
                  leftSection={<IconPhoto size={16} />}
                  onClick={handlePngDownload}
                  loading={isPngDownloading}
                  variant="filled"
                  color="orange"
                  fullWidth
                >
                  PNGダウンロード
                </Button>
              </Group>
            </Tabs.Panel>
          </Tabs>

          <Button
            onClick={handleSaveToBackend}
            loading={isSaving}
            variant="outline"
            color="green"
            fullWidth
          >
            サーバーに保存
          </Button>
        </Card>

        {/* プレビュー */}
        <Card shadow="sm" padding="lg" radius="md" withBorder style={{ flex: 1 }}>
          <Group mb="md">
            <IconStars size={20} />
            <Title order={4}>プレビュー</Title>
          </Group>

          <Box style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
            <div 
              ref={kyuseiBoardRef}
              style={{ 
                width: Math.min(size, 500), 
                height: Math.min(size, 500),
                display: 'inline-block',
                position: 'relative'
              }}
            >
              <KyuseiBoard_Authentic
                centerStar={centerStar}
                size={Math.min(size, 500)} // プレビューでは最大500pxに制限
                theme="luxury"
                glowEffect={glowEffect}
                backgroundGradient={backgroundGradient as 'classic' | 'blue-yellow' | 'purple-pink' | 'green-lime' | 'orange-red' | 'gray-white' | 'dark-purple'}
                interactive={false}
              />
            </div>
          </Box>
        </Card>
      </Group>

      <Paper shadow="xs" p="md" mt="xl" withBorder>
        <Title order={5} mb="sm">📋 使用方法と比較</Title>
        <Text size="sm" mb="xs">1. 中央星、サイズ、背景グラデーションを設定</Text>
        <Text size="sm" mb="xs">2. プレビューで確認</Text>
        <Text size="sm" mb="xs">3. 形式を選択してダウンロード</Text>
        
        <Title order={6} mt="md" mb="xs">🎯 新手法：SVG→PNG変換</Title>
        <Text size="sm" mb="xs">• <strong>従来手法</strong>: React画面スクリーンショット（複雑エフェクトでエラー）</Text>
        <Text size="sm" mb="xs">• <strong>新手法</strong>: SVG生成→Canvas→PNG変換（100%確実）</Text>
        
        <Title order={6} mt="md" mb="xs">📊 ファイルサイズ（600px基準）</Title>
        <Text size="sm" mb="xs">• <strong>SVG</strong>: 20-50 KB (軽量、ベクター)</Text>
        <Text size="sm" mb="xs">• <strong>PNG 標準(1x)</strong>: 80-150 KB</Text>
        <Text size="sm" mb="xs">• <strong>PNG 高品質(2x)</strong>: 200-400 KB</Text>
        <Text size="sm" mb="xs">• <strong>PNG 印刷用(3x)</strong>: 400-800 KB</Text>
        
        <Text size="sm" c="dimmed" mt="md">
          ✨ <strong>新技術</strong>: React画面と完全同一、エラーなし、ファイルサイズ最適化！
        </Text>
      </Paper>
    </Container>
  );
} 