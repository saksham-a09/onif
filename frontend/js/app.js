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
async function apiCall(endpoint, method = 'GET', body = null, isFormData = false) {
  const headers = {};
  if (state.token) {
    headers['Authorization'] = `Bearer ${state.token}`;
  }
  // Do not set Content-Type for FormData; browser sets multipart boundary automatically
  if (!isFormData) {
    headers['Content-Type'] = 'application/json';
  }

  const options = { method, headers };
  if (body) {
    options.body = isFormData ? body : JSON.stringify(body);
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
  const el = document.getElementById('auth-screen');
  if (el) el.style.display = 'block';
  
  // Hide main app elements so they don't show through the transparent glass auth screen
  const mainWrapper = document.querySelector('.main-wrapper');
  if (mainWrapper) mainWrapper.style.display = 'none';

  initAuthCanvas();
}

function hideAuthOverlay() {
  const el = document.getElementById('auth-screen');
  if (el) el.style.display = 'none';

  // Restore main app elements
  const mainWrapper = document.querySelector('.main-wrapper');
  if (mainWrapper) mainWrapper.style.display = 'flex';
}

function initAuthCanvas() {
  const canvas = document.getElementById('authCanvas');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  const candleW = 9, gapW = 7;
  let candles = [], lastPrice = 100;

  function nextCandle(){
    const open = lastPrice;
    const change = (Math.random() - 0.47) * 5.5;
    const close = Math.max(30, open + change);
    const high = Math.max(open, close) + Math.random() * 3;
    const low = Math.min(open, close) - Math.random() * 3;
    lastPrice = close;
    return {open, close, high, low};
  }
  function seedCandles(width){
    candles = []; lastPrice = 100;
    const count = Math.ceil(width / (candleW + gapW)) + 3;
    for(let i=0;i<count;i++) candles.push(nextCandle());
  }
  function draw(){
    const w = canvas.width / dpr, h = canvas.height / dpr;
    ctx.clearRect(0,0,w,h);
    const values = candles.flatMap(c => [c.high, c.low]);
    const max = Math.max(...values), min = Math.min(...values);
    const pad = 20;
    const scaleY = v => h - pad - ((v - min) / ((max - min) || 1)) * (h - pad * 2);
    candles.forEach((c,i) => {
      const x = i * (candleW + gapW);
      const up = c.close >= c.open;
      ctx.strokeStyle = up ? 'rgba(63,203,140,0.5)' : 'rgba(228,105,78,0.45)';
      ctx.fillStyle = up ? 'rgba(63,203,140,0.22)' : 'rgba(228,105,78,0.20)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(x + candleW/2, scaleY(c.high));
      ctx.lineTo(x + candleW/2, scaleY(c.low));
      ctx.stroke();
      const yO = scaleY(c.open), yC = scaleY(c.close);
      const top = Math.min(yO,yC), hgt = Math.max(2, Math.abs(yO-yC));
      ctx.fillRect(x, top, candleW, hgt);
    });
  }
  function resize(){
    if (!canvas.parentElement) return;
    const rect = canvas.parentElement.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) return;
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.setTransform(dpr,0,0,dpr,0,0);
    seedCandles(rect.width);
    draw();
  }
  if (canvas._resizeHandler) {
    window.removeEventListener('resize', canvas._resizeHandler);
  }
  canvas._resizeHandler = resize;
  window.addEventListener('resize', resize);
  resize();
  if (!reduceMotion && !canvas._intervalId) {
    canvas._intervalId = setInterval(() => {
      const screen = document.getElementById('auth-screen');
      if (screen && screen.style.display === 'none') return;
      candles.shift();
      candles.push(nextCandle());
      draw();
    }, 1300);
  }
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
    container.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline>
            <polyline points="17 6 23 6 23 12"></polyline>
          </svg>
        </div>
        <div class="empty-state-title">No Active Investments</div>
        <div class="empty-state-desc">Select an institutional yield plan to start earning up to 5.0% weekly ROI.</div>
        <button class="btn btn-sm btn-primary" onclick="switchNav('investments')">+ Choose Plan</button>
      </div>
    `;
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
          <span style="color: var(--emerald); font-weight: 700; font-family: var(--font-mono);">
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

  const plansToRender = state.plans.length > 0 ? state.plans : [
    { id: 'starter-plan', name: 'Starter Plan', weekly_roi_rate: 2.50, minimum_amount: 100, maximum_amount: 1000, duration_weeks: 120 },
    { id: 'pro-plan', name: 'Pro Plan', weekly_roi_rate: 3.50, minimum_amount: 500, maximum_amount: 5000, duration_weeks: 120 },
    { id: 'elite-plan', name: 'Elite Plan', weekly_roi_rate: 5.00, minimum_amount: 1000, maximum_amount: 10000, duration_weeks: 120 }
  ];

  plansToRender.forEach((plan, idx) => {
    const isPopular = idx === 1;
    grid.innerHTML += `
      <div class="plan-card ${isPopular ? 'popular' : ''}">
        ${isPopular ? '<div class="popular-badge">Popular TIER</div>' : ''}
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
          Choose ${plan.name}
        </button>
      </div>
    `;
  });
}

function renderMyInvestmentsTable() {
  const tbody = document.getElementById('investments-tbody');
  tbody.innerHTML = '';

  if (state.investments.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" style="padding: 0;">
          <div class="empty-state">
            <div class="empty-state-title">No Investment History</div>
            <div class="empty-state-desc">Choose a plan and submit your deposit proof to start earning weekly ROI.</div>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  state.investments.forEach(inv => {
    const dateStr = inv.created_at ? new Date(inv.created_at).toLocaleString() : 'N/A';
    const credited = Number(inv.total_credited || 0);
    const maxRet = Number(inv.max_return || inv.amount * 3);
    const pct = maxRet > 0 ? Math.min(100, (credited / maxRet) * 100) : 0;
    const isDepositPending = inv.status === 'DEPOSIT_PENDING';
    tbody.innerHTML += `
      <tr>
        <td><b>${inv.plan_name || 'Plan'}</b></td>
        <td style="font-weight: 700; font-family: var(--font-mono);">$${Number(inv.amount).toFixed(2)}</td>
        <td style="color: var(--emerald); font-family: var(--font-mono);">$${maxRet.toFixed(2)}</td>
        <td style="font-family: var(--font-mono);">
          ${isDepositPending ? '—' : `$${credited.toFixed(2)} <small style="color:var(--text-muted);">(${pct.toFixed(0)}%)</small>`}
        </td>
        <td><span class="badge badge-${(inv.status || 'PENDING').toLowerCase().replace('_','-')}">${inv.status.replace('_',' ')}</span></td>
        <td style="font-size: 12px; color: var(--text-muted);">${dateStr}</td>
      </tr>
    `;
  });
}

function renderLedgerTable(items, elementId) {
  const tbody = document.getElementById(elementId);
  tbody.innerHTML = '';

  if (!items || items.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" style="padding: 0;">
          <div class="empty-state">
            <div class="empty-state-title">No Recent Ledger Activity</div>
            <div class="empty-state-desc">All deposits, ROI payouts, direct bonuses, and withdrawals will record here.</div>
          </div>
        </td>
      </tr>
    `;
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
        <td style="color: ${color}; font-weight: 700; font-family: var(--font-mono);">${isCredit ? '+' : '-'}$${Number(item.amount).toFixed(2)}</td>
        <td style="font-family: var(--font-mono);">$${Number(item.balance_after || 0).toFixed(2)}</td>
        <td style="font-size: 13px; color: var(--text-muted);">${item.description} (${dateStr})</td>
      </tr>
    `;
  });
}

function renderDepositsTable() {
  // Deposits are now part of investments — show investment deposit status here
  const tbody = document.getElementById('deposits-tbody');
  tbody.innerHTML = '';

  if (state.investments.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="6" style="padding: 0;">
          <div class="empty-state">
            <div class="empty-state-title">No Investment Deposits</div>
            <div class="empty-state-desc">When you buy an investment plan, your deposit proof will appear here for admin verification.</div>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  state.investments.forEach(inv => {
    const dateStr = inv.deposit_submitted_at
      ? new Date(inv.deposit_submitted_at).toLocaleString()
      : (inv.created_at ? new Date(inv.created_at).toLocaleString() : 'N/A');
    const txHash = inv.deposit_txn_hash || 'N/A';
    const network = inv.deposit_network || '—';
    const statusBadge = inv.status === 'DEPOSIT_PENDING'
      ? '<span class="badge badge-pending">AWAITING REVIEW</span>'
      : `<span class="badge badge-${(inv.status || 'pending').toLowerCase()}">${inv.status}</span>`;
    tbody.innerHTML += `
      <tr>
        <td><b>${inv.plan_name || 'Plan'}</b></td>
        <td style="font-weight: 700; font-family: var(--font-mono);">$${Number(inv.amount).toFixed(2)}</td>
        <td><span class="badge badge-approved">${network}</span></td>
        <td style="font-family: var(--font-mono); font-size: 11px; max-width: 120px; overflow: hidden; text-overflow: ellipsis;">${txHash}</td>
        <td>${statusBadge}</td>
        <td style="font-size: 12px; color: var(--text-muted);">${dateStr}</td>
      </tr>
    `;
  });
}

function renderWithdrawalsTable() {
  const tbody = document.getElementById('withdrawals-tbody');
  tbody.innerHTML = '';

  if (state.withdrawals.length === 0) {
    tbody.innerHTML = `
      <tr>
        <td colspan="5" style="padding: 0;">
          <div class="empty-state">
            <div class="empty-state-title">No Withdrawal History</div>
            <div class="empty-state-desc">Requested payouts and capital redemptions will appear here.</div>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  state.withdrawals.forEach(wdr => {
    const dateStr = wdr.created_at ? new Date(wdr.created_at).toLocaleString() : 'N/A';
    tbody.innerHTML += `
      <tr>
        <td><b>${wdr.withdrawal_type}</b></td>
        <td style="font-weight: 700; font-family: var(--font-mono);">$${Number(wdr.amount).toFixed(2)}</td>
        <td style="color: var(--emerald); font-weight: 700; font-family: var(--font-mono);">$${Number(wdr.net_amount || wdr.amount).toFixed(2)}</td>
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
    teamTbody.innerHTML = `
      <tr>
        <td colspan="4" style="padding: 0;">
          <div class="empty-state">
            <div class="empty-state-title">No Team Members Yet</div>
            <div class="empty-state-desc">Share your referral link to build your team and unlock up to 5 commission levels!</div>
          </div>
        </td>
      </tr>
    `;
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
    commTbody.innerHTML = `
      <tr>
        <td colspan="6" style="padding: 0;">
          <div class="empty-state">
            <div class="empty-state-title">No Commission Records</div>
            <div class="empty-state-desc">Earned direct and ROI downline commissions will record here in real-time.</div>
          </div>
        </td>
      </tr>
    `;
  } else {
    state.commissions.forEach(c => {
      const dateStr = c.created_at ? new Date(c.created_at).toLocaleString() : 'N/A';
      const fromUser = c.from_user_email || (typeof c.from_user === 'object' ? c.from_user.email : c.from_user) || 'Downline User';
      commTbody.innerHTML += `
        <tr>
          <td><b>${c.commission_type === 'DIRECT' ? 'Direct Income (2%)' : 'ROI Income (1.5%)'}</b></td>
          <td><span class="badge badge-active">Level ${c.level}</span></td>
          <td style="font-size: 13px;">${fromUser}</td>
          <td style="color: var(--emerald); font-weight: 700; font-family: var(--font-mono);">+$${Number(c.amount).toFixed(2)}</td>
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
    tbody.innerHTML = `
      <tr>
        <td colspan="4" style="padding: 0;">
          <div class="empty-state">
            <div class="empty-state-title">No Tickets Found</div>
            <div class="empty-state-desc">Submit a ticket using the form on the left if you need assistance.</div>
          </div>
        </td>
      </tr>
    `;
    return;
  }

  state.tickets.forEach(t => {
    const dateStr = t.created_at ? new Date(t.created_at).toLocaleDateString() : 'N/A';
    const statusLower = (t.status || 'OPEN').toLowerCase();
    tbody.innerHTML += `
      <tr style="cursor: pointer;" onclick="openTicketThreadModal('${t.id}')">
        <td><b style="color: var(--emerald-soft);">${t.subject}</b> <span style="font-size: 11px; color: var(--mute);">(Click to view thread)</span></td>
        <td>${t.category || 'General'}</td>
        <td><span class="badge badge-${statusLower}">${t.status || 'OPEN'}</span></td>
        <td style="font-size: 12px; color: var(--text-muted);">${dateStr}</td>
      </tr>
    `;
  });
}

// Support Ticket Thread Modal Functions
async function openTicketThreadModal(ticketId) {
  openModal('modal-ticket-thread');
  document.getElementById('thread-ticket-id').value = ticketId;
  const listContainer = document.getElementById('thread-messages-list');
  listContainer.innerHTML = '<div style="text-align: center; color: var(--mute); padding: 20px;">Loading ticket thread...</div>';
  
  try {
    const ticket = await apiCall(`/support/tickets/${ticketId}/`);
    document.getElementById('thread-ticket-subject').innerText = ticket.subject || 'Ticket Thread';
    const statusLower = (ticket.status || 'OPEN').toLowerCase();
    const statusBadge = document.getElementById('thread-ticket-status');
    statusBadge.className = `badge badge-${statusLower}`;
    statusBadge.innerText = ticket.status || 'OPEN';
    document.getElementById('thread-ticket-date').innerText = ticket.created_at ? new Date(ticket.created_at).toLocaleString() : '';

    renderTicketThreadMessages(ticket);
  } catch (err) {
    listContainer.innerHTML = `<div style="color: var(--accent-danger); padding: 20px;">${err.message}</div>`;
  }
}

function renderTicketThreadMessages(ticket) {
  const listContainer = document.getElementById('thread-messages-list');
  listContainer.innerHTML = '';

  const replies = ticket.replies || [];
  if (replies.length === 0) {
    listContainer.innerHTML = '<div style="text-align: center; color: var(--mute); padding: 20px;">No replies in this thread yet.</div>';
    return;
  }

  replies.forEach(r => {
    const isStaff = r.is_staff_reply;
    const sender = isStaff ? 'Support Team (Staff)' : (r.user_email || 'You');
    const dateStr = r.created_at ? new Date(r.created_at).toLocaleString() : '';
    const bg = isStaff ? 'rgba(63,203,140,0.06)' : 'var(--field)';
    const border = isStaff ? '1px solid rgba(63,203,140,0.2)' : '1px solid var(--line)';
    const nameColor = isStaff ? 'var(--emerald-soft)' : 'var(--text)';
    
    listContainer.innerHTML += `
      <div style="background: ${bg}; border: ${border}; padding: 12px 14px; border-radius: 4px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
          <span style="font-weight: 600; font-size: 13px; color: ${nameColor};">${sender}</span>
          <span style="font-size: 11px; color: var(--mute);">${dateStr}</span>
        </div>
        <div style="font-size: 14px; color: var(--text); white-space: pre-wrap; line-height: 1.5;">${escapeHtml(r.message || '')}</div>
      </div>
    `;
  });

  listContainer.scrollTop = listContainer.scrollHeight;
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.innerText = text;
  return div.innerHTML;
}

async function handleSendReply(e) {
  e.preventDefault();
  const ticketId = document.getElementById('thread-ticket-id').value;
  const messageInput = document.getElementById('thread-reply-message');
  const message = messageInput.value.trim();
  if (!message) return;

  try {
    await apiCall(`/support/tickets/${ticketId}/reply/`, 'POST', { message });
    messageInput.value = '';
    showToast('Reply sent successfully!');
    // Refresh thread modal
    const ticket = await apiCall(`/support/tickets/${ticketId}/`);
    renderTicketThreadMessages(ticket);
    // Refresh tickets list
    await loadAllAPIData();
  } catch (err) {
    showToast(err.message, true);
  }
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
  const loginTab = document.getElementById('tab-login-btn');
  const regTab = document.getElementById('tab-register-btn');
  if (loginTab) loginTab.className = `auth-tab ${tab === 'login' ? 'active' : ''}`;
  if (regTab) regTab.className = `auth-tab ${tab === 'register' ? 'active' : ''}`;

  document.getElementById('form-login').style.display = tab === 'login' ? 'block' : 'none';
  document.getElementById('form-register').style.display = tab === 'register' ? 'block' : 'none';
  document.getElementById('form-verify-otp').style.display = 'none';

  const title = document.getElementById('auth-form-title');
  const subtitle = document.getElementById('auth-form-subtitle');
  if (title && subtitle) {
    if (tab === 'login') {
      title.innerText = 'Sign in to your account';
      subtitle.innerHTML = 'Don\'t have an account? <a href="#" onclick="switchAuthTab(\'register\'); return false;">Register</a>';
    } else {
      title.innerText = 'Create your account';
      subtitle.innerHTML = 'Already have an account? <a href="#" onclick="switchAuthTab(\'login\'); return false;">Sign in</a>';
    }
  }
}

// Show the OTP verification step
let _otpEmail = '';
let _otpCountdownTimer = null;

function showOTPStep(email) {
  _otpEmail = email;
  document.getElementById('form-login').style.display = 'none';
  document.getElementById('form-register').style.display = 'none';
  document.getElementById('form-verify-otp').style.display = 'block';
  document.getElementById('otp-email-display').innerText = email;

  const title = document.getElementById('auth-form-title');
  const subtitle = document.getElementById('auth-form-subtitle');
  if (title) title.innerText = 'Verify your email';
  if (subtitle) subtitle.innerHTML = 'Enter the 6-digit code we sent to your inbox.';

  // Clear all digit inputs
  ['otp-d1','otp-d2','otp-d3','otp-d4','otp-d5','otp-d6'].forEach(id => {
    const el = document.getElementById(id);
    if (el) { el.value = ''; el.className = 'otp-digit'; }
  });

  // Setup digit auto-advance
  initOTPDigitBehaviour();

  // Start 60-second countdown before resend is enabled
  startOTPCountdown(60);

  // Focus first digit
  setTimeout(() => document.getElementById('otp-d1')?.focus(), 100);
}

function initOTPDigitBehaviour() {
  const ids = ['otp-d1','otp-d2','otp-d3','otp-d4','otp-d5','otp-d6'];
  ids.forEach((id, idx) => {
    const el = document.getElementById(id);
    if (!el) return;

    el.addEventListener('input', () => {
      // Only allow digits
      el.value = el.value.replace(/[^0-9]/g, '').slice(-1);
      el.classList.toggle('otp-filled', el.value !== '');
      if (el.value && idx < ids.length - 1) {
        document.getElementById(ids[idx + 1])?.focus();
      }
    });

    el.addEventListener('keydown', (e) => {
      if (e.key === 'Backspace' && !el.value && idx > 0) {
        const prev = document.getElementById(ids[idx - 1]);
        if (prev) { prev.value = ''; prev.classList.remove('otp-filled'); prev.focus(); }
      }
    });

    el.addEventListener('paste', (e) => {
      e.preventDefault();
      const text = (e.clipboardData || window.clipboardData).getData('text').replace(/\D/g, '');
      ids.forEach((did, di) => {
        const d = document.getElementById(did);
        if (d) { d.value = text[di] || ''; d.classList.toggle('otp-filled', !!d.value); }
      });
      const lastFilled = Math.min(text.length, ids.length) - 1;
      if (lastFilled >= 0) document.getElementById(ids[lastFilled])?.focus();
    });
  });
}

function startOTPCountdown(seconds) {
  if (_otpCountdownTimer) clearInterval(_otpCountdownTimer);
  const resendBtn = document.getElementById('otp-resend-btn');
  const countdownEl = document.getElementById('otp-countdown');
  if (resendBtn) resendBtn.disabled = true;
  let remaining = seconds;

  function updateDisplay() {
    if (countdownEl) countdownEl.innerText = remaining > 0 ? `Resend in ${remaining}s` : '';
    if (remaining <= 0) {
      if (resendBtn) resendBtn.disabled = false;
      clearInterval(_otpCountdownTimer);
    }
    remaining--;
  }
  updateDisplay();
  _otpCountdownTimer = setInterval(updateDisplay, 1000);
}

function getOTPValue() {
  return ['otp-d1','otp-d2','otp-d3','otp-d4','otp-d5','otp-d6']
    .map(id => (document.getElementById(id)?.value || '')).join('');
}

function setOTPDigitState(state) {
  ['otp-d1','otp-d2','otp-d3','otp-d4','otp-d5','otp-d6'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.className = `otp-digit${state ? ` ${state}` : ''}`;
  });
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
  const password2 = document.getElementById('reg-password2').value;
  const referral_code = document.getElementById('reg-refcode').value;

  if (password !== password2) {
    showToast('Passwords do not match.', true);
    return;
  }

  const submitBtn = document.getElementById('reg-submit-btn');
  if (submitBtn) { submitBtn.disabled = true; submitBtn.innerText = 'Creating account…'; }

  try {
    // 1. Register the user
    await apiCall('/auth/register/', 'POST', {
      email, username, first_name, last_name, password, password2, referral_code
    });

    // 2. Silently log in to obtain a token (needed by verify-email endpoint)
    const loginData = await apiCall('/auth/login/', 'POST', { email, password });
    if (loginData && loginData.access) {
      state.token = loginData.access;
      localStorage.setItem('finovo_token', loginData.access);
    }

    // 3. Show OTP verification step
    showToast('Account created! Check your email for the verification code.');
    showOTPStep(email);
  } catch (err) {
    showToast(err.message, true);
  } finally {
    if (submitBtn) { submitBtn.disabled = false; submitBtn.innerText = 'Create Account'; }
  }
}

