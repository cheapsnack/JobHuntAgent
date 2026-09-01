// GET /api/jobs?pass=<passcode>&status=PENDING_REVIEW
// status may be a single value, a comma list, or ALL.
export default async function handler(req, res) {
  if (req.query.pass !== process.env.DASHBOARD_PASSCODE) {
    res.status(401).json({ error: "wrong passcode" });
    return;
  }
  const statusParam = req.query.status || "PENDING_REVIEW";
  let filter = "";
  if (statusParam === "ALL") {
    filter = "";
  } else if (statusParam.includes(",")) {
    const list = statusParam.split(",").map((s) => `"${s}"`).join(",");
    filter = `&status=in.(${list})`;
  } else {
    filter = `&status=eq.${encodeURIComponent(statusParam)}`;
  }
  const url = `${process.env.SUPABASE_URL}/rest/v1/jobs?order=date_added.desc&limit=500${filter}`;
  const r = await fetch(url, {
    headers: {
      apikey: process.env.SUPABASE_SERVICE_KEY,
      Authorization: `Bearer ${process.env.SUPABASE_SERVICE_KEY}`,
    },
  });
  res.status(200).json(await r.json());
}
