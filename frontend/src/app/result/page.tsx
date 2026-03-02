'use client';

import React, { useEffect, useState, useRef } from 'react';
import { Result } from '@/components/features/results';
import { useAuth } from '@/contexts/auth/AuthContext';
import { Container, Loader, Text, Button, Transition } from '@mantine/core';
import { useRouter } from 'next/navigation';
import { HiArrowUp, HiArrowDown } from 'react-icons/hi';
import { ResultData, CompatibilityData } from '@/types';

// ローカルストレージキー
const STORAGE_KEY = 'ninestarki-result-data';
const COMPATIBILITY_STORAGE_KEY = 'ninestarki-compatibility-result-data';

export default function ResultPage() {
  const router = useRouter();
  const { token, isLoading: authLoading } = useAuth();
  const [resultData, setResultData] = useState<ResultData | null>(null);
  const [compatibilityData, setCompatibilityData] = useState<CompatibilityData | null>(null);
  const [isDataLoading, setIsDataLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [showScrollTop, setShowScrollTop] = useState(false);
  const [showScrollBottom, setShowScrollBottom] = useState(false);
  const containerRef = useRef<HTMLDivElement>(null);

  // ローカルストレージからデータを読み込む
  useEffect(() => {
    const loadData = async () => {
      if (authLoading) return;

      if (!token) {
        router.push('/login');
        return;
      }
      
      try {
        // ローカルストレージへのアクセスをチェック
        try {
          // ローカルストレージにアクセスできるかテスト
          localStorage.setItem('test-storage', 'test');
          localStorage.removeItem('test-storage');
        } catch (storageAccessError) {
          console.error('ローカルストレージへのアクセスエラー:', storageAccessError);
          setLoadError('ブラウザのストレージへのアクセスが制限されています。プライベートブラウジングを無効にするか、Cookieを許可してください。');
          setIsDataLoading(false);
          return;
        }
        
        // ローカルストレージから通常鑑定データを取得
        const savedData = localStorage.getItem(STORAGE_KEY);
        console.log('取得したデータ:', savedData ? '存在します' : 'ありません');
        
        if (savedData) {
          try {
            const parsedData = JSON.parse(savedData);
            console.log('パース成功:', parsedData ? 'データあり' : 'データなし');
            
            // 必須フィールドが存在するか確認
            if (!parsedData.result || !parsedData.fullName) {
              console.error('データの形式が不正:', parsedData);
              setLoadError('不完全なデータが見つかりました。最初から鑑定をやり直してください。');
              localStorage.removeItem(STORAGE_KEY);
              setIsDataLoading(false);
              setTimeout(() => router.push('/'), 3000);
              return;
            }
            
            setResultData(parsedData);

            // 相性鑑定データも取得
            const savedCompatibilityData = localStorage.getItem(COMPATIBILITY_STORAGE_KEY);
            if (savedCompatibilityData) {
              try {
                const parsedCompatibilityData = JSON.parse(savedCompatibilityData);
                setCompatibilityData(parsedCompatibilityData);
              } catch (parseError) {
                console.error('相性データの解析に失敗:', parseError);
                // 相性データ取得失敗はエラーとしない（オプション）
              }
            }
            
            setIsDataLoading(false);
          } catch (parseError) {
            console.error('データの解析に失敗:', parseError);
            setLoadError('データの読み込みに失敗しました。最初から鑑定をやり直してください。');
            localStorage.removeItem(STORAGE_KEY);
            setIsDataLoading(false);
            setTimeout(() => router.push('/'), 3000);
          }
        } else {
          // ローカルストレージにデータがない場合はホームページに遷移
          console.log('データが見つからないため、ホームページへリダイレクト');
          router.push('/');
        }
      } catch (error) {
        console.error('データ読み込みエラー:', error);
        setLoadError('データの読み込みに失敗しました。最初から鑑定をやり直してください。');
        setIsDataLoading(false);
        setTimeout(() => router.push('/'), 3000);
      }
    };

    loadData();
  }, [authLoading, token, router]);

  // スクロール位置を監視して、トップボタンの表示/非表示を切り替える
  const handleScroll = () => {
    if (containerRef.current) {
      const scrollTop = containerRef.current.scrollTop;
      const maxScrollTop = containerRef.current.scrollHeight - containerRef.current.clientHeight;
      const threshold = 300;
      setShowScrollTop(scrollTop > threshold); // 300px以上スクロールしたらトップへ戻るボタン
      setShowScrollBottom(scrollTop < maxScrollTop - threshold); // 下端手前300pxより上なら下へボタン
    }
  };

  // トップにスクロールする関数
  const scrollToTop = () => {
    if (containerRef.current) {
      containerRef.current.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    }
  };

  const scrollToBottom = () => {
    if (containerRef.current) {
      containerRef.current.scrollTo({
        top: containerRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  };

  if (authLoading || isDataLoading) {
    return (
      <Container style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Loader size="xl" />
      </Container>
    );
  }

  if (loadError) {
    return (
      <Container style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <Text c="red">{loadError}</Text>
      </Container>
    );
  }

  if (!token || !resultData) {
    return null;
  }

  const handleReset = () => {
    // ローカルストレージをクリア
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(COMPATIBILITY_STORAGE_KEY);
    
    // ホームページに遷移
    router.push('/');
  };

  return (
    <div 
      className="result-container" 
      ref={containerRef}
      onScroll={handleScroll}
    >
      <style jsx>{`
        .result-container {
          height: 100%;
          overflow: auto;
          max-height: calc(100vh - 60px);
          scrollbar-width: thin;
          scrollbar-color: rgba(75, 163, 227, 0.3) rgba(0, 0, 0, 0.05);
          position: relative;
        }
        .result-container::-webkit-scrollbar {
          width: 6px;
        }
        .result-container::-webkit-scrollbar-track {
          background: rgba(0, 0, 0, 0.05);
          border-radius: 3px;
        }
        .result-container::-webkit-scrollbar-thumb {
          background: rgba(75, 163, 227, 0.3);
          border-radius: 3px;
        }
        .result-container::-webkit-scrollbar-thumb:hover {
          background: rgba(75, 163, 227, 0.5);
        }
      `}</style>
      <Result 
        resultData={resultData}
        onReset={handleReset} 
        compatibilityData={compatibilityData}
      />
      
      <Transition mounted={showScrollTop} transition="fade" duration={400}>
        {(styles) => (
          <Button
            style={{
              ...styles,
              position: 'fixed',
              bottom: '20px',
              right: '20px',
              borderRadius: '50%',
              width: '50px',
              height: '50px',
              padding: 0,
              zIndex: 1000,
            }}
            color="blue"
            onClick={scrollToTop}
          >
            <HiArrowUp size={24} />
          </Button>
        )}
      </Transition>

      <Transition mounted={showScrollBottom} transition="fade" duration={400}>
        {(styles) => (
          <Button
            style={{
              ...styles,
              position: 'fixed',
              bottom: '80px',
              right: '20px',
              borderRadius: '50%',
              width: '50px',
              height: '50px',
              padding: 0,
              zIndex: 1000,
            }}
            color="blue"
            onClick={scrollToBottom}
          >
            <HiArrowDown size={24} />
          </Button>
        )}
      </Transition>
    </div>
  );
} 