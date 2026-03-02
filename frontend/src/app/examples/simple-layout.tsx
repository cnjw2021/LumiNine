'use client';

import React from 'react';

export default function SimpleLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div style={{
      width: '100%',
      maxWidth: '100%',
      margin: 0,
      backgroundColor: 'white',
      backgroundImage: 'linear-gradient(135deg, rgba(64, 169, 255, 0.9) 0%, rgba(255, 255, 255, 0.8) 50%, rgba(0, 188, 255, 0.9) 100%)',
      padding: '24px',
      minHeight: '100vh'
    }}>
      {children}
    </div>
  );
} 