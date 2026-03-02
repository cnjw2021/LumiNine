import React from 'react';
import { UnstyledButton, Group, Text } from '@mantine/core';
import { IconX } from '@tabler/icons-react';

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
              backgroundColor: 'rgba(75, 163, 227, 0.1)',
            },
          }}
        >
          <IconX size={24} color="#4BA3E3" stroke={1.5} />
        </UnstyledButton>
        <Text 
          size="xl" 
          fw={600} 
          c="#4BA3E3" 
          style={{ 
            letterSpacing: '0.5px',
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