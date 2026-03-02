import { Icon } from '@tabler/icons-react';

export interface MenuItem {
  icon: Icon;
  label: string;
  href: string;
  permission?: string;
  onClick?: () => void;
} 