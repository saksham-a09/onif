/* FINOVO - Pure API Integrated Frontend Application */

const API_BASE = 'http://127.0.0.1:8000/api/v1';

// Global Application State
let state = {
  token: localStorage.getItem('finovo_token') || null,
  user: null,
  wallet: { balance: 0, total_deposited: 0, total_roi_earned: 0, total_direct_income: 0, total_referral_income: 0, total_withdrawn: 0 },
  plans: [],
  investments: [],
  deposits: [],
  withdrawals: [],
  ledger: [],
  team: [],
  commissions: [],
  tickets: [],
  apiConnected: false,
};

// Initialize Application on Page Load
document.addEventListener('DOMContentLoaded', () => {
  if (!state.token) {
    showAuthOverlay();
  } else {
    loadAllAPIData();
  }
});

// Generic Fetch Wrapper with Authorization Header & Error Handling
async function apiCall(endpoint, method = 'GET', body = null) {
  const headers = {
    'Content-Type': 'application/json',
  };
  if (state.token) {
    headers['Authorization'] = `Bearer ${state.token}`;
  }

  const options = { method, headers };
  if (body) {
    options.body = JSON.stringify(body);
  }

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, options);
    state.apiConnected = true;
    updateConnectionBadge(true);

    if (response.status === 401) {
      handleLogout();
      throw new Error('Session expired. Please sign in again.');
    }

    if (!response.ok) {
      const errData = await response.json().catch(() => ({}));
      const errorMsg = parseErrorMessage(errData) || `Server Error (${response.status})`;
      throw new Error(errorMsg);
    }

    if (response.status === 204) return null;
    return await response.json();
  } catch (err) {
    console.error(`[API Error] ${method} ${endpoint}:`, err);
    if (err.message.includes('Failed to fetch')) {
      state.apiConnected = false;
      updateConnectionBadge(false);
      throw new Error('Could not connect to backend server at http://127.0.0.1:8000. Is Docker/Django server running?');
    }
    throw err;
  }
}

function parseErrorMessage(errData) {
  if (typeof errData === 'string') return errData;
  if (errData.detail) return errData.detail;
  if (errData.non_field_errors) return errData.non_field_errors.join(' ');
  const keys = Object.keys(errData);
  if (keys.length > 0) {
    const firstVal = errData[keys[0]];
    return `${keys[0]}: ${Array.isArray(firstVal) ? firstVal.join(' ') : firstVal}`;
  }
  return null;
}

function updateConnectionBadge(isConnected) {
  const badge = document.getElementById('connection-status');
  const text = document.getElementById('status-text');
  if (badge && text) {
    if (isConnected) {
      badge.className = 'status-badge';
      text.innerText = 'API Connected (Live)';
    } else {
      badge.className = 'status-badge demo';
      text.innerText = 'API Disconnected';
    }
  }
}

// Show/Hide Auth Screen
function showAuthOverlay() {
  document.getElementById('auth-screen').style.display = 'flex';
}

function hideAuthOverlay() {
  document.getElementById('auth-screen').style.display = 'none';
}

// Load All Data from Backend API
async function loadAllAPIData() {
  try {
    // 1. Fetch User Profile
    state.user = await apiCall('/auth/profile/');
    hideAuthOverlay();

    // 2. Fetch Dashboard Overview & All Core Resources Parallelly
    const [overviewData, investmentsData, plansData, ledgerData, teamData, commData, depositsData, withdrawalsData, ticketsData] = await Promise.all([
      apiCall('/dashboard/').catch(() => null),
      apiCall('/investments/').catch(() => []),
      apiCall('/investments/plans/').catch(() => []),
      apiCall('/wallet/transactions/').catch(() => []),
      apiCall('/referrals/team/').catch(() => []),
      apiCall('/referrals/commissions/').catch(() => []),
      apiCall('/deposits/').catch(() => []),
      apiCall('/withdrawals/').catch(() => []),
      apiCall('/support/tickets/').catch(() => []),
    ]);

    if (overviewData) {
      state.wallet = {
        balance: overviewData.wallet_balance || 0,
        total_deposited: overviewData.total_deposited || 0,
        total_roi_earned: overviewData.total_roi_earned || 0,
        total_direct_income: overviewData.total_direct_income || 0,
        total_referral_income: overviewData.total_referral_income || 0,
        total_withdrawn: overviewData.total_withdrawn || 0,
      };
      if (overviewData.active_level !== undefined) {
        state.user.active_level = overviewData.active_level;
      }
    }

    state.investments = Array.isArray(investmentsData) ? investmentsData : (investmentsData.results || []);
    state.plans = Array.isArray(plansData) ? plansData : (plansData.results || []);
    state.ledger = Array.isArray(ledgerData) ? ledgerData : (ledgerData.results || []);
    state.team = Array.isArray(teamData) ? teamData : (teamData.results || []);
    state.commissions = Array.isArray(commData) ? commData : (commData.results || []);
    state.deposits = Array.isArray(depositsData) ? depositsData : (depositsData.results || []);
    state.withdrawals = Array.isArray(withdrawalsData) ? withdrawalsData : (withdrawalsData.results || []);
    state.tickets = Array.isArray(ticketsData) ? ticketsData : (ticketsData.results || []);

    renderAllViews();
  } catch (err) {
    showToast(err.message, true);
    showAuthOverlay();
  }
}

