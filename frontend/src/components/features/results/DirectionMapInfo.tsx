import React from 'react';
import Image from 'next/image';

const DirectionMapInfo = () => (
  <div style={{
    padding: '20px',
    backgroundColor: 'white',
    borderRadius: '8px',
    boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    border: '1px solid #e0e0e0'
  }}>
    <h3 style={{fontSize: '1.4rem', textAlign: 'center', marginTop: 0, marginBottom: '15px', color: '#333'}}>
      方位の見つけ方
    </h3>
    <div
      className="houi-3col-flex"
      style={{
        display: 'flex',
        flexDirection: typeof window !== 'undefined' && window.innerWidth > 600 ? 'row' : 'column',
        gap: '20px',
        flexWrap: 'wrap',
        alignItems: typeof window !== 'undefined' && window.innerWidth > 600 ? 'stretch' : 'center',
        justifyContent: 'space-between',
        minHeight: typeof window !== 'undefined' && window.innerWidth > 600 ? '340px' : 'auto',
      }}
    >
      {/* 左カラム：説明と使い方 */}
      <div style={{
        flex: '1 1 320px',
        minWidth: 0,
        maxWidth: '350px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'flex-start',
        height: '100%'
      }}>
        <p style={{fontSize: '0.9rem', lineHeight: 1.6, margin: 0}}>
          九星気学では、自宅や居場所からの方位が運気に大きく影響します。鑑定結果の
          <span style={{fontWeight: 'bold', color: '#3490dc'}}>吉方位を知り、その方向に行動することで運気を高める</span>
          ことができます。
        </p>
        <p style={{fontSize: '0.9rem', lineHeight: 1.6, marginTop: '10px', marginBottom: '15px'}}>
          『あちこち方位』アプリを使えば、自宅を中心とした正確な方位を簡単に確認でき、
          効果的な方位取りが可能になります。
        </p>
        <div style={{
          backgroundColor: '#f9f9f9', 
          padding: '15px', 
          borderRadius: '8px',
          marginBottom: '15px'
        }}>
          <div style={{fontWeight: 'bold', fontSize: '0.95rem', marginBottom: '10px', color: '#333'}}>
            方位探しの手順：
          </div>
          <ol style={{margin: '0', paddingLeft: '20px'}}>
            <li style={{fontSize: '0.85rem', marginBottom: '8px'}}>
              地図を自宅周辺に合わせ、左上の【<span style={{fontWeight: 'bold'}}>画面中央を自宅に設定</span>】ボタンを押す
            </li>
            <li style={{fontSize: '0.85rem', marginBottom: '8px'}}>
              【方位の線】を開き、<span style={{fontWeight: 'bold'}}>方位線</span>にチェックを入れる
            </li>
            <li style={{fontSize: '0.85rem', marginBottom: '8px', color: '#d32f2f', fontWeight: 'bold'}}>
              線の種類で「気学30/60°」を選択する（重要）
            </li>
            <li style={{fontSize: '0.85rem', marginBottom: '0'}}>
              地図を動かして自宅からの方位を確認し、吉方位への行動計画を立てる
            </li>
          </ol>
        </div>
        <div style={{textAlign: 'center'}}>
          <a 
            href="https://h200.com/houi1/" 
            target="_blank" 
            rel="noopener noreferrer"
            style={{
              display: 'inline-block',
              padding: '10px 30px',
              backgroundColor: '#4CAF50',
              color: 'white',
              textDecoration: 'none',
              borderRadius: '4px',
              fontWeight: 600,
              boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
              transition: 'all 0.2s ease'
            }}
            onMouseOver={(e) => e.currentTarget.style.backgroundColor = '#3d8b40'}
            onMouseOut={(e) => e.currentTarget.style.backgroundColor = '#4CAF50'}
          >
            あちこち方位アプリを開く
          </a>
        </div>
      </div>

      {/* 中央カラム：必須設定 */}
      <div style={{
        flex: '0 1 270px',
        minWidth: '220px',
        maxWidth: '320px',
        backgroundColor: '#fff8f8',
        borderRadius: '8px',
        border: '1px solid #ffcccc',
        padding: '18px 12px',
        marginBottom: '15px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '10px',
        height: '100%'
      }}>
        <div style={{
          padding: '6px 16px', 
          backgroundColor: '#d32f2f', 
          color: 'white', 
          borderRadius: '4px', 
          fontSize: '0.95rem',
          fontWeight: 'bold',
          marginBottom: '10px',
          textAlign: 'center'
        }}>
          必須設定
        </div>
        <div style={{width: '100%', display: 'flex', justifyContent: 'center'}}>
          <Image 
            src="/images/directions/ninestarki_30_60.png" 
            alt="気学30/60°設定" 
            width={220} height={320}
            style={{
              width: '220px', 
              maxWidth: '100%',
              height: 'auto', 
              border: '1px solid #ddd',
              borderRadius: '4px',
              margin: '0 auto',
              display: 'block'
            }}
          />
        </div>
        <p style={{
          fontSize: '0.9rem', 
          margin: '10px 0 5px 0', 
          fontWeight: 'bold', 
          color: '#d32f2f',
          textAlign: 'center'
        }}>
          必ず「気学30/60°」を選択！
        </p>
        <p style={{fontSize: '0.8rem', margin: '0', color: '#666', lineHeight: 1.5, textAlign: 'center'}}>
          九星気学の正確な方位線を表示するために<br />最も重要な設定です
        </p>
      </div>

      {/* 右カラム：地図 */}
      <div style={{
        flex: '2 1 340px',
        minWidth: '260px',
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        height: '100%'
      }}>
        <div style={{
          borderRadius: '8px', 
          overflow: 'hidden', 
          boxShadow: '0 2px 8px rgba(0,0,0,0.15)',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
        }}>
          <Image 
            src="/images/directions/achikochi_map.png" 
            alt="あちこち方位サイト" 
            width={600} height={400}
            style={{
              width: '100%', 
              height: '100%',
              minHeight: 0,
              objectFit: 'cover',
              display: 'block',
              flex: '1 1 auto'
            }}
            priority
          />
          <div style={{
            backgroundColor: '#f0f0f0', 
            padding: '8px', 
            textAlign: 'center', 
            fontSize: '0.8rem',
            color: '#666',
            flex: '0 0 auto'
          }}>
            あちこち方位アプリの表示例 - 青い線が自宅からの方位線
          </div>
        </div>
      </div>
    </div>
  </div>
);

export default DirectionMapInfo; 