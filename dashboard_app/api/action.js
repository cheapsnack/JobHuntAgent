// POST /api/action  { id, action | status, passcode }
// action: approve | reject | applied | interviewing
// Notes are APPENDED, never replaced - the notes field is your audit trail.
const ACTION_TO_STATUS = {
  approve: "APPROVED",
  reject: "REJECTED",
  applied: "APPLIED",
  interviewing: "INTERVIEWING",
};

const ALLOWED_STATUSES = new Set([
  "PENDING_REVIEW", "APPROVED", "REJECTED", "EMAILED", "APPLIED",
  "INTERVIEWING", "OFFER", "EMPLOYER_REJECTED", "FAILED",
]);

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.status(405).json({ error: "POST only" });
    return;
  }
  const { id, action, status, passcode } = req.body || {};
  if (passcode !== process.env.DASHBOARD_PASSCODE) {
    res.status(401).json({ error: "wrong passcode" });
    return;
  }

  let newStatus = null;
  if (action && ACTION_TO_STATUS[action]) newStatus = ACTION_TO_STATUS[action];
  else if (status && ALLOWED_STATUSES.has(status)) newStatus = status;

  if (!id || !newStatus) {
    res.status(400).json({ error: "id and a valid action or status required" });
    return;
  }

  const url = `${process.env.SUPABASE_URL}/rest/v1/jobs?id=eq.${encodeURIComponent(id)}`;
  const authHeaders = {
    apikey: process.env.SUPABASE_SERVICE_KEY,
    Authorization: `Bearer ${process.env.SUPABASE_SERVICE_KEY}`,
    "Content-Type": "application/json",
  };

  let existingNotes = "";
  try {
    const cur = await fetch(`${url}&select=notes`, { headers: authHeaders });
    if (cur.ok) {
      const rows = await cur.json();
      existingNotes = (rows && rows[0] && rows[0].notes) || "";
    }
  } catch (e) { /* append to "" if the read fails */ }

  const stamp = `${newStatus} via dashboard on ${new Date().toISOString()}`;
  const notes = existingNotes.trim() ? `${existingNotes.trim()}\n\n${stamp}` : stamp;
  const patch = { status: newStatus, updated_at: new Date().toISOString(), notes };
  if (newStatus === "APPLIED" || newStatus === "EMAILED") {
    patch.applied_on = new Date().toISOString();
  }

  const r = await fetch(url, {
    method: "PATCH",
    headers: { ...authHeaders, Prefer: "return=representation" },
    body: JSON.stringify(patch),
  });
  const data = await r.json();
  if (!r.ok) {
    res.status(500).json({ error: data });
    return;
  }
  res.status(200).json({ ok: true, job: data[0] || null });
}
