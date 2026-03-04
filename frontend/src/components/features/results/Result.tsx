'use client';

import React, { useEffect, useState } from 'react';

import ResultFortuneSection from './ResultFortuneSection';
import MainStarWithInfo from './MainStarWithInfo';
import TemplateSelectionModal from './TemplateSelectionModal';
import api from '@/utils/api';
import { useNineStarKiStore } from '@/stores/nineStarKiStore';
import DirectionMapInfo from './DirectionMapInfo';
import CompatibilityResult from './CompatibilityResult';
import { ResultProps, CompatibilityData, PdfJobResultDataMinimal, PartnerMinimal } from '@/types/results';
import { CalculationResult } from '@/types/stars';
import { StarLifeGuidance } from '@/components/features';
import StarAttributesDisplay from './StarAttributesDisplay';
import FiveElementsCycle from './FiveElementsCycle';
// Progress removed (modal handles display)

// MainStarWithInfoコンポーネントのStar型と互換性のある型を定義
interface StarForInfo {
  number: number;
  name_jp: string;
  name_en?: string;
  element?: string;
  description?: string;
  keywords?: string;
  title?: string;     // 特性タイトルを追加
  advice?: string;    // アドバイスを追加
}

// 月命星読みの型定義
interface MonthStarReading {
  id: number;
  star_number: number;
  title: string;
  keywords: string;
  description: string;
}

// 日命星読みの型定義
interface DailyStarReading {
  id: number;
  star_number: number;
  title: string;
  keywords: string | null;
  description: string;
  advice: string | null;
}

export default function Result({ resultData, onReset, compatibilityData }: ResultProps) {
  const { result, fullName, birthdate } = resultData;
  const [monthStarReading, setMonthStarReading] = useState<MonthStarReading | null>(null);
  const [dailyStarReading, setDailyStarReading] = useState<DailyStarReading | null>(null);
  const [isGeneratingPdf, setIsGeneratingPdf] = useState<boolean>(false);
  const [pdfProgress, setPdfProgress] = useState<number>(0);
  const [showTemplateModal, setShowTemplateModal] = useState<boolean>(false);
  const [localCompatibilityData, setLocalCompatibilityData] = useState<CompatibilityData | null>(null);
  const [browserType, setBrowserType] = useState<'safari' | 'chrome' | 'other'>('other');

  // Zustandストアから日命星と月命星読みデータを保存・取得するための関数を取得
  const {
    setMonthlyStarReading: storeMonthlyStarReading,
    monthlyStarReading: storedMonthlyStarReading,
    setDailyStarReading: storeDailyStarReading,
    dailyStarReading: storedDailyStarReading
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

      // 相性鑑定結果が存在するかチェック
      const isCompatMode = !!compatibilityData || !!resultData.isCompatibilityReading;
      const compatSource = isCompatMode ? (compatibilityData || localCompatibilityData) : undefined;
      const partnerMinimal: PartnerMinimal | undefined = compatSource?.targetPerson && compatSource?.gender ? {
        fullName: compatSource.targetPerson.name,
        birthdate: (compatSource.targetPerson.birthdate || '').replace(/\//g, '-'),
        gender: compatSource.gender,
      } : undefined;

      // 日命星 / 月命星 の読みデータをストアから取得し、リクエストデータに追加
      const normalizedBirthdate = (resultData.birthdate || '').replace(/\//g, '-');
      const minimalResultData: PdfJobResultDataMinimal = {
        fullName: resultData.fullName,
        birthdate: normalizedBirthdate,
        gender: (resultData as { gender: 'male' | 'female' }).gender,
        targetYear: resultData.targetYear || new Date().getFullYear(),
        ...(partnerMinimal ? { partner: partnerMinimal } : {}),
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



      // finalCompatibilityDataが存在するかチェック
      const compatibilityResult = compatibilityData?.result || localCompatibilityData?.result;

      // デバッグログ
      console.log('プレビュー - 相性鑑定データ状態:', {
        'propsからのデータ': compatibilityData ? true : false,
        'ローカルストレージからのデータ': localCompatibilityData ? true : false,
        '最終使用データ': compatibilityResult ? true : false,
        'browserType': browserType,
        'useSimple': useSimple
      });

      // 日命星と月命星の読みデータをストアから取得しリクエストデータに追加
      const resultDataWithReadings = {
        ...resultData,
        result: {
          ...resultData.result,
          month_star_reading: storedMonthlyStarReading,
          day_star_reading: storedDailyStarReading,
          // 相性鑑定結果があれば追加
          compatibility: compatibilityResult
        }
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

  // 相性鑑定結果がある場合に表示するコンテンツを取得
  const finalCompatibilityData = compatibilityData || localCompatibilityData;

  if (!result) {
    return null;
  }

  const { main_star, month_star, day_star } = result;

  // 星番号に基づいて色を返す関数
  const getStarColor = (starNumber: number): string => {
    const colors = [
      '#3490dc',  // 1: 一白水星 - 鮮やかな青
      '#2d3748',  // 2: 二黒土星 - 深い黒
      '#38a169',  // 3: 三碧木星 - 爽やかな緑
      '#319795',  // 4: 四緑木星 - ティール
      '#ecc94b',  // 5: 五黄土星 - 黄金色
      '#a0aec0',  // 6: 六白金星 - シルバー
      '#e53e3e',  // 7: 七赤金星 - 情熱的な赤
      '#805ad5',  // 8: 八白土星 - 神秘的な紫
      '#ed64a6'   // 9: 九紫火星 - 鮮やかなピンク
    ];
    return colors[starNumber - 1] || '#3490dc';
  };

  // カンマ区切りのキーワード文字列を処理する関数
  const processKeywords = (keywordsStr: string | null | undefined): string => {
    if (!keywordsStr) return '';
    // カンマと読点を「・」に置き換えて整形
    return keywordsStr.replace(/[,、]/g, '・').trim();
  };

  // StarForInfo形式に変換する関数
  const formatStarForInfo = (star: CalculationResult['main_star'], additionalInfo?: Partial<StarForInfo>): StarForInfo => ({
    number: star.star_number,
    name_jp: star.name_jp,
    name_en: star.name_en || '',
    element: star.element || '',
    description: additionalInfo?.description || star.description || '',
    // キーワードの処理をprocessKeywords関数で統一
    keywords: processKeywords(additionalInfo?.keywords || star.keywords),
    title: additionalInfo?.title || '',
    advice: additionalInfo?.advice || '',
  });

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
        </div>
      </div>



      {/* 本命星のSVGと説明文 */}
      <MainStarWithInfo
        star={formatStarForInfo(main_star)}
        title={`本命星\n（性格・運命の流れ）`}
      />

      {/* 月命星のSVGと説明文 */}
      <MainStarWithInfo
        star={formatStarForInfo(month_star, monthStarReading ? {
          description: monthStarReading.description,
          keywords: monthStarReading.keywords,
          title: monthStarReading.title
        } : undefined)}
        title={`月命星\n（環境・対人関係）`}
        isMonthStar={true}
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