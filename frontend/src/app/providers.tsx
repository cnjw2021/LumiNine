'use client';

import { MantineProvider } from '@mantine/core';
import { Notifications } from '@mantine/notifications';

export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <MantineProvider
      theme={{
        primaryColor: 'pink',
        components: {
          Notification: {
            styles: {
              root: { border: '1px solid #e9ecef' }
            }
          }
        }
      }}
      defaultColorScheme="light"
    >
      <Notifications 
        position="top-right" 
        autoClose={3000} 
        limit={1}
        classNames={{ root: 'custom-notifications' }}
      />
      {children}
    </MantineProvider>
  );
} 