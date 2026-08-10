import React, { useContext, useState } from 'react';
import { StyleSheet, View, Text, TouchableOpacity, SafeAreaView, StatusBar } from 'react-native';
import { AuthProvider, AuthContext } from './src/context/AuthContext';
import AuthScreen from './src/screens/AuthScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import InvestmentsScreen from './src/screens/InvestmentsScreen';
import WalletScreen from './src/screens/WalletScreen';
import ReferralsScreen from './src/screens/ReferralsScreen';
import SupportScreen from './src/screens/SupportScreen';
import colors from './src/theme/colors';

function MainApp() {
  const { token, user } = useContext(AuthContext);
  const [activeTab, setActiveTab] = useState('dashboard');

  if (!token || !user) {
    return <AuthScreen />;
  }

  const renderScreen = () => {
    switch (activeTab) {
      case 'dashboard':
        return <DashboardScreen />;
      case 'investments':
        return <InvestmentsScreen />;
      case 'wallet':
        return <WalletScreen />;
      case 'referrals':
        return <ReferralsScreen />;
      case 'support':
        return <SupportScreen />;
      default:
        return <DashboardScreen />;
    }
  };

  return (
    <SafeAreaView style={styles.safeArea}>
      <StatusBar barStyle="light-content" backgroundColor={colors.bgDark} />
      <View style={styles.content}>{renderScreen()}</View>

      {/* Bottom Navigation Bar */}
      <View style={styles.bottomNav}>
        <TouchableOpacity
          style={styles.navTab}
          onPress={() => setActiveTab('dashboard')}
        >
          <Text style={[styles.navIcon, activeTab === 'dashboard' && styles.navIconActive]}>📊</Text>
          <Text style={[styles.navLabel, activeTab === 'dashboard' && styles.navLabelActive]}>
            Home
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.navTab}
          onPress={() => setActiveTab('investments')}
        >
          <Text style={[styles.navIcon, activeTab === 'investments' && styles.navIconActive]}>💼</Text>
          <Text style={[styles.navLabel, activeTab === 'investments' && styles.navLabelActive]}>
            Invest
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.navTab}
          onPress={() => setActiveTab('wallet')}
        >
          <Text style={[styles.navIcon, activeTab === 'wallet' && styles.navIconActive]}>💳</Text>
          <Text style={[styles.navLabel, activeTab === 'wallet' && styles.navLabelActive]}>
            Wallet
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.navTab}
          onPress={() => setActiveTab('referrals')}
        >
          <Text style={[styles.navIcon, activeTab === 'referrals' && styles.navIconActive]}>👥</Text>
          <Text style={[styles.navLabel, activeTab === 'referrals' && styles.navLabelActive]}>
            Network
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.navTab}
          onPress={() => setActiveTab('support')}
        >
          <Text style={[styles.navIcon, activeTab === 'support' && styles.navIconActive]}>💬</Text>
          <Text style={[styles.navLabel, activeTab === 'support' && styles.navLabelActive]}>
            Support
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: colors.bgDark,
  },
  content: {
    flex: 1,
  },
  bottomNav: {
    flexDirection: 'row',
    height: 64,
    backgroundColor: '#0d1320',
    borderTopWidth: 1,
    borderTopColor: colors.bgCardBorder,
    alignItems: 'center',
    justifyContent: 'space-around',
  },
  navTab: {
    alignItems: 'center',
    justifyContent: 'center',
    flex: 1,
  },
  navIcon: {
    fontSize: 18,
    opacity: 0.6,
  },
  navIconActive: {
    opacity: 1,
  },
  navLabel: {
    fontSize: 11,
    color: colors.textMuted,
    marginTop: 2,
    fontWeight: '600',
  },
  navLabelActive: {
    color: colors.primaryCyan,
  },
});
