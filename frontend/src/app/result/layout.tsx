'use client';

import React from 'react';

/**
 * Result ページ専用レイアウト。
 * ※ AppShell を使用しない — root layout.tsx の AppShell と二重に
 *   ネストすると、Mantine 内部のスクロールコンテナが競合し、
 *   client-side navigation 後にスクロール不能になるため (Issue #129)。
 */
export default function ResultLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div
      style={{
        width: '100%',
        maxWidth: '100%',
        margin: 0,
        backgroundImage:
          'linear-gradient(135deg, rgba(64, 169, 255, 0.9) 0%, rgba(255, 255, 255, 0.8) 50%, rgba(0, 188, 255, 0.9) 100%)',
      }}
    >
      {children}
    </div>
  );
}