async function handleVerifyOTP(e) {
  e.preventDefault();
  const otp = getOTPValue();
  if (otp.length !== 6) {
    showToast('Please enter the complete 6-digit code.', true);
    return;
  }

  const submitBtn = document.getElementById('otp-submit-btn');
  if (submitBtn) { submitBtn.disabled = true; submitBtn.innerText = 'Verifying…'; }

  try {
    await apiCall('/auth/verify-email/', 'POST', { otp });
    setOTPDigitState('otp-success');
    showToast('Email verified! Welcome to FINOVO 🎉');
    // Short delay so user sees the success state, then load dashboard
    setTimeout(() => loadAllAPIData(), 900);
  } catch (err) {
    setOTPDigitState('otp-error');
    showToast(err.message || 'Invalid or expired OTP.', true);
    // Reset error state after animation
    setTimeout(() => {
      ['otp-d1','otp-d2','otp-d3','otp-d4','otp-d5','otp-d6'].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.className = `otp-digit${el.value ? ' otp-filled' : ''}`;
      });
    }, 600);
  } finally {
    if (submitBtn) { submitBtn.disabled = false; submitBtn.innerText = 'Verify Email'; }
  }
}

async function handleResendOTP() {
  try {
    await apiCall('/auth/resend-otp/', 'POST', { email: _otpEmail });
    showToast('A new code has been sent to your email.');
    startOTPCountdown(60);
    // Clear digit inputs
    ['otp-d1','otp-d2','otp-d3','otp-d4','otp-d5','otp-d6'].forEach(id => {
      const el = document.getElementById(id);
      if (el) { el.value = ''; el.className = 'otp-digit'; }
    });
    setTimeout(() => document.getElementById('otp-d1')?.focus(), 50);
  } catch (err) {
    showToast(err.message || 'Failed to resend OTP.', true);
  }
}

