'use client';

import React from 'react';
import SimpleResult from '@/components/features/results/SimpleResult';

// サンプルデータ
const sampleData = {
  result: {
    main_star: {
      star_number: 1,
      name_jp: '一白水星',
      name_en: 'Sui Sei',
      element: '水',
      keywords: '知的,冷静,論理的,分析力',
      description: '一白水星は九星気学において最も知的で論理的な星とされています。水の性質を持ち、柔軟性と適応力に優れ、どんな環境にも順応することができます。その強い分析力は物事を客観的に見ることを可能にし、状況を冷静に判断できます。'
    },
    month_star: {
      star_number: 7,
      name_jp: '七赤金星',
      name_en: 'Kin Sei',
      element: '金',
      keywords: '社交性,雄弁,明朗,表現力',
      description: '七赤金星は社交的で表現力に富んだ星です。金の性質を持ち、明るく華やかなエネルギーを放ちます。対人関係においては魅力的で人を惹きつける力があります。'
    },
    day_star: {
      star_number: 3,
      name_jp: '三碧木星',
      name_en: 'Moku Sei',
      element: '木',
      keywords: '創造性,先進的,成長,直感力',
      description: '三碧木星は創造性と成長の星です。木の性質を持ち、常に新しいアイデアを生み出し、前進していく力があります。直感力も強く、物事の本質を見抜く目を持っています。'
    },
    hour_star: { star_number: 4, name_jp: '四緑木星', element: '木' },
    year_star: { star_number: 9, name_jp: '九紫火星', element: '火' },
    birth_datetime: '1990-01-01T12:00:00',
    target_year: 2023
  },
  fullName: 'サンプル 太郎',
  birthdate: '1990/01/01',
  birthtime: '12:00',
  gender: '男性'
};

export default function SimplePage() {
  return (
    <div style={{ 
      maxWidth: '800px', 
      margin: '0 auto', 
      padding: '20px',
      backgroundColor: 'white',
      borderRadius: '8px',
      boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
    }}>
      <h1 style={{ textAlign: 'center', marginBottom: '20px' }}>九星気学 サンプル結果</h1>
      <SimpleResult resultData={sampleData} onReset={() => console.log('リセット')} />
    </div>
  );
} 