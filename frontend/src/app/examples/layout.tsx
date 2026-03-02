'use client';

import React from 'react';
import { AppShell } from '@mantine/core';

export default function NinestarExampleLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <AppShell
      padding={{ base: '6px', sm: '12px', md: '16px', lg: '24px' }}
      style={{
        backgroundColor: 'white',
      }}
      styles={{
        root: {
          backgroundColor: 'white !important',
          backgroundImage: 'none !important',
        },
        main: {
          width: '100%',
          maxWidth: '100%',
          margin: 0,
          backgroundColor: 'white !important',
          backgroundImage: 'linear-gradient(135deg, rgba(64, 169, 255, 0.9) 0%, rgba(255, 255, 255, 0.8) 50%, rgba(0, 188, 255, 0.9) 100%) !important',
          '@media (maxWidth: 576px)': {
            padding: '0 6px',
          },
          '@media (minWidth: 577px) and (maxWidth: 768px)': {
            padding: '0 12px',
          },
          '@media (minWidth: 769px) and (maxWidth: 992px)': {
            padding: '0 16px',
          },
          '@media (minWidth: 993px)': {
            padding: '0 24px',
          }
        }
      }}
    >
      {children}
    </AppShell>
  );
}