const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export async function fetchSystemHealth() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('FastAPI unavailable, using sandbox fallback:', err);
    return null;
  }
}

export async function fetchPipelineNodes() {
  try {
    const res = await fetch(`${API_BASE_URL}/pipeline`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('FastAPI unavailable, using sandbox fallback:', err);
    return null;
  }
}

export async function fetchIncidents() {
  try {
    const res = await fetch(`${API_BASE_URL}/incidents`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('FastAPI unavailable, using sandbox fallback:', err);
    return null;
  }
}

export async function investigateIncidentApi(incidentId: string) {
  try {
    const res = await fetch(`${API_BASE_URL}/incidents/${incidentId}/investigation`, { cache: 'no-store' });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('FastAPI unavailable, using sandbox fallback:', err);
    return null;
  }
}

export async function approvePlanApi(incidentId: string, approver: string = 'HUMAN_OPERATOR') {
  try {
    const res = await fetch(`${API_BASE_URL}/incidents/${incidentId}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ approver })
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('FastAPI unavailable, using sandbox fallback:', err);
    return null;
  }
}

export async function executePlanApi(incidentId: string) {
  try {
    const res = await fetch(`${API_BASE_URL}/incidents/${incidentId}/execute`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('FastAPI unavailable, using sandbox fallback:', err);
    return null;
  }
}

export async function verifyRecoveryApi(incidentId: string) {
  try {
    const res = await fetch(`${API_BASE_URL}/incidents/${incidentId}/verify`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('FastAPI unavailable, using sandbox fallback:', err);
    return null;
  }
}

export async function injectScenarioApi(scenario: string = 'null_customer_id') {
  try {
    const res = await fetch(`${API_BASE_URL}/demo/inject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario })
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('FastAPI unavailable, using sandbox fallback:', err);
    return null;
  }
}

export async function resetDemoApi() {
  try {
    const res = await fetch(`${API_BASE_URL}/demo/reset`, {
      method: 'POST'
    });
    if (!res.ok) throw new Error(`HTTP error ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn('FastAPI unavailable, using sandbox fallback:', err);
    return null;
  }
}
