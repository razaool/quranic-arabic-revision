import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  ScrollView,
} from 'react-native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../App';
import { theme, spacing, borderRadius } from '../utils/theme';
import { apiService } from '../services/api';
import { ProgressData } from '../types';

type HomeScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Home'>;

interface Props {
  navigation: HomeScreenNavigationProp;
}

const HomeScreen: React.FC<Props> = ({ navigation }) => {
  const [progress, setProgress] = useState<ProgressData>({ revised: 0, total: 604, percentage: 0 });
  const [loading, setLoading] = useState(false);
  const [progressLoading, setProgressLoading] = useState(true);

  useEffect(() => {
    loadProgress();
  }, []);

  const loadProgress = async () => {
    try {
      setProgressLoading(true);
      const progressData = await apiService.getProgress();
      setProgress(progressData);
    } catch (error) {
      console.error('Failed to load progress:', error);
      Alert.alert('Error', 'Failed to load progress data');
    } finally {
      setProgressLoading(false);
    }
  };

  const handleGeneratePage = async () => {
    try {
      setLoading(true);
      const response = await apiService.generateRandomPage();
      
      if (response.success && response.pageNum && response.imageUrl) {
        navigation.navigate('PageViewer', {
          pageNum: response.pageNum,
          surahTitles: response.surahTitles || '',
          imageUrl: response.imageUrl,
          wbwLink: response.wbwLink,
        });
        // Refresh progress after generating a page
        loadProgress();
      } else {
        Alert.alert('Error', response.message || 'Failed to generate page');
      }
    } catch (error) {
      console.error('Failed to generate page:', error);
      Alert.alert('Error', 'Failed to generate page. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  const handleViewProgress = () => {
    navigation.navigate('Progress');
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
      <View style={styles.header}>
        <Text style={styles.title}>Quranic Arabic Revision</Text>
        <Text style={styles.subtitle}>Track your progress through the Quran</Text>
      </View>

      <View style={styles.progressCard}>
        <Text style={styles.progressTitle}>Your Progress</Text>
        {progressLoading ? (
          <ActivityIndicator color={theme.colors.primary} size="large" />
        ) : (
          <>
            <View style={styles.progressBar}>
              <View 
                style={[
                  styles.progressFill, 
                  { width: `${progress.percentage}%` }
                ]} 
              />
            </View>
            <Text style={styles.progressText}>
              {progress.revised} of {progress.total} pages completed ({progress.percentage}%)
            </Text>
          </>
        )}
      </View>

      <TouchableOpacity 
        style={[styles.generateButton, loading && styles.generateButtonDisabled]}
        onPress={handleGeneratePage}
        disabled={loading}
      >
        {loading ? (
          <ActivityIndicator color={theme.colors.background} size="small" />
        ) : (
          <Text style={styles.generateButtonText}>Generate Random Page</Text>
        )}
      </TouchableOpacity>

      <TouchableOpacity 
        style={styles.progressButton}
        onPress={handleViewProgress}
      >
        <Text style={styles.progressButtonText}>View Detailed Progress</Text>
      </TouchableOpacity>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  contentContainer: {
    padding: spacing.lg,
  },
  header: {
    alignItems: 'center',
    marginBottom: spacing.xl,
  },
  title: {
    fontSize: 28,
    fontWeight: 'bold',
    color: theme.colors.text,
    textAlign: 'center',
    marginBottom: spacing.sm,
  },
  subtitle: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    textAlign: 'center',
  },
  progressCard: {
    backgroundColor: theme.colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.xl,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  progressTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: spacing.md,
  },
  progressBar: {
    height: 8,
    backgroundColor: theme.colors.border,
    borderRadius: borderRadius.sm,
    marginBottom: spacing.md,
  },
  progressFill: {
    height: '100%',
    backgroundColor: theme.colors.primary,
    borderRadius: borderRadius.sm,
  },
  progressText: {
    fontSize: 14,
    color: theme.colors.textSecondary,
    textAlign: 'center',
  },
  generateButton: {
    backgroundColor: theme.colors.primary,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    alignItems: 'center',
    marginBottom: spacing.md,
    shadowColor: theme.colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  generateButtonDisabled: {
    opacity: 0.6,
  },
  generateButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: theme.colors.background,
  },
  progressButton: {
    backgroundColor: 'transparent',
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  progressButtonText: {
    fontSize: 16,
    fontWeight: '500',
    color: theme.colors.text,
  },
});

export default HomeScreen;
