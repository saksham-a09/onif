import React, { useState, useEffect, useContext } from 'react';
import {
  StyleSheet,
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  Modal,
  TextInput,
  Alert,
} from 'react-native';
import { AuthContext } from '../context/AuthContext';
import { apiCall } from '../config/api';
import colors from '../theme/colors';

export default function InvestmentsScreen() {
  const { isDemoMode } = useContext(AuthContext);
  const [plans, setPlans] = useState([
    {
      id: 'starter',
      name: 'Starter Plan',
      weekly_roi_rate: 2.5,
      minimum_amount: 100,
      maximum_amount: 1000,
    },
    {
      id: 'pro',
      name: 'Pro Plan',
      weekly_roi_rate: 3.5,
      minimum_amount: 500,
      maximum_amount: 5000,
    },
    {
      id: 'elite',
      name: 'Elite Plan',
      weekly_roi_rate: 5.0,
      minimum_amount: 1000,
      maximum_amount: 10000,
    },
  ]);

  const [investments, setInvestments] = useState([]);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [investAmount, setInvestAmount] = useState('100');
  const [modalVisible, setModalVisible] = useState(false);

  const loadPlansAndInvestments = async () => {
    if (isDemoMode) return;
    try {
      const fetchedPlans = await apiCall('/investments/plans/').catch(() => []);
      if (Array.isArray(fetchedPlans) && fetchedPlans.length > 0) setPlans(fetchedPlans);

      const fetchedInvestments = await apiCall('/investments/').catch(() => []);
      if (Array.isArray(fetchedInvestments)) setInvestments(fetchedInvestments);
    } catch (err) {
      console.warn('Investments load error:', err.message);
    }
  };

  useEffect(() => {
    loadPlansAndInvestments();
  }, []);

  const openModal = (plan) => {
    setSelectedPlan(plan);
    setInvestAmount(String(plan.minimum_amount || 100));
    setModalVisible(true);
  };

  const handleConfirmInvestment = async () => {
    const amt = Number(investAmount);
    if (!amt || amt < (selectedPlan?.minimum_amount || 100)) {
      Alert.alert('Invalid Amount', `Minimum amount for this plan is $${selectedPlan?.minimum_amount}`);
      return;
    }

    try {
      if (!isDemoMode) {
        await apiCall('/investments/', 'POST', {
          plan: selectedPlan.id,
          amount: amt,
        });
      }

      setModalVisible(false);
      Alert.alert('Success', `Invested $${amt.toFixed(2)} in ${selectedPlan.name}!`);
      loadPlansAndInvestments();
    } catch (err) {
      Alert.alert('Investment Error', err.message);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.screenTitle}>Investment Plans</Text>

      {/* Plan Cards */}
      {plans.map((plan) => (
        <View key={plan.id} style={styles.planCard}>
          <Text style={styles.planName}>{plan.name}</Text>
          <Text style={styles.planRoi}>
            {Number(plan.weekly_roi_rate).toFixed(2)}%{' '}
            <Text style={{ fontSize: 14, color: colors.textMuted }}>/ weekly ROI</Text>
          </Text>
          <View style={styles.featureRow}>
            <Text style={styles.featureLabel}>Min Investment:</Text>
            <Text style={styles.featureValue}>${Number(plan.minimum_amount).toFixed(2)}</Text>
          </View>
          <View style={styles.featureRow}>
            <Text style={styles.featureLabel}>Max Total Return:</Text>
            <Text style={[styles.featureValue, { color: colors.accentGreen }]}>300.00%</Text>
          </View>
          <TouchableOpacity style={styles.btnInvest} onPress={() => openModal(plan)}>
            <Text style={styles.btnInvestText}>Invest {plan.name}</Text>
          </TouchableOpacity>
        </View>
      ))}

      {/* My Investments History */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>My Portfolio</Text>
        {investments.length === 0 ? (
          <Text style={{ color: colors.textMuted, fontSize: 13 }}>No investments recorded yet.</Text>
        ) : (
          investments.map((inv, idx) => (
            <View key={inv.id || idx} style={styles.invRow}>
              <View>
                <Text style={{ color: colors.textMain, fontWeight: '700' }}>{inv.plan_name || 'Plan'}</Text>
                <Text style={{ color: colors.textMuted, fontSize: 12 }}>Status: {inv.status}</Text>
              </View>
              <Text style={{ color: colors.primaryCyan, fontWeight: '800', fontSize: 16 }}>
                ${Number(inv.amount).toFixed(2)}
              </Text>
            </View>
          ))
        )}
      </View>

      {/* Purchase Modal */}
      <Modal visible={modalVisible} transparent animationType="slide">
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Confirm Investment</Text>
            <Text style={{ color: colors.textMuted, marginBottom: 12 }}>{selectedPlan?.name}</Text>

            <Text style={styles.label}>Amount ($)</Text>
            <TextInput
              style={styles.input}
              value={investAmount}
              onChangeText={setInvestAmount}
              keyboardType="numeric"
            />

            <Text style={{ color: colors.accentGreen, marginVertical: 12, fontWeight: '700' }}>
              Max Return (300%): ${(Number(investAmount || 0) * 3).toFixed(2)}
            </Text>

            <View style={{ flexDirection: 'row', gap: 12, marginTop: 8 }}>
              <TouchableOpacity
                style={[styles.btnInvest, { flex: 1, backgroundColor: colors.bgInput }]}
                onPress={() => setModalVisible(false)}
              >
                <Text style={{ color: colors.textMain, fontWeight: '700' }}>Cancel</Text>
              </TouchableOpacity>

              <TouchableOpacity style={[styles.btnInvest, { flex: 1 }]} onPress={handleConfirmInvestment}>
                <Text style={styles.btnInvestText}>Confirm</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.bgDark, padding: 16 },
  screenTitle: { fontSize: 22, fontWeight: '800', color: colors.textMain, marginVertical: 16 },
  planCard: {
    backgroundColor: colors.bgCard,
    borderRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: colors.bgCardBorder,
    marginBottom: 16,
  },
  planName: { fontSize: 20, fontWeight: '800', color: colors.textMain },
  planRoi: { fontSize: 30, fontWeight: '800', color: colors.primaryCyan, marginVertical: 8 },
  featureRow: { flexDirection: 'row', justifyContent: 'space-between', paddingVertical: 4 },
  featureLabel: { color: colors.textMuted, fontSize: 13 },
  featureValue: { color: colors.textMain, fontWeight: '700', fontSize: 13 },
  btnInvest: {
    backgroundColor: colors.primaryCyan,
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: 'center',
    marginTop: 16,
  },
  btnInvestText: { color: '#090d16', fontWeight: '800', fontSize: 15 },
  card: {
    backgroundColor: colors.bgCard,
    borderRadius: 16,
    padding: 18,
    borderWidth: 1,
    borderColor: colors.bgCardBorder,
    marginVertical: 16,
  },
  cardTitle: { fontSize: 16, fontWeight: '700', color: colors.textMain, marginBottom: 14 },
  invRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.05)',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.8)',
    justifyContent: 'center',
    padding: 20,
  },
  modalContent: {
    backgroundColor: colors.bgDark,
    borderRadius: 20,
    padding: 24,
    borderWidth: 1,
    borderColor: colors.primaryCyan,
  },
  modalTitle: { fontSize: 20, fontWeight: '800', color: colors.textMain, marginBottom: 4 },
  label: { color: colors.textMuted, fontSize: 13, marginBottom: 6 },
  input: {
    backgroundColor: colors.bgInput,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: colors.bgCardBorder,
    padding: 12,
    color: colors.textMain,
    fontSize: 16,
  },
});