// Render All UI Views
function renderAllViews() {
  if (!state.user) return;

  // Header & Sidebar Info
  const fullName = `${state.user.first_name || ''} ${state.user.last_name || ''}`.trim() || state.user.username || state.user.email;
  document.getElementById('sidebar-avatar').innerText = (fullName[0] || 'U').toUpperCase();
  document.getElementById('sidebar-username').innerText = fullName;
  document.getElementById('sidebar-userrole').innerText = `Level ${state.user.active_level || 0} Unlock`;

  // Dashboard Stats
  document.getElementById('dash-wallet-balance').innerText = `$${Number(state.wallet.balance || 0).toFixed(2)}`;
  
  const activeInvestSum = state.investments
    .filter(i => i.status === 'ACTIVE')
    .reduce((sum, item) => sum + Number(item.amount), 0);
  document.getElementById('dash-active-invest').innerText = `$${activeInvestSum.toFixed(2)}`;
  document.getElementById('dash-total-roi').innerText = `$${Number(state.wallet.total_roi_earned || 0).toFixed(2)}`;
  document.getElementById('dash-direct-income').innerText = `$${Number(state.wallet.total_direct_income || 0).toFixed(2)}`;

  // Referral Link
  const refCode = state.user.referral_code || '';
  document.getElementById('dash-ref-link').value = `https://finovo.app/register?ref=${refCode}`;
  document.getElementById('dash-downline-count').innerText = `${state.team.length} Members`;
  document.getElementById('dash-unlocked-levels').innerText = `Level ${state.user.active_level || 0}`;

  // Dashboard Active Investment List
  renderActiveInvestmentsList();

  // Ledger Table
  renderLedgerTable(state.ledger.slice(0, 8), 'dash-ledger-tbody');

  // Wallet View Totals
  document.getElementById('wallet-pg-balance').innerText = `$${Number(state.wallet.balance || 0).toFixed(2)}`;
  document.getElementById('wallet-pg-deposited').innerText = `$${Number(state.wallet.total_deposited || 0).toFixed(2)}`;
  document.getElementById('wallet-pg-withdrawn').innerText = `$${Number(state.wallet.total_withdrawn || 0).toFixed(2)}`;
  const totalEarnings = Number(state.wallet.total_roi_earned || 0) + Number(state.wallet.total_direct_income || 0) + Number(state.wallet.total_referral_income || 0);
  document.getElementById('wallet-pg-earnings').innerText = `$${totalEarnings.toFixed(2)}`;

  // Plans, Investments, Transactions, Referral Views
  renderInvestmentPlansCards();
  renderMyInvestmentsTable();
  renderDepositsTable();
  renderWithdrawalsTable();
  renderReferralView();
  renderSupportTicketsTable();
}

