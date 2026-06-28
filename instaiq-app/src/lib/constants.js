export const API_BASE = import.meta.env.VITE_API_URL || "/api";

export const SUMMARY_STATS = {
  totalUsers: 206209,
  criticalChurnUsers: 18432,
  globalReorderRate: 0.589,
  avgCLV: 412.7,
};

export const SEGMENT_COLORS = {
  "Lapsed Users":       "#e31837",
  "Occasional Buyers":  "#3b82f6",
  "Regular Shoppers":   "#f59e0b",
  "Weekly Loyalists":   "#22c55e",
};

export const CLV_COLORS = {
  Bronze:   "#a8714f",
  Silver:   "#8b949e",
  Gold:     "#e3b341",
  Platinum: "#7dd3fc",
};

export const RISK_META = {
  Critical: { dot: "#e31837", text: "#fca5b1", bg: "rgba(227,24,55,0.08)" },
  High:     { dot: "#f59e0b", text: "#fcd34d", bg: "rgba(245,158,11,0.07)" },
  Medium:   { dot: "#eab308", text: "#fef08a", bg: "rgba(234,179,8,0.06)"  },
  Low:      { dot: "#22c55e", text: "#86efac", bg: "rgba(34,197,94,0.06)"  },
};

export const CHURN_DISTRIBUTION = [
  { risk: "Critical", users: 18432,  pct: "8.9%",  action: "Immediate win-back" },
  { risk: "High",     users: 31250,  pct: "15.2%", action: "Re-engagement offers" },
  { risk: "Medium",   users: 54980,  pct: "26.7%", action: "Monitor & nurture" },
  { risk: "Low",      users: 101547, pct: "49.2%", action: "Standard lifecycle" },
];

export const SUGGESTED_QUESTIONS = [
  "How many users are at critical churn risk?",
  "Which segment has the highest CLV?",
  "What is the global reorder rate?",
  "How many association rules were found?",
];

// Demo credentials
export const DEMO_USER = {
  email:    "soham.joshi@atliq.com",
  password: "atliq@2025",
  name:     "Soham Joshi",
  role:     "Business Intelligence Lead",
  avatar:   "SJ",
  dept:     "Data & Analytics",
  joined:   "May 2025",
};

// Fake team members shown in sidebar
export const TEAM_MEMBERS = [
  { name: "Priya Sharma",   role: "Data Engineer",    avatar: "PS", online: true  },
  { name: "Rahul Mehta",    role: "ML Engineer",      avatar: "RM", online: true  },
  { name: "Ananya Iyer",    role: "Product Analyst",  avatar: "AI", online: false },
  { name: "Vikram Nair",    role: "Data Scientist",   avatar: "VN", online: true  },
  { name: "Deepa Krishnan", role: "BI Analyst",       avatar: "DK", online: false },
];

// Fake notifications
export const INITIAL_NOTIFICATIONS = [
  { id: 1, type: "alert",   read: false, time: "2m ago",  title: "Churn spike detected",       body: "Critical churn users up 3.2% in the last 6 hours." },
  { id: 2, type: "info",    read: false, time: "18m ago", title: "Model retrained",             body: "RandomForest retrained on latest data. AUC: 0.912." },
  { id: 3, type: "mention", read: false, time: "1h ago",  title: "Rahul mentioned you",         body: "Tagged you in a note on Weekly Report — check Basket page." },
  { id: 4, type: "success", read: true,  time: "3h ago",  title: "Batch job complete",          body: "206,209 users scored. CLV pipeline finished in 4m 12s." },
  { id: 5, type: "info",    read: true,  time: "Yesterday",title: "New association rules",      body: "147 new rules discovered. Confidence threshold: 0.72." },
];

// Activity log entries
export const ACTIVITY_LOG = [
  { id: 1,  user: "Soham Joshi",   action: "Ran recommendations",  target: "User #14",            time: "Just now",    type: "query"   },
  { id: 2,  user: "Rahul Mehta",   action: "Retrained model",      target: "RandomForest v3",     time: "12m ago",     type: "model"   },
  { id: 3,  user: "Soham Joshi",   action: "Exported report",      target: "Weekly Summary PDF",  time: "1h ago",      type: "export"  },
  { id: 4,  user: "Priya Sharma",  action: "Updated pipeline",     target: "CLV scoring job",     time: "2h ago",      type: "pipeline"},
  { id: 5,  user: "Ananya Iyer",   action: "Queried AI assistant", target: "Churn analysis",      time: "3h ago",      type: "query"   },
  { id: 6,  user: "Vikram Nair",   action: "Added segment rule",   target: "Weekly Loyalists",    time: "5h ago",      type: "model"   },
  { id: 7,  user: "Soham Joshi",   action: "Viewed basket data",   target: "Product #24852",      time: "Yesterday",   type: "query"   },
  { id: 8,  user: "Deepa Krishnan",action: "Generated report",     target: "Executive Summary",   time: "Yesterday",   type: "export"  },
  { id: 9,  user: "Rahul Mehta",   action: "Deployed model",       target: "Churn predictor v2",  time: "2 days ago",  type: "model"   },
  { id: 10, user: "Priya Sharma",  action: "Ingested dataset",     target: "Instacart Q2 2025",   time: "2 days ago",  type: "pipeline"},
  { id: 11, user: "Soham Joshi",   action: "Created dashboard",    target: "CLV Tier View",       time: "3 days ago",  type: "export"  },
  { id: 12, user: "Ananya Iyer",   action: "Reviewed segment",     target: "Lapsed Users cohort", time: "3 days ago",  type: "query"   },
];