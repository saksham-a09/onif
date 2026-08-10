import React, { useState, useEffect, useContext } from 'react';
import {
  StyleSheet,
  View,
  Text,
  ScrollView,
} from 'react-native';
import { AuthContext } from '../context/AuthContext';
import { apiCall } from '../config/api';
import colors from '../theme/colors';

export default function ReferralsScreen() {
  const { user, isDemoMode } = useContext(AuthContext);
  const [team, setTeam] = useState([
    { email: 'l2_emma@finovo.com', username: 'l2emma', date_joined: '2026-08-02' },
    { email: 'l2_frank@finovo.com', username: 'l2frank', date_joined: '2026-08-02' },
  ]);

  const [commissions, setCommissions] = useState([
    { id: 'c1', commission_type: 'DIRECT', level: 1, amount: 40.0, from_user_email: 'l2_emma@finovo.com' },
    { id: 'c2', commission_type: 'ROI', level: 1, amount: 25.0, from_user_email: 'l2_emma@finovo.com' },
  ]);

  const loadReferralData = async () => {
    if (isDemoMode) return;
    try {
      const teamData = await apiCall('/referrals/team/').catch(() => []);
      if (Array.isArray(teamData)) setTeam(teamData);

      const commData = await apiCall('/referrals/commissions/').catch(() => []);
      if (Array.isArray(commData)) setCommissions(commData);
    } catch (err) {
      console.warn('Referrals data load error:', err.message);
    }
  };

  useEffect(() => {
    loadReferralData();
  }, []);

  const currentLevel = user?.active_level || 2;
  const levels = [
    { lvl: 1, req: 2, type: 'Direct 2%' },
    { lvl: 2, req: 4, type: 'ROI 1.5%' },
    { lvl: 3, req: 6, type: 'ROI 1.5%' },
    { lvl: 4, req: 8, type: 'ROI 1.5%' },
    { lvl: 5, req: 10, type: 'ROI 1.5%' },
  ];

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.screenTitle}>Referral Network</Text>

      {/* Code Card */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Your Referral Code</Text>
        <View style={styles.refBox}>
          <Text style={styles.refCodeText}>{user?.referral_code || 'ALICE123'}</Text>
          <Text style={{ color: colors.primaryCyan, fontWeight: '700' }}>
            Earn 2.0% Direct + 1.5% ROI
          </Text>
        </View>
      </View>

      {/* Level Unlock Progress */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Multi-Level Unlock Status</Text>
        {levels.map((item) => {
          const isUnlocked = currentLevel >= item.lvl;
          return (
            <View key={item.lvl} style={styles.levelRow}>
              <View>
                <Text style={{ color: colors.textMain, fontWeight: '700' }}>
                  Level {item.lvl} ({item.type})
                </Text>
                <Text style={{ color: colors.textMuted, fontSize: 11 }}>
                  Requires {item.req} Active Directs
                </Text>
              </View>
              <Text style={{ color: isUnlocked ? colors.accentGreen : colors.accentWarning, fontWeight: '800' }}>
                {isUnlocked ? 'UNLOCKED' : 'LOCKED'}
              </Text>
            </View>
          );
        })}
      </View>

      {/* Direct Team Members */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Direct Downline Members ({team.length})</Text>
        {team.length === 0 ? (
          <Text style={{ color: colors.textMuted, fontSize: 13 }}>No direct members registered yet.</Text>
        ) : (
          team.map((m, idx) => (
            <View key={m.id || idx} style={styles.levelRow}>
              <View>
                <Text style={{ color: colors.textMain, fontWeight: '700' }}>{m.email}</Text>
                <Text style={{ color: colors.textMuted, fontSize: 11 }}>{m.username || 'Member'}</Text>
              </View>
              <Text style={{ color: colors.primaryCyan, fontSize: 12, fontWeight: '700' }}>Direct (L1)</Text>
            </View>
          ))
        )}
      </View>

      {/* Earned Commissions Ledger */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Earned Referral Commissions</Text>
        {commissions.length === 0 ? (
          <Text style={{ color: colors.textMuted, fontSize: 13 }}>No commissions recorded yet.</Text>
        ) : (
          commissions.map((c, idx) => (
            <View key={c.id || idx} style={styles.levelRow}>
              <View>
                <Text style={{ color: colors.textMain, fontWeight: '700' }}>
                  {c.commission_type} (Level {c.level})
                </Text>
                <Text style={{ color: colors.textMuted, fontSize: 11 }}>
                  From: {c.from_user_email || 'Downline'}
                </Text>
              </View>
              <Text style={{ color: colors.primaryCyan, fontWeight: '800', fontSize: 16 }}>
                +${Number(c.amount).toFixed(2)}
              </Text>
            </View>
          ))
        )}
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgDark, padding: 16 },
  screenTitle: { fontSize: 22, fontWeight: '800', color: colors.textMain, marginVertical: 16 },
  card: {
    backgroundColor: colors.bgCard,
    borderRadius: 16,
    padding: 18,
    borderWidth: 1,
    borderColor: colors.bgCardBorder,
    marginBottom: 16,
  },
  cardTitle: { fontSize: 16, fontWeight: '700', color: colors.textMain, marginBottom: 14 },
  refBox: {
    backgroundColor: colors.bgInput,
    padding: 14,
    borderRadius: 10,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  refCodeText: { fontSize: 20, fontWeight: '800', color: colors.textMain },
  levelRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.05)',
  },
});