function renderActiveInvestmentsList() {
  const container = document.getElementById('dash-active-investments-list');
  container.innerHTML = '';

  const activeItems = state.investments.filter(i => i.status === 'ACTIVE' || i.status === 'PENDING');
  if (activeItems.length === 0) {
    container.innerHTML = '<p style="color: var(--text-muted); font-size: 13px;">No investments found. Select an Investment Plan to start earning ROI!</p>';
    return;
  }

  activeItems.forEach(inv => {
    const credited = Number(inv.total_credited || 0);
    const maxRet = Number(inv.max_return || inv.amount * 3);
    const pct = maxRet > 0 ? Math.min(100, (credited / maxRet) * 100) : 0;
    container.innerHTML += `
      <div style="margin-bottom: 16px;">
        <div style="display: flex; justify-content: space-between; font-size: 14px; margin-bottom: 6px;">
          <b style="color: var(--text-main);">${inv.plan_name || 'Plan'} ($${Number(inv.amount).toFixed(2)})</b>
          <span style="color: var(--primary-cyan); font-weight: 700;">
            ${inv.status === 'PENDING' ? '<span class="badge badge-pending">PENDING ADMIN APPROVAL</span>' : `$${credited.toFixed(2)} / $${maxRet.toFixed(2)} (${pct.toFixed(0)}%)`}
          </span>
        </div>
        <div class="progress-bar-bg">
          <div class="progress-bar-fill" style="width: ${pct}%"></div>
        </div>
      </div>
    `;
  });
}

function renderInvestmentPlansCards() {
  const grid = document.querySelector('#view-investments .grid-3');
  grid.innerHTML = '';

  if (state.plans.length === 0) {
    grid.innerHTML = '<p style="color: var(--text-muted);">No active investment plans configured.</p>';
    return;
  }

  state.plans.forEach((plan, idx) => {
    const isPopular = idx === 1;
    grid.innerHTML += `
      <div class="plan-card ${isPopular ? 'popular' : ''}">
        ${isPopular ? '<div class="popular-badge">Popular</div>' : ''}
        <div class="plan-name">${plan.name}</div>
        <div class="plan-roi">${Number(plan.weekly_roi_rate).toFixed(2)}% <span>/ weekly ROI</span></div>
        <ul class="plan-features">
          <li>Min Investment <span>$${Number(plan.minimum_amount).toFixed(2)}</span></li>
          <li>Max Investment <span>$${Number(plan.maximum_amount).toFixed(2)}</span></li>
          <li>Max Total Return <span>300.00%</span></li>
          <li>Duration <span>${plan.duration_weeks || 120} Weeks</span></li>
        </ul>
        <button class="btn btn-primary" style="width: 100%; justify-content: center;" 
          onclick="openInvestModal('${plan.id}', '${plan.name}', ${plan.minimum_amount}, ${plan.maximum_amount})">
          Invest ${plan.name}
        </button>
      </div>
    `;
  });
}

function renderMyInvestmentsTable() {
  const tbody = document.getElementById('investments-tbody');
  tbody.innerHTML = '';

  if (state.investments.length === 0) {
    tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--text-muted);">No investments found</td></tr>';
    return;
  }

  state.investments.forEach(inv => {
    const dateStr = inv.created_at ? new Date(inv.created_at).toLocaleString() : 'N/A';
    tbody.innerHTML += `
      <tr>
        <td><b>${inv.plan_name || 'Plan'}</b></td>
        <td style="font-weight: 700;">$${Number(inv.amount).toFixed(2)}</td>
        <td style="color: var(--accent-green);">$${Number(inv.max_return || inv.amount*3).toFixed(2)}</td>
        <td>$${Number(inv.total_credited || 0).toFixed(2)}</td>
        <td><span class="badge badge-${(inv.status || 'PENDING').toLowerCase()}">${inv.status}</span></td>
        <td style="font-size: 12px; color: var(--text-muted);">${dateStr}</td>
      </tr>
    `;
  });
}

function renderLedgerTable(items, elementId) {
  const tbody = document.getElementById(elementId);
  tbody.innerHTML = '';

  if (!items || items.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:var(--text-muted);">No transaction ledger entries found</td></tr>';
    return;
  }

  items.forEach(item => {
    const isCredit = item.transaction_type === 'CREDIT';
    const color = isCredit ? 'var(--accent-green)' : 'var(--accent-danger)';
    const dateStr = item.created_at ? new Date(item.created_at).toLocaleString() : 'Recent';
    tbody.innerHTML += `
      <tr>
        <td><span class="badge ${isCredit ? 'badge-approved' : 'badge-rejected'}">${item.transaction_type}</span></td>
        <td><b>${item.category}</b></td>
        <td style="color: ${color}; font-weight: 700;">${isCredit ? '+' : '-'}$${Number(item.amount).toFixed(2)}</td>
        <td>$${Number(item.balance_after || 0).toFixed(2)}</td>
        <td style="font-size: 13px; color: var(--text-muted);">${item.description} (${dateStr})</td>
      </tr>
    `;
  });
}

