'use client';

import { CompatibilityData } from '@/types';

export default function CompatibilityResult({ compatibilityData }: { compatibilityData: CompatibilityData }) {
  const { result, targetPerson } = compatibilityData;
  
  // 相性鑑定結果が存在するか確認
  if (!result || !result.readings || Object.keys(result.readings).length === 0) {
    return (
      <div style={{ 
        padding: '20px', 
        backgroundColor: 'white', 
        borderRadius: '8px', 
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)', 
        border: '1px solid #e0e0e0',
        marginTop: '20px',
        textAlign: 'center'
      }}>
        <h2 style={{ 
          textAlign: 'center', 
          fontSize: '1.2rem', 
          fontWeight: 500, 
          margin: '0 0 20px 0',
          color: '#3490dc'
        }}>
          相性鑑定結果
        </h2>
        <p>相性鑑定結果を取得できませんでした。</p>
      </div>
    );
  }
  
  // テーマ名の日本語表示
  const themeLabels = {
    energy: '関係のエネルギー強度',
    emotional: '感情面・精神面の調和',
    challenge: '課題と学びの可能性',
    relationship_type: '適した関係性',
    stability: '長期的な安定性'
  };
  
  return (
    <div style={{ 
      padding: '20px', 
      backgroundColor: 'white', 
      borderRadius: '8px', 
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)', 
      border: '1px solid #e0e0e0',
      marginTop: '20px'
    }}>
      <h3 style={{fontSize: '1.4rem', textAlign: 'center', marginTop: 0, marginBottom: '15px', color: '#333'}}>
        相性鑑定結果
      </h3>

      {/* 相手の情報表示 */}
      <div style={{
        textAlign: 'center',
        marginBottom: '20px',
        padding: '10px',
        backgroundColor: '#f0f7ff',
        borderRadius: '6px'
      }}>
        <p style={{
          margin: '0',
          fontSize: '0.9rem',
          color: '#555'
        }}>
          <span style={{ fontWeight: 600 }}>相手：</span>
          {targetPerson.name || "名前なし"}様（生年月日：{targetPerson.birthdate || "不明"}）
        </p>
      </div>
      
      {/* テーマごとに表示 */}
      {Object.entries(result.readings).map(([theme, reading]) => (
        <div 
          key={theme}
          style={{ 
            padding: '15px', 
            backgroundColor: '#f8f9fa', 
            borderRadius: '8px', 
            border: '1px solid #e9ecef',
            marginBottom: '15px'
          }}
        >
          <h3 style={{ 
            fontSize: '1rem', 
            fontWeight: 600, 
            color: '#4BA3E3', 
            marginTop: 0, 
            marginBottom: '10px' 
          }}>
            {themeLabels[theme as keyof typeof themeLabels] || reading.title || '相性診断'}
          </h3>
          <p style={{ 
            whiteSpace: 'pre-wrap', 
            margin: 0, 
            fontSize: '0.9rem', 
            lineHeight: 1.5 
          }}>
            {reading.content || '相性診断結果が表示できません。'}
          </p>
        </div>
      ))}
    </div>
  );
} 