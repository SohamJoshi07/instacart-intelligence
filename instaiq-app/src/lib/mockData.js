/**
 * /health doesn't return a per-segment or per-CLV-tier breakdown, so these
 * derive a deterministic mock distribution from the total user count.
 * Swap these out for a real endpoint (e.g. GET /segments/summary) once one
 * exists on the backend.
 */
export function buildSegmentData(totalUsers) {
  const shares = [
    { segment: "Lapsed Users", share: 0.28 },
    { segment: "Occasional Buyers", share: 0.34 },
    { segment: "Regular Shoppers", share: 0.26 },
    { segment: "Weekly Loyalists", share: 0.12 },
  ];
  return shares.map((s) => ({ segment: s.segment, users: Math.round(totalUsers * s.share) }));
}

export function buildClvData(totalUsers) {
  const shares = [
    { tier: "Bronze", share: 0.42 },
    { tier: "Silver", share: 0.31 },
    { tier: "Gold", share: 0.19 },
    { tier: "Platinum", share: 0.08 },
  ];
  return shares.map((s) => ({ tier: s.tier, users: Math.round(totalUsers * s.share) }));
}