function renderDepositsTable() {
  const tbody = document.getElementById('deposits-tbody');
  tbody.innerHTML = '';

  if (state.deposits.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:var(--text-muted);">No deposit history found</td></tr>';
    return;
  }

  state.deposits.forEach(dep => {
    const dateStr = dep.created_at ? new Date(dep.created_at).toLocaleString() : 'N/A';
    tbody.innerHTML += `
      <tr>
        <td style="font-weight: 700;">$${Number(dep.amount).toFixed(2)}</td>
        <td><span class="badge badge-approved">${dep.network}</span></td>
        <td style="font-family: monospace; font-size: 12px;">${dep.txn_hash || 'N/A'}</td>
        <td><span class="badge badge-${(dep.status || 'PENDING').toLowerCase()}">${dep.status}</span></td>
        <td style="font-size: 12px; color: var(--text-muted);">${dateStr}</td>
      </tr>
    `;
  });
}

function renderWithdrawalsTable() {
  const tbody = document.getElementById('withdrawals-tbody');
  tbody.innerHTML = '';

  if (state.withdrawals.length === 0) {
    tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:var(--text-muted);">No withdrawal history found</td></tr>';
    return;
  }

  state.withdrawals.forEach(wdr => {
    const dateStr = wdr.created_at ? new Date(wdr.created_at).toLocaleString() : 'N/A';
    tbody.innerHTML += `
      <tr>
        <td><b>${wdr.withdrawal_type}</b></td>
        <td style="font-weight: 700;">$${Number(wdr.amount).toFixed(2)}</td>
        <td style="color: var(--accent-green); font-weight: 700;">$${Number(wdr.net_amount || wdr.amount).toFixed(2)}</td>
        <td><span class="badge badge-${(wdr.status || 'PENDING').toLowerCase()}">${wdr.status}</span></td>
        <td style="font-size: 12px; color: var(--text-muted);">${dateStr}</td>
      </tr>
    `;
  });
}

function renderReferralView() {
  document.getElementById('ref-summary-direct').innerText = `$${Number(state.wallet.total_direct_income || 0).toFixed(2)}`;
  document.getElementById('ref-summary-roi').innerText = `$${Number(state.wallet.total_referral_income || 0).toFixed(2)}`;

  // Level Unlock Progress List
  const container = document.getElementById('referral-levels-list');
  container.innerHTML = '';
  const currentLvl = state.user.active_level || 0;
  const thresholds = [
    { lvl: 1, req: 2 },
    { lvl: 2, req: 4 },
    { lvl: 3, req: 6 },
    { lvl: 4, req: 8 },
    { lvl: 5, req: 10 }
  ];

  thresholds.forEach(t => {
    const isUnlocked = currentLvl >= t.lvl;
    container.innerHTML += `
      <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 14px; background: rgba(255,255,255,0.03); border-radius: var(--radius-sm); margin-bottom: 8px;">
        <div>
          <b>Level ${t.lvl} Commission (${t.lvl === 1 ? 'Direct 2%' : 'ROI 1.5%'})</b>
          <div style="font-size: 12px; color: var(--text-muted);">Requires ${t.req} Active Direct Referrals</div>
        </div>
        <span class="badge ${isUnlocked ? 'badge-approved' : 'badge-pending'}">${isUnlocked ? 'UNLOCKED' : 'LOCKED'}</span>
      </div>
    `;
  });

  // Downline Team Table
  const teamTbody = document.getElementById('referral-team-tbody');
  teamTbody.innerHTML = '';

  if (state.team.length === 0) {
    teamTbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:var(--text-muted);">No direct downline members yet. Share your referral link!</td></tr>';
  } else {
    state.team.forEach(m => {
      const dateJoined = m.date_joined ? new Date(m.date_joined).toLocaleDateString() : 'N/A';
      teamTbody.innerHTML += `
        <tr>
          <td><b>${m.email}</b></td>
          <td>${m.username || 'N/A'}</td>
          <td style="font-size: 12px; color: var(--text-muted);">${dateJoined}</td>
          <td><span class="badge badge-approved">Direct (Level 1)</span></td>
        </tr>
      `;
    });
  }

  // Commissions Table
  const commTbody = document.getElementById('referral-commissions-tbody');
  commTbody.innerHTML = '';

  if (state.commissions.length === 0) {
    commTbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--text-muted);">No referral commissions recorded yet</td></tr>';
  } else {
    state.commissions.forEach(c => {
      const dateStr = c.created_at ? new Date(c.created_at).toLocaleString() : 'N/A';
      const fromUser = c.from_user_email || (typeof c.from_user === 'object' ? c.from_user.email : c.from_user) || 'Downline User';
      commTbody.innerHTML += `
        <tr>
          <td><b>${c.commission_type === 'DIRECT' ? 'Direct Income (2%)' : 'ROI Income (1.5%)'}</b></td>
          <td><span class="badge badge-active">Level ${c.level}</span></td>
          <td style="font-size: 13px;">${fromUser}</td>
          <td style="color: var(--primary-cyan); font-weight: 700;">+$${Number(c.amount).toFixed(2)}</td>
          <td><span class="badge badge-approved">${c.is_paid ? 'Paid to Wallet' : 'Pending'}</span></td>
          <td style="font-size: 12px; color: var(--text-muted);">${dateStr}</td>
        </tr>
      `;
    });
  }
}

