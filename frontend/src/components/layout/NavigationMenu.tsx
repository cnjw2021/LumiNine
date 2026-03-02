import React from 'react';
import { UnstyledButton, Group, Text, Loader } from '@mantine/core';
import { usePathname } from 'next/navigation';

export interface MenuItem {
  icon: React.ComponentType<{ size?: number; stroke?: number; style?: React.CSSProperties }>;
  label: string;
  href: string;
  onClick?: (href: string) => void | Promise<void>;
  permission?: string;
}

interface NavigationMenuProps {
  items: MenuItem[];
  onNavigate: (href: string) => void;
  navigating: string | null;
}

export const NavigationMenu = ({ items, onNavigate, navigating }: NavigationMenuProps) => {
  const pathname = usePathname();

  const renderMenuItem = (item: MenuItem) => {
    const isActive = pathname === item.href || 
                    (item.href !== '/' && pathname?.startsWith(item.href));
    const activeColor = '#d53f8c';
    const isNavigating = navigating === item.href;
    
    return (
      <UnstyledButton
        onClick={() => {
          if (item.onClick) {
            item.onClick(item.href);
          } else {
            onNavigate(item.href);
          }
        }}
        styles={{
          root: {
            width: '100%',
            margin: '0 auto',
            padding: '10px 8px',
            color: isActive ? activeColor : '#4a5568',
            transition: 'all 0.2s ease',
            borderRadius: '8px',
            backgroundColor: 'rgba(255, 255, 255, 0.5)',
            backdropFilter: 'blur(5px)',
            '&:hover': {
              backgroundColor: 'rgba(75, 163, 227, 0.08)',
              transform: 'translateX(4px)',
              color: isActive ? activeColor : '#4BA3E3'
            },
          },
        }}
      >
        <Group wrap="nowrap" style={{ width: '100%', gap: 6 }}>
          {isNavigating ? (
            <Loader size="xs" color={activeColor} />
          ) : (
            <item.icon size={18} style={{ color: isActive ? activeColor : '#4BA3E3', flexShrink: 0 }} stroke={1.5} />
          )}
          <Text size="sm" fw={isActive ? 600 : 500} style={{ whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', lineHeight: 1.3 }}>
            {item.label}
          </Text>
        </Group>
      </UnstyledButton>
    );
  };

  return (
    <>
      {items.map((item, index) => (
        <div key={index}>
          {renderMenuItem(item)}
        </div>
      ))}
    </>
  );
}; 