function handleLogout() {
  localStorage.removeItem('finovo_token');
  state.token = null;
  state.user = null;
  showAuthOverlay();
  switchAuthTab('login');
  showToast('Signed out of session.');
}

// Modal Toggle Handlers
function openModal(modalId) {
  document.getElementById(modalId).classList.add('show');
}

function closeModal(modalId) {
  document.getElementById(modalId).classList.remove('show');
}

// ─── Investment Plan Modal & API Creation ─────────────────────────────────────

function openInvestModal(planId, planName, minAmt, maxAmt) {
  document.getElementById('inv-plan-name').value = planId;
  document.getElementById('inv-plan-display').value = planName;
  const input = document.getElementById('inv-amount');
  input.value = minAmt;
  input.min = minAmt;
  input.max = maxAmt;
  // Clear deposit fields
  document.getElementById('inv-network').value = '';
  document.getElementById('inv-txhash').value = '';
  document.getElementById('inv-sender').value = '';
  document.getElementById('inv-proof').value = '';
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
  const amount = document.getElementById('inv-amount').value;
  const network = document.getElementById('inv-network').value;
  const txhash = document.getElementById('inv-txhash').value;
  const sender = document.getElementById('inv-sender').value;
  const proofFile = document.getElementById('inv-proof').files[0];

  if (!network) {
    showToast('Please select a deposit network.', true);
    return;
  }
  if (!txhash && !proofFile) {
    showToast('Please provide a transaction hash or upload a payment screenshot.', true);
    return;
  }

  const formData = new FormData();
  formData.append('plan', plan);
  formData.append('amount', amount);
  formData.append('deposit_network', network);
  if (txhash) formData.append('deposit_txn_hash', txhash);
  if (sender) formData.append('deposit_sender_address', sender);
  if (proofFile) formData.append('deposit_proof', proofFile);

  try {
    await apiCall('/investments/', 'POST', formData, /* isFormData */ true);
    closeModal('modal-invest');
    showToast('Investment submitted! Admin will verify your deposit and activate the plan.');
    await loadAllAPIData();
  } catch (err) {
    showToast(err.message, true);
  }
}

// ─── Withdrawal Fee Calculator & API Submission ────────────────────────────────

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
    await apiCall('/withdrawals/', 'POST', { withdrawal_type, amount, network, wallet_address });
    closeModal('modal-withdraw');
    showToast('Withdrawal request submitted! Awaiting Admin approval.');
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