function renderSupportTicketsTable() {
  const tbody = document.getElementById('support-tickets-tbody');
  tbody.innerHTML = '';

  if (state.tickets.length === 0) {
    tbody.innerHTML = '<tr><td colspan="4" style="text-align:center; color:var(--text-muted);">No support tickets submitted</td></tr>';
    return;
  }

  state.tickets.forEach(t => {
    const dateStr = t.created_at ? new Date(t.created_at).toLocaleDateString() : 'N/A';
    tbody.innerHTML += `
      <tr>
        <td><b>${t.subject}</b></td>
        <td>${t.category}</td>
        <td><span class="badge badge-pending">${t.status || 'OPEN'}</span></td>
        <td style="font-size: 12px; color: var(--text-muted);">${dateStr}</td>
      </tr>
    `;
  });
}

// Navigation Tab Switcher
function switchNav(viewName) {
  document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
  document.querySelectorAll('.page-view').forEach(el => el.classList.remove('active'));

  const navItem = document.getElementById(`nav-${viewName}`);
  const viewEl = document.getElementById(`view-${viewName}`);

  if (navItem) navItem.classList.add('active');
  if (viewEl) viewEl.classList.add('active');

  const titles = {
    dashboard: 'Dashboard Overview',
    investments: 'Investment Plans & Portfolio',
    wallet: 'Wallet & Ledger History',
    referrals: 'Multi-Level Referral Downline',
    support: 'Support Center'
  };
  document.getElementById('header-page-title').innerText = titles[viewName] || 'FINOVO Portal';
}

// Auth Handlers
function switchAuthTab(tab) {
  document.getElementById('tab-login-btn').className = `auth-tab ${tab === 'login' ? 'active' : ''}`;
  document.getElementById('tab-register-btn').className = `auth-tab ${tab === 'register' ? 'active' : ''}`;
  document.getElementById('form-login').style.display = tab === 'login' ? 'block' : 'none';
  document.getElementById('form-register').style.display = tab === 'register' ? 'block' : 'none';
}

async function handleLogin(e) {
  e.preventDefault();
  const email = document.getElementById('login-email').value;
  const password = document.getElementById('login-password').value;

  try {
    const data = await apiCall('/auth/login/', 'POST', { email, password });
    if (data && data.access) {
      state.token = data.access;
      localStorage.setItem('finovo_token', data.access);
      showToast('Signed in successfully!');
      await loadAllAPIData();
    }
  } catch (err) {
    showToast(err.message, true);
  }
}

async function handleRegister(e) {
  e.preventDefault();
  const first_name = document.getElementById('reg-firstname').value;
  const last_name = document.getElementById('reg-lastname').value;
  const username = document.getElementById('reg-username').value;
  const email = document.getElementById('reg-email').value;
  const password = document.getElementById('reg-password').value;
  const referral_code = document.getElementById('reg-refcode').value;

  try {
    await apiCall('/auth/register/', 'POST', {
      email, username, first_name, last_name, password, password2: password, referral_code
    });
    showToast('Registration successful! Please sign in with your email & password.');
    switchAuthTab('login');
    document.getElementById('login-email').value = email;
  } catch (err) {
    showToast(err.message, true);
  }
}

