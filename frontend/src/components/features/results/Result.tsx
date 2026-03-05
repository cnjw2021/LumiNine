'use client';

import ResultFortuneSection from './ResultFortuneSection';
import NumerologyStarInfo from './NumerologyStarInfo';
import ResultStarDisplay from './ResultStarDisplay';
import TemplateSelectionModal from './TemplateSelectionModal';
import { useEffect, useState } from 'react';
import api from '@/utils/api';
import { useNineStarKiStore } from '@/stores/nineStarKiStore';
import { ResultProps, PdfJobResultDataMinimal, PartnerMinimal } from '@/types/results';
import { CalculationResult } from '@/types/stars';
import { StarLifeGuidance } from '@/components/features';
import StarAttributesDisplay from './StarAttributesDisplay';
// Progress removed (modal handles display)



export default function Result({ resultData, onReset }: ResultProps) {
  const { result, fullName, birthdate } = resultData;
  const [isGeneratingPdf, setIsGeneratingPdf] = useState<boolean>(false);
  const [pdfProgress, setPdfProgress] = useState<number>(0);
  const [showTemplateModal, setShowTemplateModal] = useState<boolean>(false);
  const [browserType, setBrowserType] = useState<'safari' | 'chrome' | 'other'>('other');

  // Zustandストアから日命星と月命星読みデータを保存・取得するための関数を取得
  const {
  } = useNineStarKiStore();

  // ブラウザを検出する関数
  const detectBrowser = (): 'safari' | 'chrome' | 'other' => {
    const userAgent = navigator.userAgent.toLowerCase();
    if (userAgent.indexOf('safari') !== -1 && userAgent.indexOf('chrome') === -1) {
      return 'safari';
    } else if (userAgent.indexOf('chrome') !== -1) {
      return 'chrome';
    }
    return 'other';
  };

  // ブラウザ検出
  useEffect(() => {
    setBrowserType(detectBrowser());
  }, []);



  // PDFをダウンロードする関数（Chrome用）
  const handleDownloadPdf = async (templateId: number) => {
    await downloadPdf(templateId, false);
  };

  // 共通のPDFダウンロード関数
  const downloadPdf = async (templateId: number, useSimple: boolean) => {
    try {
      setIsGeneratingPdf(true);
      setPdfProgress(0);

      const normalizedBirthdate = (resultData.birthdate || '').replace(/\//g, '-');
      const minimalResultData: PdfJobResultDataMinimal = {
        fullName: resultData.fullName,
        birthdate: normalizedBirthdate,
        gender: (resultData as { gender: 'male' | 'female' }).gender,
        targetYear: resultData.targetYear || new Date().getFullYear(),
      };

      // 1. ジョブ登録
      const createRes = await api.post('/pdf-jobs', {
        resultData: minimalResultData,
        templateId,
        backgroundId: templateId, // 背景IDはテンプレートIDと同じ
        useSimple,
      });

      const jobId: string = createRes.data.job_id;
      setPdfProgress(0); // queued 状態

      // 2. ポーリングでステータス確認
      const pollInterval = 3000; // 3秒
      const wait = (ms: number) => new Promise((res) => setTimeout(res, ms));

      while (true) {
        const statusRes = await api.get(`/pdf-jobs/${jobId}`);
        const { status, download_url } = statusRes.data;

        if (status === 'queued') {
          setPdfProgress(10);
        } else if (status === 'started') {
          // started 状態が続く間は 30→90% を徐々に進める
          setPdfProgress((prev) => (prev < 90 ? prev + 10 : prev));
        }

        if (status === 'finished') {
          setPdfProgress(100);
          // ダウンロード開始。ブラウザに任せる。
          window.location.href = download_url;
          // 100% をユーザーに見せるため 600ms 程度待機
          await wait(600);
          break;
        }

        if (status === 'failed') {
          throw new Error('PDF生成に失敗しました。');
        }

        // まだqueued / started の場合は待機
        await wait(pollInterval);
      }

      // 上記 wait で 100% が表示された後にモーダルを閉じる
      setShowTemplateModal(false);
    } catch (error) {
      console.error('PDFの非同期生成中にエラーが発生しました:', error);
      alert('PDFの生成に失敗しました。もう一度お試しください。');
    } finally {
      setPdfProgress(0);
      setIsGeneratingPdf(false);
    }
  };

  // プレビューを表示する関数
  const handlePreviewReport = async (templateId: number) => {
    // ブラウザタイプに応じてsimpleディレクトリを使用するかを決定
    const useSimple = browserType === 'safari';

    try {
      setIsGeneratingPdf(true);

      // プレビュー用にリクエストデータを準備
      const resultDataWithReadings = {
        ...resultData,
      };

      // プレビューエンドポイントを呼び出し
      const response = await api.post('/nine-star/preview-report',
        {
          resultData: resultDataWithReadings,
          templateId: templateId,
          backgroundId: templateId, // 背景IDはテンプレートIDと同じ値を使用
          useSimple: useSimple // simpleディレクトリのSVGを使うかどうか
        },
        { responseType: 'text' }
      );

      // 新しいタブでHTMLコンテンツを開く
      const newWindow = window.open('', '_blank');
      if (newWindow) {
        newWindow.document.write(response.data);
        newWindow.document.close();
      } else {
        alert('プレビューを表示できません。ポップアップがブロックされている可能性があります。');
      }

      setShowTemplateModal(false);
    } catch (error) {
      console.error('プレビュー表示中にエラーが発生しました:', error);
      alert('プレビューの表示に失敗しました。もう一度お試しください。');
    } finally {
      setIsGeneratingPdf(false);
    }
  };

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


      {/* ほかのセクションの後、本命星と月命星のガイダンス情報（新規追加）*/}
      <StarLifeGuidance
        mainStar={main_star.star_number}
        monthStar={month_star.star_number}
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