'use client';

import ResultFortuneSection from './ResultFortuneSection';
import TemplateSelectionModal from './TemplateSelectionModal';
import { useState } from 'react';
import { usePdfReport } from '@/hooks/usePdfReport';
import { usePowerStoneData } from '@/hooks/usePowerStoneData';
import { useMonthFortuneData } from '@/hooks/useMonthFortuneData';
import { isSixLayer } from '@/types/directionFortune';
import BasePowerstonesSection from './BasePowerstonesSection';
import NumerologyProfileSection from './NumerologyProfileSection';
import { ResultProps } from '@/types/results';

export default function Result({ resultData, onReset }: ResultProps) {
  const { result, fullName, birthdate } = resultData;
  const [showTemplateModal, setShowTemplateModal] = useState<boolean>(false);

  const {
    isGeneratingPdf,
    pdfProgress,
    handleDownloadPdf,
    handlePreviewReport
  } = usePdfReport({
    resultData,
    onActionComplete: () => setShowTemplateModal(false)
  });

  if (!result) return null;

  const { main_star, month_star } = result;
  const targetYear = resultData.targetYear || new Date().getFullYear();

  const {
    loading: stonesLoading,
    powerStones,
    error: stonesError,
  } = usePowerStoneData(main_star.star_number, month_star.star_number, targetYear, birthdate);

  const {
    loading: fortuneLoading,
    currentMonthData,
    error: fortuneError,
  } = useMonthFortuneData(main_star.star_number, month_star.star_number, targetYear);

  const loading = stonesLoading || fortuneLoading;
  const error = [stonesError, fortuneError].filter(Boolean).join(' / ') || null;
  const sixLayer = powerStones && isSixLayer(powerStones) ? powerStones : null;

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      flexDirection: 'column',
      backgroundColor: '#f9f7f2',
      position: 'relative',
      fontFamily: '"Montserrat", sans-serif',
      color: '#4a4a4a',
      backgroundImage: `
        radial-gradient(circle at 10% 10%, rgba(216, 167, 167, 0.03) 0%, transparent 40%),
        radial-gradient(circle at 90% 90%, rgba(155, 176, 165, 0.03) 0%, transparent 40%)
      `
    }}>

      {/* ──── Header ──── */}
      <header className="result-header" style={{
        width: '100%',
        borderBottom: '1px solid rgba(212, 175, 55, 0.1)',
        backgroundColor: 'rgba(255, 255, 255, 0.3)',
        backdropFilter: 'blur(4px)',
        position: 'sticky', top: 0, zIndex: 50
      }}>
        <div style={{ maxWidth: '1100px', margin: '0 auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span style={{ color: '#d4af37', fontSize: '20px' }}>✦</span>
            <h1 style={{
              fontSize: 'clamp(16px, 4vw, 20px)', fontWeight: 'normal', color: '#4a4a4a',
              fontFamily: '"Shippori Mincho", "Noto Serif JP", serif',
              letterSpacing: '0.05em', margin: 0
            }}>
              {fullName}様の鑑定結果
            </h1>
          </div>
        </div>
      </header>

      {/* ──── Main Content: Two-Column Grid ──── */}
      <main className="result-main" style={{ maxWidth: '1100px', margin: '0 auto', position: 'relative', zIndex: 10, width: '100%' }}>

        <div className="result-grid">

          {/* ════ Left Column: Numerology + Recommended Stones ════ */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>

            {/* ── Numerology Profile ── */}
            {sixLayer && (
              <NumerologyProfileSection stoneData={sixLayer} />
            )}

            {/* ── Recommended Stones ── */}
            <div>
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', marginBottom: '24px' }}>
                <h3 style={{
                  color: '#d4af37', fontSize: '11px', letterSpacing: '0.3em',
                  fontWeight: 500, textTransform: 'uppercase' as const,
                  fontFamily: '"Montserrat", sans-serif', margin: 0
                }}>
                  Recommended Stones
                </h3>
                <div style={{ width: '48px', height: '1px', background: 'linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.4), transparent)' }} />
              </div>

              {stonesLoading ? (
                <div style={{ display: 'flex', justifyContent: 'center', padding: '40px 0' }}>
                  <span style={{ color: '#d4af37' }}>読み込み中...</span>
                </div>
              ) : stonesError ? (
                <p style={{ color: 'red', textAlign: 'center', fontSize: '14px' }}>{stonesError}</p>
              ) : sixLayer ? (
                <BasePowerstonesSection stoneData={sixLayer} />
              ) : (
                <p style={{ textAlign: 'center', fontSize: '13px', color: 'rgba(74, 74, 74, 0.5)' }}>
                  パワーストーンデータがありません
                </p>
              )}
            </div>

            {/* ── Action Buttons ── */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '16px' }}>
              <button
                onClick={() => setShowTemplateModal(true)}
                disabled={isGeneratingPdf}
                style={{
                  padding: '16px 48px',
                  backgroundColor: '#d8a7a7', color: '#FFF',
                  fontFamily: '"Noto Serif JP", serif',
                  borderRadius: '9999px',
                  boxShadow: '0 10px 20px -5px rgba(216, 167, 167, 0.25)',
                  fontSize: '13px', letterSpacing: '0.2em',
                  border: 'none', cursor: 'pointer',
                  transition: 'all 0.3s ease'
                }}
              >
                {isGeneratingPdf ? 'PDF生成中...' : '詳細な鑑定書をダウンロード'}
              </button>
              <button
                onClick={onReset}
                style={{
                  padding: '14px 48px',
                  backgroundColor: 'transparent',
                  color: '#d4af37',
                  fontFamily: '"Noto Serif JP", serif',
                  borderRadius: '9999px',
                  border: '1px solid rgba(212, 175, 55, 0.3)',
                  fontSize: '13px', letterSpacing: '0.2em',
                  cursor: 'pointer',
                  transition: 'all 0.3s ease'
                }}
              >
                新しい鑑定
              </button>
            </div>

          </div>

          {/* ════ Right Column: Yearly Fortune + Direction Guide ════ */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '40px' }}>
            <ResultFortuneSection
              targetYear={targetYear}
              powerStones={powerStones}
              currentMonthData={currentMonthData}
              loading={loading}
              error={error}
            />
          </div>
        </div>
      </main>

      {/* ──── Footer ──── */}
      <footer style={{
        width: '100%', padding: '36px', marginTop: 'auto',
        borderTop: '1px solid rgba(212, 175, 55, 0.1)', textAlign: 'center'
      }}>
        <p style={{
          fontSize: '10px', letterSpacing: '0.4em',
          color: 'rgba(74, 74, 74, 0.4)', textTransform: 'uppercase' as const,
          fontFamily: '"Montserrat", sans-serif', margin: 0
        }}>
          © 2024 Nine Star Ki &amp; Numerology Healing Experience
        </p>
      </footer>

      {/* テンプレート選択モーダル */}
      <TemplateSelectionModal
        isOpen={showTemplateModal}
        onClose={() => setShowTemplateModal(false)}
        onSelect={handleDownloadPdf}
        onPreview={handlePreviewReport}
        isGeneratingPdf={isGeneratingPdf}
        pdfProgress={pdfProgress}
      />
    </div>
  );
}