function handleLogout() {
  localStorage.removeItem('finovo_token');
  state.token = null;
  state.user = null;
  showAuthOverlay();
  showToast('Signed out of session.');
}

// Modal Toggle Handlers
function openModal(modalId) {
  document.getElementById(modalId).classList.add('show');
}

function closeModal(modalId) {
  document.getElementById(modalId).classList.remove('show');
}

// Deposit API Submission
async function handleDepositSubmit(e) {
  e.preventDefault();
  const amount = Number(document.getElementById('dep-amount').value);
  const network = document.getElementById('dep-network').value;
  const txn_hash = document.getElementById('dep-txhash').value;

  try {
    await apiCall('/deposits/', 'POST', {
      amount,
      network,
      txn_hash,
      sender_wallet_address: '0xSENDER'
    });
    closeModal('modal-deposit');
    showToast('Deposit request submitted! Awaiting Admin approval.');
    await loadAllAPIData();
  } catch (err) {
    showToast(err.message, true);
  }
}

// Withdrawal Fee Calculator & API Submission
function updateWithdrawalFeeCalc() {
  const type = document.getElementById('wdr-type').value;
  const amount = Number(document.getElementById('wdr-amount').value) || 0;

  const fee = type === 'PROFIT' ? 1.00 : 10.00;
  const net = Math.max(0, amount - fee);

  document.getElementById('wdr-fee-preview').innerText = `$${fee.toFixed(2)}`;
  document.getElementById('wdr-net-preview').innerText = `$${net.toFixed(2)}`;
}

async function handleWithdrawSubmit(e) {
  e.preventDefault();
  const withdrawal_type = document.getElementById('wdr-type').value;
  const amount = Number(document.getElementById('wdr-amount').value);
  const network = document.getElementById('wdr-network').value;
  const wallet_address = document.getElementById('wdr-address').value;

  try {
    await apiCall('/withdrawals/', 'POST', {
      withdrawal_type,
      amount,
      network,
      wallet_address
    });
    closeModal('modal-withdraw');
    showToast('Withdrawal request submitted! Awaiting Admin approval.');
    await loadAllAPIData();
  } catch (err) {
    showToast(err.message, true);
  }
}

// Investment Plan Modal & API Creation
function openInvestModal(planId, planName, minAmt, maxAmt) {
  document.getElementById('inv-plan-name').value = planId;
  document.getElementById('inv-plan-display').value = planName;
  const input = document.getElementById('inv-amount');
  input.value = minAmt;
  input.min = minAmt;
  input.max = maxAmt;
  updateMaxReturnCalc();
  openModal('modal-invest');
}

document.getElementById('inv-amount')?.addEventListener('input', updateMaxReturnCalc);

function updateMaxReturnCalc() {
  const amt = Number(document.getElementById('inv-amount').value) || 0;
  const maxReturn = amt * 3.0;
  document.getElementById('inv-max-return').innerText = `$${maxReturn.toFixed(2)}`;
}

async function handleInvestSubmit(e) {
  e.preventDefault();
  const plan = document.getElementById('inv-plan-name').value;
  const amount = Number(document.getElementById('inv-amount').value);

  try {
    await apiCall('/investments/', 'POST', { plan, amount });
    closeModal('modal-invest');
    showToast('Investment request submitted! Direct referral income triggered upon admin approval.');
    await loadAllAPIData();
  } catch (err) {
    showToast(err.message, true);
  }
}

// Copy Referral Link
function copyReferralLink() {
  const input = document.getElementById('dash-ref-link');
  input.select();
  document.execCommand('copy');
  showToast('Referral link copied to clipboard!');
}

// Create Support Ticket via API
async function handleCreateTicket(e) {
  e.preventDefault();
  const subject = document.getElementById('ticket-subject').value;
  const category = document.getElementById('ticket-category').value;
  const message = document.getElementById('ticket-message').value;

  try {
    await apiCall('/support/tickets/', 'POST', { subject, category, message });
    document.getElementById('ticket-subject').value = '';
    document.getElementById('ticket-message').value = '';
    showToast('Support ticket created successfully!');
    await loadAllAPIData();
  } catch (err) {
    showToast(err.message, true);
  }
}

// Toast Helper
function showToast(message, isError = false) {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = 'toast';
  if (isError) {
    toast.style.borderColor = 'var(--accent-danger)';
    toast.style.color = 'var(--accent-danger)';
  }
  toast.innerText = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}