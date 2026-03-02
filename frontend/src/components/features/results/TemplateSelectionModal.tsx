'use client';

import { useState } from 'react';
import Image from 'next/image';
import { Button, Overlay, Loader, Progress } from '@mantine/core';
import { IconDownload } from '@tabler/icons-react';

export interface TemplateStyle {
  primaryColor: string;
  gradientStart: string;
  gradientEnd: string;
  name: string;
}

interface TemplateSelectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelect: (templateId: number) => void;
  onPreview?: (templateId: number) => void;
  isGeneratingPdf: boolean;
  initialTemplateId?: number;
  pdfProgress?: number;
}

// テンプレートスタイルを定義（4つのテンプレート）
const templateStyles: Record<number, TemplateStyle> = {
  1: {
    primaryColor: '#4caf50',
    gradientStart: '#e8f5e9',
    gradientEnd: '#fff3e0',
    name: 'クラシック'
  },
  2: {
    primaryColor: '#e91e63',
    gradientStart: '#fff7fa',
    gradientEnd: '#fff2f6',
    name: 'エレガント'
  },
  3: {
    primaryColor: '#ff9800',
    gradientStart: '#fff3e0',
    gradientEnd: '#fff8e1',
    name: 'スピリチュアル'
  },
  4: {
    primaryColor: '#4a90e2',
    gradientStart: '#e3f2fd',
    gradientEnd: '#fff8e1',
    name: 'フレッシュ'
  }
};

// カスタムローダー関数を定義
const customImageLoader = ({ src }: { src: string }) => {
  return src;
};

// テンプレートIDをそのまま使用（1-4に対応）
const getTemplateId = (templateId: number): number => {
  return templateId;
};

export default function TemplateSelectionModal({
  isOpen,
  onClose,
  onSelect,
  onPreview,
  isGeneratingPdf,
  initialTemplateId = 1,  // デフォルトをグリーンに変更
  pdfProgress = 0
}: TemplateSelectionModalProps) {
  const [selectedTemplate, setSelectedTemplate] = useState<number>(initialTemplateId);

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      zIndex: 1000
    }}>
      <div style={{
        backgroundColor: 'white',
        borderRadius: '8px',
        padding: window.innerWidth <= 768 ? '15px' : '20px',
        width: window.innerWidth <= 768 ? '95%' : '80%',
        maxWidth: '620px',
        maxHeight: '90vh',
        overflow: 'auto',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        position: 'relative'
      }}>
        {/* Progress Overlay */}
        {isGeneratingPdf && (
          <Overlay opacity={0.75} color="#fff" blur={1} zIndex={2000} radius={0}>
            <div style={{height:'100%',display:'flex',flexDirection:'column',justifyContent:'center',alignItems:'center'}}>
              <Loader size="lg"/>
              <Progress value={pdfProgress} style={{width:'60%',marginTop:16}} animated striped/>
              <p style={{marginTop:8,fontWeight:600}}>{pdfProgress}%</p>
            </div>
          </Overlay>
        )}
                <p style={{ textAlign: 'center', color: '#666', marginBottom: '15px', marginTop: 0, fontSize: window.innerWidth <= 768 ? '0.9rem' : '1rem', fontWeight: 600 }}>
          PDFのデザイン選択＆ダウンロード
        </p>
        
        <div style={{ 
          display: window.innerWidth <= 520 ? 'flex' : 'grid',
          gridTemplateColumns: window.innerWidth <= 520 ? undefined : 'repeat(auto-fit, minmax(140px, 1fr))',
          gap: window.innerWidth <= 520 ? '2px' : window.innerWidth <= 768 ? '4px' : '6px',
          marginBottom: '20px',
          overflowX: window.innerWidth <= 520 ? 'auto' : 'visible',
          padding: window.innerWidth <= 520 ? '0 2px' : undefined
        }}>
          {/* 4つのテンプレートを表示 */}
          {[1, 2, 3, 4].map((templateId) => (
            <div 
              key={templateId}
              onClick={() => setSelectedTemplate(templateId)}
              style={{
                border: `2px solid ${selectedTemplate === templateId ? templateStyles[templateId].primaryColor : '#e0e0e0'}`,
                borderRadius: '6px',
                overflow: 'hidden',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                transform: selectedTemplate === templateId ? 'scale(1.05)' : 'scale(1)',
                boxShadow: selectedTemplate === templateId ? '0 4px 8px rgba(0,0,0,0.1)' : 'none',
                margin: window.innerWidth <= 520 ? '2px 0' : undefined
              }}
            >
              <div style={{
                height: window.innerWidth <= 520 ? '90px' : window.innerWidth <= 768 ? '80px' : '120px',
                background: `linear-gradient(135deg, ${templateStyles[templateId].gradientStart}, ${templateStyles[templateId].gradientEnd})`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                padding: window.innerWidth <= 520 ? '2px' : window.innerWidth <= 768 ? '4px' : '8px'
              }}>
                                  <Image 
                    loader={customImageLoader}
                    src={`/api/nine-star/static/images/background/certificate_template${getTemplateId(templateId)}.png`} 
                    alt={`テンプレート${templateId}`}
                    width={window.innerWidth <= 520 ? 135 : window.innerWidth <= 768 ? 120 : 180}
                    height={window.innerWidth <= 520 ? 90 : window.innerWidth <= 768 ? 80 : 120}
                    style={{ 
                      maxHeight: '100%', 
                      maxWidth: '100%', 
                      objectFit: 'contain',
                      opacity: 0.8
                    }}
                  />
              </div>
              {/* テンプレート名ラベル (モバイルでは非表示) */}
              {window.innerWidth > 520 && (
                <div
                  style={{
                padding: window.innerWidth <= 768 ? '4px' : '6px',
                textAlign: 'center',
                backgroundColor: '#f8f9fa',
                color: templateStyles[templateId].primaryColor,
                fontWeight: 500,
                fontSize: window.innerWidth <= 768 ? '0.7rem' : '0.8rem',
                minHeight: window.innerWidth <= 768 ? '28px' : '32px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
                  }}
                >
                {templateStyles[templateId].name}
              </div>
              )}
            </div>
          ))}
        </div>
        
        <div style={{ marginBottom: window.innerWidth <= 768 ? '10px' : '12px' }} />
        
        <div style={{ 
          display: 'flex', 
          justifyContent: 'center', 
          gap: window.innerWidth <= 768 ? '8px' : '10px', 
          flexWrap: 'wrap',
          padding: window.innerWidth <= 768 ? '0 5px' : '0'
        }}>
          <Button
            onClick={() => onSelect(selectedTemplate)}
            disabled={isGeneratingPdf}
            variant="filled"
            color="green"
            size="sm"
            rightSection={<IconDownload size={window.innerWidth <= 768 ? 14 : 16} />}
            style={{
              height: window.innerWidth <= 768 ? '30px' : '34px',
              fontSize: window.innerWidth <= 768 ? '0.8rem' : '0.85rem'
            }}
          >
            ダウンロード
          </Button>
          <Button
            onClick={onClose}
            variant="light"
            color="gray"
            size="sm"
            style={{ 
              height: window.innerWidth <= 768 ? '30px' : '34px',
              fontSize: window.innerWidth <= 768 ? '0.8rem' : '0.85rem'
            }}
          >
            キャンセル
          </Button>
        </div>
      </div>
    </div>
  );
}

// テンプレートスタイルを外部からも使用できるようにエクスポート
export { templateStyles }; 