import React, { createContext, useState, useEffect } from 'react';
import { apiCall, setAuthToken } from '../config/api';

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [token, setTokenState] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [isDemoMode, setIsDemoMode] = useState(false);

  // Mock demo user profile for offline demo mode
  const demoUser = {
    email: 'user@mail.com',
    username: 'user',
    first_name: 'First',
    last_name: 'Last',
    referral_code: '12345678',
    active_level: 2,
  };

  const login = async (email, password) => {
    setLoading(true);
    try {
      if (isDemoMode) {
        setUser({ ...demoUser, email });
        setTokenState('demo-token-123');
        setLoading(false);
        return;
      }

      const res = await apiCall('/auth/login/', 'POST', { email, password });
      if (res && res.access) {
        setAuthToken(res.access);
        setTokenState(res.access);
        await fetchProfile();
      }
    } catch (err) {
      console.warn('Login API failed, falling back to Demo Mode:', err.message);
      // Fallback to demo mode if server isn't reachable
      enableDemoMode(email);
    } finally {
      setLoading(false);
    }
  };

  const register = async (data) => {
    setLoading(true);
    try {
      if (isDemoMode) {
        setLoading(false);
        return { success: true };
      }
      await apiCall('/auth/register/', 'POST', data);
      return { success: true };
    } catch (err) {
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const fetchProfile = async () => {
    try {
      const profile = await apiCall('/auth/profile/');
      setUser(profile);
    } catch (err) {
      console.error('Fetch profile error:', err.message);
    }
  };

  const logout = () => {
    setAuthToken(null);
    setTokenState(null);
    setUser(null);
    setIsDemoMode(false);
  };

  const enableDemoMode = (email = 'l1_alice@finovo.com') => {
    setIsDemoMode(true);
    setUser({ ...demoUser, email });
    setTokenState('demo-token-123');
  };

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        loading,
        isDemoMode,
        login,
        register,
        logout,
        enableDemoMode,
        fetchProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};
