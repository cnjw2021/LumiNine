import React from 'react';
import { UnstyledButton, Group, Text } from '@mantine/core';
import { IconX } from '@tabler/icons-react';
import { COLORS, FONTS, NAV } from '@/utils/theme';

interface DrawerHeaderProps {
  title: string;
  onClose: () => void;
}

export const DrawerHeader = ({ title, onClose }: DrawerHeaderProps) => {
  return (
    <Group h={60} px="20px" justify="space-between" w="100%">
      <Group gap="sm">
        <UnstyledButton
          onClick={onClose}
          style={{
            width: '32px',
            height: '32px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: '4px',
            transition: 'background-color 0.2s ease',
            '&:hover': {
              backgroundColor: NAV.hoverBg,
            },
          }}
        >
          <IconX size={24} color={COLORS.accent} stroke={1.5} />
        </UnstyledButton>
        <Text
          size="xl"
          fw={400}
          c={COLORS.text}
          style={{
            fontFamily: FONTS.title,
            letterSpacing: '0.05em',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis'
          }}
        >
          {title}
        </Text>
      </Group>
    </Group>
  );
};