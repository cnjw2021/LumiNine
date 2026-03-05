'use client';

import ResultFortuneSection from './ResultFortuneSection';
import NumerologyStarInfo from './NumerologyStarInfo';
import ResultStarDisplay from './ResultStarDisplay';
import TemplateSelectionModal from './TemplateSelectionModal';
import { useEffect, useState } from 'react';
import { usePdfReport } from '@/hooks/usePdfReport';
import api from '@/utils/api';
import { useNineStarKiStore } from '@/stores/nineStarKiStore';
import { ResultProps, PdfJobResultDataMinimal, PartnerMinimal } from '@/types/results';
import { CalculationResult } from '@/types/stars';
import StarAttributesDisplay from './StarAttributesDisplay';
// Progress removed (modal handles display)


export default function Result({ resultData, onReset }: ResultProps) {
  const { result, fullName, birthdate } = resultData;
  const [showTemplateModal, setShowTemplateModal] = useState<boolean>(false);

  // PDF生成とプレビュー用のカスタムフック
  const {
    isGeneratingPdf,
    pdfProgress,
    handleDownloadPdf,
    handlePreviewReport
  } = usePdfReport({
    resultData,
    onActionComplete: () => setShowTemplateModal(false)
  });


  // テンプレート選択モーダルを開く
  const openTemplateModal = () => {
    setShowTemplateModal(true);
  };

  // テンプレート選択モーダルを閉じる
  const closeTemplateModal = () => {
    setShowTemplateModal(false);
  };


  if (!result) {
    return null;
  }

  const { main_star, month_star, day_star } = result;


  // カンマ区切りのキーワード文字列を処理する関数
  const processKeywords = (keywordsStr: string | null | undefined): string => {
    if (!keywordsStr) return '';
    // カンマと読点を「・」に置き換えて整形
    return keywordsStr.replace(/[,、]/g, '・').trim();
  };


  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      {/* 進捗バーはモーダル内オーバーレイで表示。ページ先頭のバーは不要 */}
      <div style={{
        padding: '20px',
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        border: '1px solid #e0e0e0'
      }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <h2 style={{ textAlign: 'center', fontSize: '1.2rem', fontWeight: 500, margin: 0 }}>
            {fullName}様の鑑定結果
          </h2>
          <p style={{ textAlign: 'center', color: '#666', margin: 0 }}>
            生年月日: {birthdate}
          </p>

          {/* 九星の数字表示セクション */}
          <ResultStarDisplay mainStar={main_star} monthStar={month_star} dayStar={day_star} />
        </div>
      </div>


      {/* 数秘術ライフパスナンバー */}
      {result.numerology && (
        <NumerologyStarInfo numerology={result.numerology} />
      )}

      {/* 本命星の属性情報 */}
      <StarAttributesDisplay
        mainStar={main_star.star_number}
        mainStarName={main_star.name_jp}
      />

      {/* 鑑定結果セクション */}
      <ResultFortuneSection
        mainStar={main_star.star_number}
        monthStar={month_star.star_number}
        targetYear={resultData.targetYear || new Date().getFullYear()}
        birthdate={resultData.birthdate}
      />

      {/* テンプレート選択モーダル */}
      <TemplateSelectionModal
        isOpen={showTemplateModal}
        onClose={closeTemplateModal}
        onSelect={handleDownloadPdf}
        onPreview={handlePreviewReport}
        isGeneratingPdf={isGeneratingPdf}
        pdfProgress={pdfProgress}
      />

      {/* アクションボタン */}
      <div style={{ display: 'flex', justifyContent: 'center', margin: '0px auto 18px', gap: '15px', width: '100%', maxWidth: '500px' }}>
        <button
          onClick={onReset}
          style={{
            padding: '10px 20px',
            fontSize: '1rem',
            backgroundColor: 'transparent',
            color: '#3490dc',
            border: '1px solid #3490dc',
            borderRadius: '4px',
            cursor: 'pointer',
            fontWeight: 500,
            transition: 'all 0.2s ease'
          }}
        >
          新しい鑑定
        </button>

        <button
          onClick={openTemplateModal}
          disabled={isGeneratingPdf}
          style={{
            padding: '10px 20px',
            fontSize: '1rem',
            backgroundColor: '#3490dc',
            color: 'white',
            border: '1px solid #3490dc',
            borderRadius: '4px',
            cursor: isGeneratingPdf ? 'wait' : 'pointer',
            fontWeight: 500,
            transition: 'all 0.2s ease',
            opacity: isGeneratingPdf ? 0.7 : 1
          }}
        >
          {isGeneratingPdf ? 'PDF生成中...' : 'PDF出力'}
        </button>
      </div>
    </div>
  );
} 