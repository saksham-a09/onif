import React, { useState, useEffect, useContext } from 'react';
import {
  StyleSheet,
  View,
  Text,
  ScrollView,
  TextInput,
  TouchableOpacity,
  Alert,
} from 'react-native';
import { AuthContext } from '../context/AuthContext';
import { apiCall } from '../config/api';
import colors from '../theme/colors';

export default function SupportScreen() {
  const { isDemoMode } = useContext(AuthContext);
  const [subject, setSubject] = useState('');
  const [message, setMessage] = useState('');
  const [tickets, setTickets] = useState([
    { id: '1', subject: 'Deposit Status Query', category: 'DEPOSIT', status: 'CLOSED' },
  ]);

  const loadTickets = async () => {
    if (isDemoMode) return;
    try {
      const data = await apiCall('/support/tickets/').catch(() => []);
      if (Array.isArray(data)) setTickets(data);
    } catch (err) {
      console.warn('Support ticket load error:', err.message);
    }
  };

  useEffect(() => {
    loadTickets();
  }, []);

  const handleSubmitTicket = async () => {
    if (!subject || !message) {
      Alert.alert('Validation Error', 'Please fill in subject and message');
      return;
    }
    try {
      if (!isDemoMode) {
        await apiCall('/support/tickets/', 'POST', {
          subject,
          category: 'GENERAL',
          message,
        });
      }
      setSubject('');
      setMessage('');
      Alert.alert('Success', 'Support ticket submitted!');
      loadTickets();
    } catch (err) {
      Alert.alert('Error', err.message);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.screenTitle}>Support Center</Text>

      {/* Ticket Form */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Submit Support Request</Text>

        <Text style={styles.label}>Subject</Text>
        <TextInput
          style={styles.input}
          value={subject}
          onChangeText={setSubject}
          placeholder="How can we help you?"
          placeholderTextColor={colors.textDim}
        />

        <Text style={styles.label}>Message</Text>
        <TextInput
          style={[styles.input, { height: 90, textAlignVertical: 'top' }]}
          value={message}
          onChangeText={setMessage}
          multiline
          placeholder="Describe your inquiry..."
          placeholderTextColor={colors.textDim}
        />

        <TouchableOpacity style={styles.btnPrimary} onPress={handleSubmitTicket}>
          <Text style={styles.btnPrimaryText}>Submit Ticket</Text>
        </TouchableOpacity>
      </View>

      {/* Tickets History */}
      <View style={styles.card}>
        <Text style={styles.cardTitle}>Your Support Tickets</Text>
        {tickets.map((t, idx) => (
          <View key={t.id || idx} style={styles.row}>
            <View>
              <Text style={{ color: colors.textMain, fontWeight: '700' }}>{t.subject}</Text>
              <Text style={{ color: colors.textMuted, fontSize: 11 }}>Category: {t.category}</Text>
            </View>
            <Text style={{ color: colors.accentWarning, fontWeight: '700' }}>{t.status || 'OPEN'}</Text>
          </View>
        ))}
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
  label: { color: colors.textMuted, fontSize: 13, marginTop: 8, marginBottom: 4 },
  input: {
    backgroundColor: colors.bgInput,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: colors.bgCardBorder,
    padding: 12,
    color: colors.textMain,
    fontSize: 15,
  },
  btnPrimary: {
    backgroundColor: colors.primaryCyan,
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: 'center',
    marginTop: 16,
  },
  btnPrimaryText: { color: '#090d16', fontWeight: '800', fontSize: 15 },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255, 255, 255, 0.05)',
  },
});
