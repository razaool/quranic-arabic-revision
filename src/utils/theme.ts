import { AppTheme } from '../types';

export const theme: AppTheme = {
  colors: {
    primary: '#ffffff',
    secondary: '#cccccc',
    background: '#000000',
    surface: '#1a1a1a',
    text: '#ffffff',
    textSecondary: '#cccccc',
    border: '#333333',
    success: '#ffffff',
    error: '#ff6b6b',
  },
  fonts: {
    regular: 'System',
    medium: 'System',
    bold: 'System',
    arabic: 'System', // Will be updated to use Arabic fonts
  },
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

export const borderRadius = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
};
