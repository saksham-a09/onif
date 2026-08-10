import React, { useContext, useState, useEffect } from 'react';
import {
  StyleSheet,
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  RefreshControl,
} from 'react-native';
import { AuthContext } from '../context/AuthContext';
import { apiCall } from '../config/api';
import colors from '../theme/colors';

export default function DashboardScreen({ navigation }) {
  const { user, logout, isDemoMode } = useContext(AuthContext);
  const [refreshing, setRefreshing] = useState(false);

  const [wallet, setWallet] = useState({
    balance: 1450.0,
    total_deposited: 1000.0,
    total_roi_earned: 125.0,
    total_direct_income: 80.0,
    total_referral_income: 25.0,
    total_withdrawn: 50.0,
  });

  const [activeInvestments, setActiveInvestments] = useState([
    {
      id: 'inv-1',
      plan_name: 'Starter Plan',
      amount: 1000.0,
      max_return: 300.0,
      total_credited: 125.0,
      status: 'ACTIVE',
    },
  ]);

  const [recentLedger, setRecentLedger] = useState([
    {
      id: '1',
      transaction_type: 'CREDIT',
      category: 'DEPOSIT',
      amount: 1000.0,
      balance_after: 1000.0,
      description: 'Approved deposit #dep-001',
    },
    {
      id: '2',
      transaction_type: 'CREDIT',
      category: 'DIRECT_INCOME',
      amount: 40.0,
      balance_after: 1040.0,
      description: 'Level-1 direct commission from l2_emma@finovo.com',
    },
    {
      id: '3',
      transaction_type: 'CREDIT',
      category: 'ROI',
      amount: 125.0,
      balance_after: 1165.0,
      description: 'Weekly ROI credited from Starter Plan',
    },
  ]);

  const loadDashboardData = async () => {
    if (isDemoMode) return;
    try {
      const data = await apiCall('/dashboard/');
      if (data) {
        setWallet({
          balance: data.wallet_balance || 0,
          total_deposited: data.total_deposited || 0,
          total_roi_earned: data.total_roi_earned || 0,
          total_direct_income: data.total_direct_income || 0,
          total_referral_income: data.total_referral_income || 0,
          total_withdrawn: data.total_withdrawn || 0,
        });
      }
      const investments = await apiCall('/investments/').catch(() => []);
      if (Array.isArray(investments)) setActiveInvestments(investments);

      const ledger = await apiCall('/wallet/transactions/').catch(() => []);
      if (Array.isArray(ledger)) setRecentLedger(ledger);
    } catch (err) {
      console.warn('Dashboard fetch error:', err.message);
    }
  };

  useEffect(() => {
    loadDashboardData();
  }, []);

  const onRefresh = async () => {
    setRefreshing(true);
    await loadDashboardData();
    setRefreshing(false);
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor={colors.primaryCyan} />
      }
    >
      {/* Top Profile Header */}
      <View style={styles.topHeader}>
        <View style={{ flexDirection: 'row', alignItems: 'center', gap: 12 }}>
          <View style={styles.avatar}>
            <Text style={styles.avatarText}>
              {(user?.first_name || user?.email || 'U')[0].toUpperCase()}
            </Text>
          </View>
          <View>
            <Text style={styles.userName}>
              {`${user?.first_name || ''} ${user?.last_name || ''}`.trim() || user?.email}
            </Text>
            <Text style={styles.userRole}>Level {user?.active_level || 0} Unlock</Text>
          </View>
        </View>

        <TouchableOpacity style={styles.logoutBtn} onPress={logout}>
          <Text style={{ fontSize: 16 }}>🚪</Text>
        </TouchableOpacity>
      </View>

      {/* KPI Cards Grid */}
      <View style={styles.grid2}>
        <View style={styles.statCard}>
          <Text style={styles.statTitle}>Wallet Balance</Text>
          <Text style={styles.statValue}>${Number(wallet.balance).toFixed(2)}</Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statTitle}>Active Investments</Text>
          <Text style={styles.statValue}>
            $
            {activeInvestments
              .filter((i) => i.status === 'ACTIVE')
              .reduce((sum, item) => sum + Number(item.amount), 0)
              .toFixed(2)}
          </Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statTitle}>Total ROI Earned</Text>
          <Text style={[styles.statValue, { color: colors.accentGreen }]}>
            ${Number(wallet.total_roi_earned).toFixed(2)}
          </Text>
        </View>
        <View style={styles.statCard}>
          <Text style={styles.statTitle}>Direct Referral Income</Text>
          <Text style={[styles.statValue, { color: colors.primaryCyan }]}>
            ${Number(wallet.total_direct_income).toFixed(2)}
          </Text>
        </View>
      </View>

      {/* Active Investment Meters */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Active Investments</Text>
        {activeInvestments.length === 0 ? (
          <Text style={{ color: colors.textMuted, fontSize: 13 }}>No active investments yet.</Text>
        ) : (
          activeInvestments.map((inv, idx) => {
            const credited = Number(inv.total_credited || 0);
            const maxRet = Number(inv.max_return || inv.amount * 3);
            const pct = maxRet > 0 ? Math.min(100, (credited / maxRet) * 100) : 0;
            return (
              <View key={inv.id || idx} style={{ marginBottom: 14 }}>
                <View style={{ flexDirection: 'row', justifyContent: 'space-between', marginBottom: 6 }}>
                  <Text style={{ color: colors.textMain, fontWeight: '700' }}>
                    {inv.plan_name || 'Plan'} (${Number(inv.amount).toFixed(2)})
                  </Text>
                  <Text style={{ color: colors.primaryCyan, fontWeight: '700' }}>
                    ${credited.toFixed(2)} / ${maxRet.toFixed(2)} ({pct.toFixed(0)}%)
                  </Text>
                </View>
                <View style={styles.progressBg}>
                  <View style={[styles.progressFill, { width: `${pct}%` }]} />
                </View>
              </View>
            );
          })
        )}
      </View>

      {/* Referral Code Card */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Your Sponsor Code</Text>
        <View style={styles.refBox}>
          <Text style={styles.refText}>{user?.referral_code || 'ALICE123'}</Text>
          <Text style={{ color: colors.primaryCyan, fontWeight: '700' }}>2% Direct + 1.5% ROI</Text>
        </View>
      </View>

      {/* Recent Ledger Activity */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Recent Wallet Ledger</Text>
        {recentLedger.slice(0, 5).map((item, idx) => {
          const isCredit = item.transaction_type === 'CREDIT';
          return (
            <View key={item.id || idx} style={styles.ledgerRow}>
              <View style={{ flex: 1 }}>
                <Text style={{ color: colors.textMain, fontWeight: '700', fontSize: 14 }}>
                  {item.category}
                </Text>
                <Text style={{ color: colors.textMuted, fontSize: 12, marginTop: 2 }}>
                  {item.description}
                </Text>
              </View>
              <Text
                style={{
                  color: isCredit ? colors.accentGreen : colors.accentDanger,
                  fontWeight: '800',
                  fontSize: 15,
                }}
              >
                {isCredit ? '+' : '-'}${Number(item.amount).toFixed(2)}
              </Text>
            </View>
          );
        })}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.bgDark,
    padding: 16,
  },
  topHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 16,
    marginBottom: 12,
  },
  avatar: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.primaryPurple,
    alignItems: 'center',
    justifyContent: 'center',
  },
  avatarText: {
    fontSize: 18,
    fontWeight: '800',
    color: '#fff',
  },
  userName: {
    fontSize: 17,
    fontWeight: '700',
    color: colors.textMain,
  },
  userRole: {
    fontSize: 12,
    color: colors.primaryCyan,
    fontWeight: '600',
  },
  logoutBtn: {
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    padding: 10,
    borderRadius: 12,
  },
  grid2: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 12,
    marginBottom: 16,
  },
  statCard: {
    width: '48%',
    backgroundColor: colors.bgCard,
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: colors.bgCardBorder,
  },
  statTitle: {
    fontSize: 12,
    color: colors.textMuted,
    marginBottom: 6,
  },
  statValue: {
    fontSize: 20,
    fontWeight: '800',
    color: colors.textMain,
  },
  card: {
    backgroundColor: colors.bgCard,
    borderRadius: 16,
    padding: 18,
    borderWidth: 1,
    borderColor: colors.bgCardBorder,
    marginBottom: 16,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: colors.textMain,
    marginBottom: 14,
  },
  progressBg: {
    height: 8,
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressFill: {
    height: '100%',
    backgroundColor: colors.primaryCyan,
  },
  refBox: {
    backgroundColor: colors.bgInput,
    padding: 14,
    borderRadius: 10,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  refText: {
    fontSize: 18,
    fontWeight: '800',
    color: colors.textMain,
  },
  ledgerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.05)',
  },
});
