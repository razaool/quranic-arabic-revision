export interface QuranPage {
  pageNum: number;
  surahTitles: string;
  imageUrl: string;
  wbwLink?: string;
}

export interface ProgressData {
  revised: number;
  total: number;
  percentage: number;
}

export interface ApiResponse {
  success: boolean;
  message: string;
  pageNum?: number;
  surahTitles?: string;
  imageUrl?: string;
  wbwLink?: string;
}

export interface AppTheme {
  colors: {
    primary: string;
    secondary: string;
    background: string;
    surface: string;
    text: string;
    textSecondary: string;
    border: string;
    success: string;
    error: string;
  };
  fonts: {
    regular: string;
    medium: string;
    bold: string;
    arabic: string;
  };
}
