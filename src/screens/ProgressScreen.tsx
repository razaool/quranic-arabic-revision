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

type ProgressScreenNavigationProp = StackNavigationProp<RootStackParamList, 'Progress'>;

interface Props {
  navigation: ProgressScreenNavigationProp;
}

const ProgressScreen: React.FC<Props> = ({ navigation }) => {
  const [progress, setProgress] = useState<ProgressData>({ revised: 0, total: 604, percentage: 0 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProgress();
  }, []);

  const loadProgress = async () => {
    try {
      setLoading(true);
      const progressData = await apiService.getProgress();
      setProgress(progressData);
    } catch (error) {
      console.error('Failed to load progress:', error);
      Alert.alert('Error', 'Failed to load progress data');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = () => {
    loadProgress();
  };

  const handleGoBack = () => {
    navigation.goBack();
  };

  const getProgressColor = (percentage: number) => {
    if (percentage >= 100) return theme.colors.success;
    if (percentage >= 75) return theme.colors.primary;
    if (percentage >= 50) return theme.colors.textSecondary;
    return theme.colors.error;
  };

  const getProgressMessage = (percentage: number) => {
    if (percentage >= 100) return "🎉 Congratulations! You've completed the entire Quran!";
    if (percentage >= 75) return "Excellent progress! You're almost there!";
    if (percentage >= 50) return "Great job! You're halfway through!";
    if (percentage >= 25) return "Good start! Keep going!";
    return "Every journey begins with a single step. Keep it up!";
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
      <View style={styles.header}>
        <Text style={styles.title}>Your Progress</Text>
        <Text style={styles.subtitle}>Track your journey through the Quran</Text>
      </View>

      {loading ? (
        <View style={styles.loadingContainer}>
          <ActivityIndicator color={theme.colors.primary} size="large" />
          <Text style={styles.loadingText}>Loading progress...</Text>
        </View>
      ) : (
        <>
          <View style={styles.progressCard}>
            <Text style={styles.progressTitle}>Overall Progress</Text>
            
            <View style={styles.progressBar}>
              <View 
                style={[
                  styles.progressFill, 
                  { 
                    width: `${progress.percentage}%`,
                    backgroundColor: getProgressColor(progress.percentage)
                  }
                ]} 
              />
            </View>
            
            <Text style={styles.progressText}>
              {progress.revised} of {progress.total} pages completed
            </Text>
            
            <Text style={[styles.percentageText, { color: getProgressColor(progress.percentage) }]}>
              {progress.percentage}%
            </Text>
          </View>

          <View style={styles.statsCard}>
            <Text style={styles.statsTitle}>Statistics</Text>
            
            <View style={styles.statRow}>
              <Text style={styles.statLabel}>Pages Completed:</Text>
              <Text style={styles.statValue}>{progress.revised}</Text>
            </View>
            
            <View style={styles.statRow}>
              <Text style={styles.statLabel}>Pages Remaining:</Text>
              <Text style={styles.statValue}>{progress.total - progress.revised}</Text>
            </View>
            
            <View style={styles.statRow}>
              <Text style={styles.statLabel}>Total Pages:</Text>
              <Text style={styles.statValue}>{progress.total}</Text>
            </View>
          </View>

          <View style={styles.messageCard}>
            <Text style={styles.messageText}>
              {getProgressMessage(progress.percentage)}
            </Text>
          </View>

          <View style={styles.actionsContainer}>
            <TouchableOpacity style={styles.refreshButton} onPress={handleRefresh}>
              <Text style={styles.refreshButtonText}>Refresh Progress</Text>
            </TouchableOpacity>
            
            <TouchableOpacity style={styles.backButton} onPress={handleGoBack}>
              <Text style={styles.backButtonText}>Back to Home</Text>
            </TouchableOpacity>
          </View>
        </>
      )}
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
    marginBottom: spacing.sm,
  },
  subtitle: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    textAlign: 'center',
  },
  loadingContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing.xl,
  },
  loadingText: {
    color: theme.colors.textSecondary,
    marginTop: spacing.md,
  },
  progressCard: {
    backgroundColor: theme.colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.lg,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  progressTitle: {
    fontSize: 20,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: spacing.lg,
    textAlign: 'center',
  },
  progressBar: {
    height: 12,
    backgroundColor: theme.colors.border,
    borderRadius: borderRadius.sm,
    marginBottom: spacing.md,
  },
  progressFill: {
    height: '100%',
    borderRadius: borderRadius.sm,
  },
  progressText: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginBottom: spacing.sm,
  },
  percentageText: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  statsCard: {
    backgroundColor: theme.colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.lg,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  statsTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: theme.colors.text,
    marginBottom: spacing.lg,
    textAlign: 'center',
  },
  statRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: spacing.sm,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  statLabel: {
    fontSize: 16,
    color: theme.colors.textSecondary,
  },
  statValue: {
    fontSize: 16,
    fontWeight: '600',
    color: theme.colors.text,
  },
  messageCard: {
    backgroundColor: theme.colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    marginBottom: spacing.lg,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  messageText: {
    fontSize: 16,
    color: theme.colors.text,
    textAlign: 'center',
    lineHeight: 24,
  },
  actionsContainer: {
    gap: spacing.md,
  },
  refreshButton: {
    backgroundColor: theme.colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  refreshButtonText: {
    fontSize: 16,
    fontWeight: '500',
    color: theme.colors.text,
  },
  backButton: {
    backgroundColor: theme.colors.primary,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    alignItems: 'center',
    shadowColor: theme.colors.primary,
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 8,
  },
  backButtonText: {
    fontSize: 18,
    fontWeight: '600',
    color: theme.colors.background,
  },
});

export default ProgressScreen;
