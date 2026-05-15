function getToken() {
  return localStorage.getItem('tf_token');
}

function getTeamId() {
  return localStorage.getItem('tf_team_id');
}

function setSession(token, teamId) {
  localStorage.setItem('tf_token', token);
  if (teamId != null) {
    localStorage.setItem('tf_team_id', String(teamId));
  } else {
    localStorage.removeItem('tf_team_id');
  }
}

function clearSession() {
  localStorage.removeItem('tf_token');
  localStorage.removeItem('tf_team_id');
}

function requireAuth() {
  if (!getToken()) {
    window.location.href = '/login.html';
    return false;
  }
  return true;
}

function requireTeam() {
  if (!getToken()) { window.location.href = '/login.html'; return false; }
  if (!getTeamId()) { window.location.href = '/team.html'; return false; }
  return true;
}
