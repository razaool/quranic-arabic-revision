import React from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createStackNavigator } from '@react-navigation/stack';
import { StatusBar } from 'react-native';
import { theme } from './utils/theme';

// Import screens (we'll create these next)
import HomeScreen from './screens/HomeScreen';
import PageViewerScreen from './screens/PageViewerScreen';
import ProgressScreen from './screens/ProgressScreen';

export type RootStackParamList = {
  Home: undefined;
  PageViewer: {
    pageNum: number;
    surahTitles: string;
    imageUrl: string;
    wbwLink?: string;
  };
  Progress: undefined;
};

const Stack = createStackNavigator<RootStackParamList>();

const App: React.FC = () => {
  return (
    <NavigationContainer>
      <StatusBar barStyle="light-content" backgroundColor={theme.colors.background} />
      <Stack.Navigator
        initialRouteName="Home"
        screenOptions={{
          headerStyle: {
            backgroundColor: theme.colors.background,
            borderBottomColor: theme.colors.border,
          },
          headerTintColor: theme.colors.text,
          headerTitleStyle: {
            fontFamily: theme.fonts.medium,
          },
          cardStyle: {
            backgroundColor: theme.colors.background,
          },
        }}
      >
        <Stack.Screen 
          name="Home" 
          component={HomeScreen} 
          options={{ title: 'Quranic Arabic Revision' }}
        />
        <Stack.Screen 
          name="PageViewer" 
          component={PageViewerScreen} 
          options={{ title: 'Page Viewer' }}
        />
        <Stack.Screen 
          name="Progress" 
          component={ProgressScreen} 
          options={{ title: 'Progress' }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
};

export default App;
