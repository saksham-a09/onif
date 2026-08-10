import React, { useState, useContext } from 'react';
import {
  StyleSheet,
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { AuthContext } from '../context/AuthContext';
import colors from '../theme/colors';

export default function AuthScreen() {
  const [activeTab, setActiveTab] = useState('login');
  const { login, register, enableDemoMode, loading } = useContext(AuthContext);

  // Form State
  const [email, setEmail] = useState('l1_alice@finovo.com');
  const [password, setPassword] = useState('Password123!');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [username, setUsername] = useState('');
  const [refCode, setRefCode] = useState('');

  const onLoginSubmit = async () => {
    if (!email || !password) {
      Alert.alert('Validation Error', 'Please enter email and password');
      return;
    }
    await login(email, password);
  };

  const onRegisterSubmit = async () => {
    if (!email || !password || !username) {
      Alert.alert('Validation Error', 'Please fill in all required fields');
      return;
    }
    try {
      await register({
        email,
        username,
        first_name: firstName,
        last_name: lastName,
        password,
        password2: password,
        referral_code: refCode,
      });
      Alert.alert('Success', 'Account created! Please sign in.');
      setActiveTab('login');
    } catch (err) {
      Alert.alert('Registration Error', err.message);
    }
  };

  return (
    <ScrollView contentContainerStyle={styles.container}>
      {/* Brand Header */}
      <View style={styles.headerBox}>
        <View style={styles.logoBadge}>
          <Text style={styles.logoText}>F</Text>
        </View>
        <Text style={styles.brandTitle}>FINOVO Mobile</Text>
        <Text style={styles.brandSubtitle}>Crypto Investments & Referral Network</Text>
      </View>

      {/* Auth Card */}
      <View style={styles.card}>
        <View style={styles.tabContainer}>
          <TouchableOpacity
            style={[styles.tab, activeTab === 'login' && styles.tabActive]}
            onPress={() => setActiveTab('login')}
          >
            <Text style={[styles.tabText, activeTab === 'login' && styles.tabTextActive]}>
              Sign In
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.tab, activeTab === 'register' && styles.tabActive]}
            onPress={() => setActiveTab('register')}
          >
            <Text style={[styles.tabText, activeTab === 'register' && styles.tabTextActive]}>
              Register
            </Text>
          </TouchableOpacity>
        </View>

        {activeTab === 'login' ? (
          <View>
            <Text style={styles.label}>Email Address</Text>
            <TextInput
              style={styles.input}
              value={email}
              onChangeText={setEmail}
              placeholder="user@example.com"
              placeholderTextColor={colors.textDim}
              keyboardType="email-address"
              autoCapitalize="none"
            />

            <Text style={styles.label}>Password</Text>
            <TextInput
              style={styles.input}
              value={password}
              onChangeText={setPassword}
              placeholder="••••••••"
              placeholderTextColor={colors.textDim}
              secureTextEntry
            />

            <TouchableOpacity
              style={styles.btnPrimary}
              onPress={onLoginSubmit}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="#090d16" />
              ) : (
                <Text style={styles.btnPrimaryText}>Sign In to Portal</Text>
              )}
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.btnSecondary}
              onPress={() => enableDemoMode()}
            >
              <Text style={styles.btnSecondaryText}>Explore Demo Mode Offline</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <View>
            <View style={{ flexDirection: 'row', gap: 10 }}>
              <View style={{ flex: 1 }}>
                <Text style={styles.label}>First Name</Text>
                <TextInput
                  style={styles.input}
                  value={firstName}
                  onChangeText={setFirstName}
                  placeholder="Alice"
                  placeholderTextColor={colors.textDim}
                />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={styles.label}>Last Name</Text>
                <TextInput
                  style={styles.input}
                  value={lastName}
                  onChangeText={setLastName}
                  placeholder="Smith"
                  placeholderTextColor={colors.textDim}
                />
              </View>
            </View>

            <Text style={styles.label}>Username</Text>
            <TextInput
              style={styles.input}
              value={username}
              onChangeText={setUsername}
              placeholder="alicesmith"
              placeholderTextColor={colors.textDim}
              autoCapitalize="none"
            />

            <Text style={styles.label}>Email Address</Text>
            <TextInput
              style={styles.input}
              value={email}
              onChangeText={setEmail}
              placeholder="user@example.com"
              placeholderTextColor={colors.textDim}
              keyboardType="email-address"
              autoCapitalize="none"
            />

            <Text style={styles.label}>Password</Text>
            <TextInput
              style={styles.input}
              value={password}
              onChangeText={setPassword}
              placeholder="Minimum 8 characters"
              placeholderTextColor={colors.textDim}
              secureTextEntry
            />

            <Text style={styles.label}>Sponsor Code (Optional)</Text>
            <TextInput
              style={styles.input}
              value={refCode}
              onChangeText={setRefCode}
              placeholder="e.g. SPONSOR123"
              placeholderTextColor={colors.textDim}
              autoCapitalize="characters"
            />

            <TouchableOpacity
              style={styles.btnPrimary}
              onPress={onRegisterSubmit}
              disabled={loading}
            >
              {loading ? (
                <ActivityIndicator color="#090d16" />
              ) : (
                <Text style={styles.btnPrimaryText}>Create Account</Text>
              )}
            </TouchableOpacity>
          </View>
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flexGrow: 1,
    backgroundColor: colors.bgDark,
    justifyContent: 'center',
    padding: 24,
  },
  headerBox: {
    alignItems: 'center',
    marginBottom: 28,
  },
  logoBadge: {
    width: 52,
    height: 52,
    borderRadius: 14,
    backgroundColor: colors.primaryCyan,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 12,
  },
  logoText: {
    fontSize: 26,
    fontWeight: '800',
    color: '#090d16',
  },
  brandTitle: {
    fontSize: 26,
    fontWeight: '800',
    color: colors.textMain,
  },
  brandSubtitle: {
    fontSize: 13,
    color: colors.textMuted,
    marginTop: 4,
  },
  card: {
    backgroundColor: colors.bgCard,
    borderRadius: 20,
    padding: 24,
    borderWidth: 1,
    borderColor: colors.bgCardBorder,
  },
  tabContainer: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: colors.bgCardBorder,
    marginBottom: 20,
  },
  tab: {
    flex: 1,
    paddingVertical: 12,
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: 'transparent',
  },
  tabActive: {
    borderBottomColor: colors.primaryCyan,
  },
  tabText: {
    fontSize: 15,
    fontWeight: '600',
    color: colors.textMuted,
  },
  tabTextActive: {
    color: colors.primaryCyan,
  },
  label: {
    fontSize: 13,
    fontWeight: '600',
    color: colors.textMuted,
    marginBottom: 6,
    marginTop: 12,
  },
  input: {
    backgroundColor: colors.bgInput,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: colors.bgCardBorder,
    paddingHorizontal: 16,
    paddingVertical: 12,
    color: colors.textMain,
    fontSize: 15,
  },
  btnPrimary: {
    backgroundColor: colors.primaryCyan,
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: 24,
  },
  btnPrimaryText: {
    fontSize: 15,
    fontWeight: '700',
    color: '#090d16',
  },
  btnSecondary: {
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    borderRadius: 10,
    paddingVertical: 14,
    alignItems: 'center',
    marginTop: 12,
  },
  btnSecondaryText: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.textMain,
  },
});
