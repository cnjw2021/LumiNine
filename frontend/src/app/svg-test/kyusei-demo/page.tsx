'use client';

import React, { useState } from 'react';
import KyuseiBoard_Authentic, { generateKyuseiBoardSVG } from '../components/KyuseiBoard_Authentic';
import Link from 'next/link';

export const dynamic = 'force-dynamic';

export default function KyuseiDemoPage() {
  const [selectedCenterStar, setSelectedCenterStar] = useState('一白水星');
  const [selectedTheme, setSelectedTheme] = useState<'luxury' | 'minimal' | 'classic'>('luxury');
  const [boardSize, setBoardSize] = useState(600);
  const [isInteractive, setIsInteractive] = useState(true);
  const [isGlowEffect, setIsGlowEffect] = useState(false);
  const [backgroundGradient, setBackgroundGradient] = useState<'classic' | 'blue-yellow' | 'purple-pink' | 'green-lime' | 'orange-red' | 'gray-white' | 'dark-purple'>('classic');

  const nineStars = [
    '一白水星', '二黒土星', '三碧木星', '四緑木星', '五黄土星',
    '六白金星', '七赤金星', '八白土星', '九紫火星'
  ];

  const starInfo = {
    '一白水星': { element: '水', color: '#3B82F6', description: '水の性質を持つ星。知恵、直感力' },
    '二黒土星': { element: '土', color: '#F59E0B', description: '土の性質を持つ星。堅実、母性' },
    '三碧木星': { element: '木', color: '#22C55E', description: '木の性質を持つ星。成長、活力' },
    '四緑木星': { element: '木', color: '#22C55E', description: '木の性質を持つ星。調和、協調' },
    '五黄土星': { element: '土', color: '#F59E0B', description: '土の性質を持つ星。中心、変化' },
    '六白金星': { element: '金', color: '#D4AF37', description: '金の性質を持つ星。権威、父性' },
    '七赤金星': { element: '金', color: '#D4AF37', description: '金の性質を持つ星。喜び、社交' },
    '八白土星': { element: '土', color: '#F59E0B', description: '土の性質を持つ星。変革、山' },
    '九紫火星': { element: '火', color: '#EF4444', description: '火の性質を持つ星。知性、美' }
  } as const;

  // SVGダウンロード機能
  const downloadSVG = () => {
    const svgContent = generateKyuseiBoardSVG(selectedCenterStar, boardSize);
    const blob = new Blob([svgContent], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `kyusei-board-${selectedCenterStar}.svg`;
    a.click();
    URL.revokeObjectURL(url);
  };

  // バックエンドに保存機能
  const saveSVGToBackend = async () => {
    const svgContent = generateKyuseiBoardSVG(selectedCenterStar, boardSize);
    
    try {
      const response = await fetch('http://localhost:5001/api/nine-star/save-svg', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          centerStar: selectedCenterStar,
          svgContent: svgContent,
          size: boardSize,
          backgroundGradient: backgroundGradient
        })
      });
      
      if (response.ok) {
        const result = await response.json();
        console.log('SVG saved successfully:', result);
        alert('SVGがバックエンドに保存されました！');
      } else {
        const error = await response.json();
        console.error('Error saving SVG:', error);
        alert('SVG保存に失敗しました: ' + error.error);
      }
    } catch (error) {
      console.error('Error saving SVG:', error);
      alert('SVG保存中にエラーが発生しました');
    }
  };

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif', background: '#f8f9fa', minHeight: '100vh' }}>
      <h1 style={{ textAlign: 'center', color: '#1f2937', marginBottom: '30px' }}>
        九星気学 - 正確な配置デモ
      </h1>
      
      {/* コントロールパネル */}
      <div style={{ 
        marginBottom: '30px', 
        display: 'flex', 
        gap: '20px', 
        flexWrap: 'wrap',
        justifyContent: 'center',
        background: 'white',
        padding: '20px',
        borderRadius: '10px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
      }}>
        <div>
          <label style={{ fontWeight: 'bold', marginRight: '10px' }}>中央の星: </label>
          <select 
            value={selectedCenterStar} 
            onChange={(e) => setSelectedCenterStar(e.target.value)}
            style={{ padding: '5px', borderRadius: '5px', border: '1px solid #ccc' }}
          >
            {nineStars.map(star => (
              <option key={star} value={star}>{star}</option>
            ))}
          </select>
        </div>
        
        <div>
          <label style={{ fontWeight: 'bold', marginRight: '10px' }}>テーマ: </label>
          <select 
            value={selectedTheme} 
            onChange={(e) => setSelectedTheme(e.target.value as 'luxury' | 'minimal' | 'classic')}
            style={{ padding: '5px', borderRadius: '5px', border: '1px solid #ccc' }}
          >
            <option value="luxury">Luxury (高級感)</option>
            <option value="minimal">Minimal (ミニマル)</option>
            <option value="classic">Classic (クラシック)</option>
          </select>
        </div>
        
        <div>
          <label style={{ fontWeight: 'bold', marginRight: '10px' }}>サイズ: </label>
          <input 
            type="range" 
            min="400" 
            max="800" 
            value={boardSize} 
            onChange={(e) => setBoardSize(Number(e.target.value))}
            style={{ marginRight: '10px' }}
          />
          <span>{boardSize}px</span>
        </div>
        
        <div>
          <label style={{ fontWeight: 'bold' }}>
            <input 
              type="checkbox" 
              checked={isInteractive} 
              onChange={(e) => setIsInteractive(e.target.checked)}
              style={{ marginRight: '5px' }}
            />
            インタラクティブ
          </label>
        </div>
        
        <div>
          <label style={{ fontWeight: 'bold' }}>
            <input 
              type="checkbox" 
              checked={isGlowEffect} 
              onChange={(e) => setIsGlowEffect(e.target.checked)}
              style={{ marginRight: '5px' }}
            />
            光るエフェクト
          </label>
        </div>
      </div>

      {/* 背景グラデーション選択 */}
      <div style={{ 
        marginBottom: '30px',
        background: 'white',
        padding: '20px',
        borderRadius: '10px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
      }}>
        <h3 style={{ color: '#1f2937', marginBottom: '15px', fontSize: '18px' }}>🎨 背景グラデーション選択</h3>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', 
          gap: '12px',
          alignItems: 'start'
        }}>
          {[
            { value: 'classic', label: 'クラシック', gradient: 'linear-gradient(135deg, #0F0F23, #1A1A3E, #2D1B69)' },
            { value: 'blue-yellow', label: '薄い水色', gradient: 'radial-gradient(circle at 30% 20%, rgba(224, 242, 254, 0.6) 0%, rgba(191, 219, 254, 0.4) 50%, rgba(147, 197, 253, 0.3) 100%)' },
            { value: 'purple-pink', label: '薄い紫色', gradient: 'radial-gradient(circle at 30% 20%, rgba(243, 232, 255, 0.6) 0%, rgba(233, 213, 255, 0.4) 50%, rgba(221, 214, 254, 0.3) 100%)' },
            { value: 'green-lime', label: '薄い緑色', gradient: 'radial-gradient(circle at 30% 20%, rgba(220, 252, 231, 0.6) 0%, rgba(187, 247, 208, 0.4) 50%, rgba(167, 243, 208, 0.3) 100%)' },
            { value: 'orange-red', label: '薄い黄色', gradient: 'radial-gradient(circle at 30% 20%, rgba(254, 240, 138, 0.6) 0%, rgba(253, 224, 71, 0.4) 50%, rgba(251, 191, 36, 0.3) 100%)' },
            { value: 'gray-white', label: '薄いグレー', gradient: 'radial-gradient(circle at 30% 20%, rgba(249, 250, 251, 0.8) 0%, rgba(243, 244, 246, 0.6) 50%, rgba(229, 231, 235, 0.4) 100%)' },
            { value: 'dark-purple', label: '青空色', gradient: 'radial-gradient(circle at 30% 20%, rgba(135, 206, 250, 0.8) 0%, rgba(147, 197, 253, 0.6) 50%, rgba(191, 219, 254, 0.4) 100%)' }
          ].map((option) => (
            <label 
              key={option.value}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px',
                borderRadius: '8px',
                border: backgroundGradient === option.value ? '2px solid #3b82f6' : '2px solid transparent',
                background: backgroundGradient === option.value ? '#f0f9ff' : 'transparent',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                fontSize: '14px'
              }}
            >
              <input
                type="radio"
                name="backgroundGradient"
                value={option.value}
                checked={backgroundGradient === option.value}
                onChange={(e) => setBackgroundGradient(e.target.value as typeof backgroundGradient)}
                style={{ margin: '0' }}
              />
              <div 
                style={{
                  width: '24px',
                  height: '24px',
                  borderRadius: '50%',
                  background: option.gradient,
                  border: '1px solid #e5e7eb',
                  flexShrink: 0
                }}
              />
              <span style={{ color: '#374151', fontWeight: backgroundGradient === option.value ? 'bold' : 'normal' }}>
                {option.label}
              </span>
            </label>
          ))}
        </div>
      </div>

      {/* 中央の星の情報表示 */}
      <div style={{ 
        marginBottom: '30px', 
        textAlign: 'center',
        background: 'white',
        padding: '15px',
        borderRadius: '10px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
      }}>
        <h3 style={{ color: starInfo[selectedCenterStar as keyof typeof starInfo].color, margin: '0 0 10px 0' }}>
          {selectedCenterStar} (中央) {isGlowEffect && <span style={{ color: '#ff6b6b', fontSize: '12px' }}>✨光るエフェクト有効</span>}
        </h3>
        <p style={{ margin: '0', color: '#6b7280' }}>
          {starInfo[selectedCenterStar as keyof typeof starInfo].description}
        </p>
      </div>

      {/* メイン九星盤 */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        marginBottom: '40px',
        background: 'white',
        padding: '20px',
        borderRadius: '15px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.1)'
      }}>
        <KyuseiBoard_Authentic 
          centerStar={selectedCenterStar}
          theme={selectedTheme}
          size={boardSize}
          interactive={isInteractive}
          glowEffect={isGlowEffect}
          backgroundGradient={backgroundGradient}
        />
      </div>

      {/* 九星の一覧表示 */}
      <div style={{ marginBottom: '40px' }}>
        <h2 style={{ textAlign: 'center', color: '#1f2937', marginBottom: '20px' }}>
          九星一覧
        </h2>
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', 
          gap: '15px' 
        }}>
          {nineStars.map(star => (
            <div 
              key={star}
              style={{
                background: selectedCenterStar === star ? '#f0f9ff' : 'white',
                border: selectedCenterStar === star ? '2px solid #3b82f6' : '1px solid #e5e7eb',
                borderRadius: '10px',
                padding: '15px',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                boxShadow: selectedCenterStar === star ? '0 4px 15px rgba(59, 130, 246, 0.2)' : '0 2px 5px rgba(0,0,0,0.1)'
              }}
              onClick={() => setSelectedCenterStar(star)}
            >
              <h4 style={{ 
                margin: '0 0 5px 0', 
                color: starInfo[star as keyof typeof starInfo].color,
                fontSize: '16px'
              }}>
                {star}
              </h4>
              <p style={{ 
                margin: '0', 
                fontSize: '14px',
                color: '#6b7280'
              }}>
                {starInfo[star as keyof typeof starInfo].description}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* 追加のデモページへのリンク */}
      <div style={{ 
        marginBottom: '30px',
        display: 'flex',
        gap: '15px',
        justifyContent: 'center',
        flexWrap: 'wrap'
      }}>
        <Link href="/svg-test/kyusei-demo/usage-demo" style={{
          display: 'inline-block',
          padding: '10px 20px',
          background: '#8b5cf6',
          color: 'white',
          textDecoration: 'none',
          borderRadius: '8px',
          fontSize: '14px',
          fontWeight: 'bold',
          transition: 'background 0.3s ease'
        }}>
          使用方法とAPI →
        </Link>
      </div>

      {/* 使用方法の説明 */}
      <div style={{ 
        background: 'white',
        padding: '20px',
        borderRadius: '10px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{ color: '#1f2937', marginBottom: '15px' }}>九星気学の特徴</h2>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
          <div>
            <h3 style={{ color: '#3b82f6', marginBottom: '10px' }}>🎯 正確な方位配置</h3>
            <p style={{ color: '#6b7280', lineHeight: '1.6' }}>
              九星気学の伝統的な方位配置を正確に再現。北が下、南が上の配置で、
              本格的な九星気学の学習と実践に対応。
            </p>
          </div>
          <div>
            <h3 style={{ color: '#8b5cf6', marginBottom: '10px' }}>🎨 多彩なテーマ</h3>
            <p style={{ color: '#6b7280', lineHeight: '1.6' }}>
              Luxury（高級感）、Minimal（ミニマル）、Classic（クラシック）の
              3つのテーマから選択可能。用途に応じてスタイルを変更。
            </p>
          </div>
          <div>
            <h3 style={{ color: '#22c55e', marginBottom: '10px' }}>⚡ インタラクティブ</h3>
            <p style={{ color: '#6b7280', lineHeight: '1.6' }}>
              星をクリックして詳細情報を表示、ホバーエフェクト、
              動的なサイズ変更など、使いやすいインタラクション機能。
            </p>
          </div>
          <div>
            <h3 style={{ color: '#f59e0b', marginBottom: '10px' }}>✨ 視覚的エフェクト</h3>
            <p style={{ color: '#6b7280', lineHeight: '1.6' }}>
              美しいグラデーション、影効果、光るエフェクトで
              視覚的に魅力的な九星盤を実現。
            </p>
          </div>
        </div>
      </div>

      {/* 包括的な使用方法ガイド */}
      <div style={{ 
        background: 'white',
        padding: '25px',
        borderRadius: '12px',
        boxShadow: '0 4px 15px rgba(0,0,0,0.1)',
        marginTop: '30px'
      }}>
        <h2 style={{ color: '#1f2937', marginBottom: '20px', fontSize: '24px' }}>🚀 九星気学コンポーネント使用ガイド</h2>
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '25px', marginBottom: '25px' }}>
          <div style={{ padding: '20px', background: '#f8fafc', borderRadius: '10px', borderLeft: '4px solid #3b82f6' }}>
            <h3 style={{ color: '#3b82f6', marginBottom: '12px', fontSize: '18px' }}>📝 基本的な使用</h3>
            <pre style={{ 
              background: '#1f2937', 
              color: '#e5e7eb', 
              padding: '15px', 
              borderRadius: '8px', 
              fontSize: '13px',
              overflow: 'auto',
              margin: '0'
            }}>
{`// 最小限の設定
<KyuseiBoard_Authentic 
  centerStar="五黄土星"
/>

// 基本的なカスタマイズ
<KyuseiBoard_Authentic 
  centerStar="一白水星"
  theme="luxury"
  size={600}
  interactive={true}
  glowEffect={false}
  backgroundGradient="blue-yellow"
/>`}
            </pre>
          </div>

          <div style={{ padding: '20px', background: '#f0fdf4', borderRadius: '10px', borderLeft: '4px solid #22c55e' }}>
            <h3 style={{ color: '#22c55e', marginBottom: '12px', fontSize: '18px' }}>🎨 テーマとエフェクト</h3>
            <ul style={{ color: '#374151', fontSize: '14px', lineHeight: '1.6', paddingLeft: '20px', margin: '0' }}>
              <li><strong>luxury:</strong> 高級感のあるゴールド系グラデーション</li>
              <li><strong>minimal:</strong> シンプルで洗練されたデザイン</li>
              <li><strong>classic:</strong> 伝統的な落ち着いた色合い</li>
              <li><strong>glowEffect:</strong> 光るエフェクトで視覚的魅力を向上</li>
            </ul>
          </div>

          <div style={{ padding: '20px', background: '#fdf2f8', borderRadius: '10px', borderLeft: '4px solid #ec4899' }}>
            <h3 style={{ color: '#ec4899', marginBottom: '12px', fontSize: '18px' }}>⚙️ 全Props一覧</h3>
            <div style={{ fontSize: '13px', color: '#374151' }}>
              <div style={{ marginBottom: '8px' }}><strong>centerStar:</strong> 中央に配置する星（必須）</div>
              <div style={{ marginBottom: '8px' }}><strong>theme:</strong> &apos;luxury&apos; | &apos;minimal&apos; | &apos;classic&apos;</div>
              <div style={{ marginBottom: '8px' }}><strong>size:</strong> ボードサイズ（デフォルト: 600px）</div>
              <div style={{ marginBottom: '8px' }}><strong>interactive:</strong> インタラクション有効化</div>
              <div style={{ marginBottom: '8px' }}><strong>glowEffect:</strong> 光るエフェクト有効化</div>
              <div><strong>backgroundGradient:</strong> 背景グラデーション選択</div>
            </div>
          </div>

          <div style={{ padding: '20px', background: '#fffbeb', borderRadius: '10px', borderLeft: '4px solid #f59e0b' }}>
            <h3 style={{ color: '#f59e0b', marginBottom: '12px', fontSize: '18px' }}>🎨 背景グラデーションオプション</h3>
            <ul style={{ color: '#374151', fontSize: '14px', lineHeight: '1.6', paddingLeft: '20px', margin: '0' }}>
              <li><strong>classic:</strong> クラシックなダークブルーグラデーション</li>
              <li><strong>blue-yellow:</strong> 青から黄色への美しいコントラスト</li>
              <li><strong>purple-pink:</strong> 神秘的な紫からピンクへ</li>
              <li><strong>green-lime:</strong> 自然な緑からライムグリーンへ</li>
              <li><strong>orange-red:</strong> 情熱的なオレンジから赤へ</li>
              <li><strong>gray-white:</strong> シンプルなグレーから白へ</li>
              <li><strong>dark-purple:</strong> 深い紫から明るい紫へ</li>
            </ul>
          </div>

          <div style={{ padding: '20px', background: '#fff7ed', borderRadius: '10px', borderLeft: '4px solid #fb923c' }}>
            <h3 style={{ color: '#fb923c', marginBottom: '12px', fontSize: '18px' }}>💡 実装のコツ</h3>
            <ul style={{ color: '#374151', fontSize: '14px', lineHeight: '1.6', paddingLeft: '20px', margin: '0' }}>
              <li>SSRに対応させるため&apos;use client&apos;を追加</li>
              <li>PDF出力時はinteractive={false}に設定</li>
              <li>レスポンシブ対応にはsizeを動的に調整</li>
              <li>TypeScriptの型安全性を活用</li>
              <li>光るエフェクトは控えめに使用</li>
              <li>背景グラデーションは用途に応じて選択</li>
            </ul>
          </div>
        </div>

        <div style={{ 
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          padding: '20px',
          borderRadius: '10px',
          color: 'white'
        }}>
          <h3 style={{ color: 'white', marginBottom: '15px', fontSize: '18px' }}>✨ 高度な使用例</h3>
          <pre style={{ 
            background: 'rgba(0,0,0,0.3)', 
            color: '#e5e7eb', 
            padding: '15px', 
            borderRadius: '8px', 
            fontSize: '13px',
            overflow: 'auto',
            margin: '0'
          }}>
{`// 状態管理と組み合わせた動的な例
const [currentStar, setCurrentStar] = useState('一白水星');
const [userTheme, setUserTheme] = useState('luxury');
const [effectsEnabled, setEffectsEnabled] = useState(false);
const [bgGradient, setBgGradient] = useState('classic');

// 年月に基づく自動計算
const calculateCenterStar = (year: number, month: number) => {
  // 計算ロジック...
  return calculatedStar;
};

<KyuseiBoard_Authentic 
  centerStar={calculateCenterStar(2024, 3)}
  theme={userTheme}
  size={window.innerWidth < 768 ? 400 : 600}
  interactive={!isPrinting}
  glowEffect={effectsEnabled && !isPrinting}
  backgroundGradient={bgGradient}
/>`}
          </pre>
        </div>
      </div>

      {/* ナビゲーション */}
      <div style={{ marginTop: '40px', textAlign: 'center' }}>
        <Link 
          href="/svg-test" 
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            padding: '12px 24px',
            background: '#6b7280',
            color: 'white',
            textDecoration: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: 'bold',
            transition: 'background 0.3s ease'
          }}
        >
          ← SVGテストに戻る
        </Link>
      </div>

      {/* SVG保存ボタン */}
      <div style={{ 
        marginTop: '40px',
        display: 'flex',
        justifyContent: 'center',
        gap: '15px'
      }}>
        <button 
          onClick={downloadSVG}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#3B82F6',
            color: 'white',
            border: 'none',
            borderRadius: '0.5rem',
            cursor: 'pointer',
            fontSize: '1rem',
            fontWeight: '600',
            transition: 'background-color 0.2s'
          }}
          onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#2563EB'}
          onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#3B82F6'}
        >
          📥 SVGダウンロード
        </button>
        
        <button 
          onClick={saveSVGToBackend}
          style={{
            padding: '0.75rem 1.5rem',
            backgroundColor: '#10B981',
            color: 'white',
            border: 'none',
            borderRadius: '0.5rem',
            cursor: 'pointer',
            fontSize: '1rem',
            fontWeight: '600',
            transition: 'background-color 0.2s'
          }}
          onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#059669'}
          onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#10B981'}
        >
          💾 バックエンドに保存
        </button>
      </div>
    </div>
  );
} 