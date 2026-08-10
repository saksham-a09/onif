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

export default function WalletScreen() {
  const { isDemoMode } = useContext(AuthContext);
  const [wallet, setWallet] = useState({
    balance: 1450.0,
    total_deposited: 1000.0,
    total_withdrawn: 50.0,
  });

  const [deposits, setDeposits] = useState([]);
  const [withdrawals, setWithdrawals] = useState([]);

  // Modals
  const [depModal, setDepModal] = useState(false);
  const [depAmount, setDepAmount] = useState('500.00');
  const [depTxHash, setDepTxHash] = useState('0x892a7f82b1c9842a');

  const [wdrModal, setWdrModal] = useState(false);
  const [wdrType, setWdrType] = useState('PROFIT');
  const [wdrAmount, setWdrAmount] = useState('100.00');
  const [wdrAddress, setWdrAddress] = useState('0x71C7656EC7ab88b098defB751B7401B5f6d8976F');

  const loadWalletData = async () => {
    if (isDemoMode) return;
    try {
      const data = await apiCall('/dashboard/');
      if (data) {
        setWallet({
          balance: data.wallet_balance || 0,
          total_deposited: data.total_deposited || 0,
          total_withdrawn: data.total_withdrawn || 0,
        });
      }

      const deps = await apiCall('/deposits/').catch(() => []);
      if (Array.isArray(deps)) setDeposits(deps);

      const wdrs = await apiCall('/withdrawals/').catch(() => []);
      if (Array.isArray(wdrs)) setWithdrawals(wdrs);
    } catch (err) {
      console.warn('Wallet data fetch error:', err.message);
    }
  };

  useEffect(() => {
    loadWalletData();
  }, []);

  const handleDepositSubmit = async () => {
    const amt = Number(depAmount);
    if (!amt || amt <= 0) {
      Alert.alert('Invalid Amount', 'Please enter a valid deposit amount');
      return;
    }
    try {
      if (!isDemoMode) {
        await apiCall('/deposits/', 'POST', {
          amount: amt,
          network: 'BEP20',
          txn_hash: depTxHash,
          sender_wallet_address: '0xSENDER',
        });
      }
      setDepModal(false);
      Alert.alert('Success', 'Deposit proof submitted for Admin approval!');
      loadWalletData();
    } catch (err) {
      Alert.alert('Deposit Error', err.message);
    }
  };

  const handleWithdrawSubmit = async () => {
    const amt = Number(wdrAmount);
    if (!amt || amt <= 0) {
      Alert.alert('Invalid Amount', 'Please enter a valid withdrawal amount');
      return;
    }
    try {
      if (!isDemoMode) {
        await apiCall('/withdrawals/', 'POST', {
          withdrawal_type: wdrType,
          amount: amt,
          network: 'BEP20',
          wallet_address: wdrAddress,
        });
      }
      setWdrModal(false);
      Alert.alert('Success', 'Withdrawal request submitted for Admin approval!');
      loadWalletData();
    } catch (err) {
      Alert.alert('Withdrawal Error', err.message);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.screenTitle}>Wallet & Transactions</Text>

      {/* Balance Summary Card */}
      <View style={styles.card}>
        <Text style={{ color: colors.textMuted, fontSize: 13 }}>Available Balance</Text>
        <Text style={styles.balanceText}>${Number(wallet.balance).toFixed(2)}</Text>

        <View style={styles.btnRow}>
          <TouchableOpacity style={styles.btnPrimary} onPress={() => setDepModal(true)}>
            <Text style={styles.btnPrimaryText}>+ Deposit</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.btnSecondary} onPress={() => setWdrModal(true)}>
            <Text style={styles.btnSecondaryText}>Withdraw</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Deposits History */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Deposits History</Text>
        {deposits.length === 0 ? (
          <Text style={{ color: colors.textMuted, fontSize: 13 }}>No deposit requests found.</Text>
        ) : (
          deposits.map((dep, idx) => (
            <View key={dep.id || idx} style={styles.row}>
              <View>
                <Text style={{ color: colors.textMain, fontWeight: '700' }}>
                  ${Number(dep.amount).toFixed(2)} ({dep.network})
                </Text>
                <Text style={{ color: colors.textMuted, fontSize: 11 }}>{dep.txn_hash || 'N/A'}</Text>
              </View>
              <Text style={{ color: colors.accentGreen, fontWeight: '700' }}>{dep.status}</Text>
            </View>
          ))
        )}
      </View>

      {/* Withdrawals History */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Withdrawals History</Text>
        {withdrawals.length === 0 ? (
          <Text style={{ color: colors.textMuted, fontSize: 13 }}>No withdrawal requests found.</Text>
        ) : (
          withdrawals.map((wdr, idx) => (
            <View key={wdr.id || idx} style={styles.row}>
              <View>
                <Text style={{ color: colors.textMain, fontWeight: '700' }}>
                  {wdr.withdrawal_type}: ${Number(wdr.amount).toFixed(2)}
                </Text>
                <Text style={{ color: colors.accentGreen, fontSize: 12 }}>
                  Net: ${Number(wdr.net_amount || wdr.amount).toFixed(2)}
                </Text>
              </View>
              <Text style={{ color: colors.accentWarning, fontWeight: '700' }}>{wdr.status}</Text>
            </View>
          ))
        )}
      </View>

      {/* Deposit Modal */}
      <Modal visible={depModal} transparent animationType="slide">
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Deposit Crypto Funds</Text>

            <Text style={styles.label}>Amount ($)</Text>
            <TextInput style={styles.input} value={depAmount} onChangeText={setDepAmount} keyboardType="numeric" />

            <Text style={styles.label}>Transaction Hash (TxID)</Text>
            <TextInput style={styles.input} value={depTxHash} onChangeText={setDepTxHash} />

            <View style={{ flexDirection: 'row', gap: 12, marginTop: 16 }}>
              <TouchableOpacity style={[styles.btnPrimary, { flex: 1, backgroundColor: colors.bgInput }]} onPress={() => setDepModal(false)}>
                <Text style={{ color: colors.textMain, fontWeight: '700' }}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.btnPrimary, { flex: 1 }]} onPress={handleDepositSubmit}>
                <Text style={styles.btnPrimaryText}>Submit</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>

      {/* Withdrawal Modal */}
      <Modal visible={wdrModal} transparent animationType="slide">
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Request Withdrawal</Text>

            <Text style={styles.label}>Amount ($)</Text>
            <TextInput style={styles.input} value={wdrAmount} onChangeText={setWdrAmount} keyboardType="numeric" />

            <Text style={styles.label}>Destination Address</Text>
            <TextInput style={styles.input} value={wdrAddress} onChangeText={setWdrAddress} />

            <View style={{ flexDirection: 'row', gap: 12, marginTop: 16 }}>
              <TouchableOpacity style={[styles.btnPrimary, { flex: 1, backgroundColor: colors.bgInput }]} onPress={() => setWdrModal(false)}>
                <Text style={{ color: colors.textMain, fontWeight: '700' }}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity style={[styles.btnPrimary, { flex: 1 }]} onPress={handleWithdrawSubmit}>
                <Text style={styles.btnPrimaryText}>Submit</Text>
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
  card: {
    backgroundColor: colors.bgCard,
    borderRadius: 16,
    padding: 18,
    borderWidth: 1,
    borderColor: colors.bgCardBorder,
    marginBottom: 16,
  },
  cardTitle: { fontSize: 16, fontWeight: '700', color: colors.textMain, marginBottom: 14 },
  balanceText: { fontSize: 32, fontWeight: '800', color: colors.textMain, marginVertical: 8 },
  btnRow: { flexDirection: 'row', gap: 12, marginTop: 12 },
  btnPrimary: {
    flex: 1,
    backgroundColor: colors.primaryCyan,
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: 'center',
  },
  btnPrimaryText: { color: '#090d16', fontWeight: '800', fontSize: 14 },
  btnSecondary: {
    flex: 1,
    backgroundColor: 'rgba(255, 255, 255, 0.08)',
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: 'center',
  },
  btnSecondaryText: { color: colors.textMain, fontWeight: '600', fontSize: 14 },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.05)',
  },
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.8)', justifyContent: 'center', padding: 20 },
  modalContent: { backgroundColor: colors.bgDark, borderRadius: 20, padding: 24, borderWidth: 1, borderColor: colors.primaryCyan },
  modalTitle: { fontSize: 20, fontWeight: '800', color: colors.textMain, marginBottom: 12 },
  label: { color: colors.textMuted, fontSize: 13, marginTop: 8, marginBottom: 4 },
  input: { backgroundColor: colors.bgInput, borderRadius: 10, borderWidth: 1, borderColor: colors.bgCardBorder, padding: 12, color: colors.textMain, fontSize: 15 },
});
