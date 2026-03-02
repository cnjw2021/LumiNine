'use client';

import React, { forwardRef } from 'react';
import { TextInput } from '@mantine/core';

interface DatePickerProps {
  value: string;
  onChange: (date: string) => void;
  label?: string;
  error?: string;
  disabled?: boolean;
}

const CustomDatePicker = forwardRef<HTMLInputElement, DatePickerProps>(
  ({ value, onChange, label, error, disabled }, ref) => {
    const handleChange = (val: string) => {
      const numericValue = val.replace(/[^0-9]/g, '').slice(0, 8);
      
      if (numericValue.length >= 4) {
        const year = numericValue.slice(0, 4);
        const month = numericValue.slice(4, 6);
        const day = numericValue.slice(6, 8);
        
        let formatted = year;
        if (month) formatted += '/' + month;
        if (day) formatted += '/' + day;
        
        onChange(formatted);
      } else {
        onChange(numericValue);
      }
    };

    return (
      <TextInput
        ref={ref}
        label={label}
        value={value}
        onChange={(e) => handleChange(e.target.value)}
        placeholder="YYYY/MM/DD"
        error={error}
        disabled={disabled}
        size="xs"
        styles={{
          input: {
            height: '30px',
            minHeight: '30px'
          }
        }}
        style={{ width: '100%' }}
      />
    );
  }
);

// 表示名を設定
CustomDatePicker.displayName = 'CustomDatePicker';

export default CustomDatePicker; 