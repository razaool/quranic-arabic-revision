import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  Image,
  ActivityIndicator,
  Alert,
  Linking,
  ScrollView,
} from 'react-native';
import { RouteProp } from '@react-navigation/native';
import { StackNavigationProp } from '@react-navigation/stack';
import { RootStackParamList } from '../App';
import { theme, spacing, borderRadius } from '../utils/theme';

type PageViewerScreenRouteProp = RouteProp<RootStackParamList, 'PageViewer'>;
type PageViewerScreenNavigationProp = StackNavigationProp<RootStackParamList, 'PageViewer'>;

interface Props {
  route: PageViewerScreenRouteProp;
  navigation: PageViewerScreenNavigationProp;
}

const PageViewerScreen: React.FC<Props> = ({ route, navigation }) => {
  const { pageNum, surahTitles, imageUrl, wbwLink } = route.params;
  const [imageLoading, setImageLoading] = useState(true);
  const [imageError, setImageError] = useState(false);

  const handleImageLoad = () => {
    setImageLoading(false);
  };

  const handleImageError = () => {
    setImageLoading(false);
    setImageError(true);
  };

  const handleOpenWBW = async () => {
    if (wbwLink) {
      try {
        await Linking.openURL(wbwLink);
      } catch (error) {
        Alert.alert('Error', 'Could not open the word-by-word translation link');
      }
    }
  };

  const handleGoBack = () => {
    navigation.goBack();
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
      <View style={styles.header}>
        <Text style={styles.pageTitle}>Page {pageNum}</Text>
        <Text style={styles.surahTitles}>{surahTitles}</Text>
      </View>

      <View style={styles.imageContainer}>
        {imageLoading && (
          <View style={styles.loadingContainer}>
            <ActivityIndicator color={theme.colors.primary} size="large" />
            <Text style={styles.loadingText}>Loading page...</Text>
          </View>
        )}
        
        {imageError ? (
          <View style={styles.errorContainer}>
            <Text style={styles.errorText}>Failed to load image</Text>
            <TouchableOpacity style={styles.retryButton} onPress={() => {
              setImageError(false);
              setImageLoading(true);
            }}>
              <Text style={styles.retryButtonText}>Retry</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <Image
            source={{ uri: imageUrl }}
            style={styles.pageImage}
            onLoad={handleImageLoad}
            onError={handleImageError}
            resizeMode="contain"
          />
        )}
      </View>

      <View style={styles.actionsContainer}>
        {wbwLink && (
          <TouchableOpacity style={styles.wbwButton} onPress={handleOpenWBW}>
            <Text style={styles.wbwButtonText}>View Word-by-Word Translation</Text>
          </TouchableOpacity>
        )}
        
        <TouchableOpacity style={styles.backButton} onPress={handleGoBack}>
          <Text style={styles.backButtonText}>Generate Another Page</Text>
        </TouchableOpacity>
      </View>
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
    marginBottom: spacing.lg,
    padding: spacing.lg,
    backgroundColor: theme.colors.surface,
    borderRadius: borderRadius.lg,
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  pageTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: theme.colors.text,
    marginBottom: spacing.sm,
  },
  surahTitles: {
    fontSize: 16,
    color: theme.colors.textSecondary,
    textAlign: 'center',
  },
  imageContainer: {
    backgroundColor: theme.colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.md,
    marginBottom: spacing.lg,
    borderWidth: 1,
    borderColor: theme.colors.border,
    minHeight: 400,
    justifyContent: 'center',
    alignItems: 'center',
  },
  pageImage: {
    width: '100%',
    height: 400,
    borderRadius: borderRadius.md,
  },
  loadingContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    height: 400,
  },
  loadingText: {
    color: theme.colors.textSecondary,
    marginTop: spacing.md,
  },
  errorContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    height: 400,
  },
  errorText: {
    color: theme.colors.error,
    fontSize: 16,
    marginBottom: spacing.md,
  },
  retryButton: {
    backgroundColor: theme.colors.primary,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderRadius: borderRadius.md,
  },
  retryButtonText: {
    color: theme.colors.background,
    fontWeight: '600',
  },
  actionsContainer: {
    gap: spacing.md,
  },
  wbwButton: {
    backgroundColor: theme.colors.surface,
    borderRadius: borderRadius.lg,
    padding: spacing.lg,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: theme.colors.border,
  },
  wbwButtonText: {
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

export default PageViewerScreen;
