import { useState } from "react";
import { Routes, Route } from "react-router-dom";
import Sidebar              from "./components/layout/Sidebar";
import DashboardPage        from "./pages/DashboardPage";
import UserExplorerPage     from "./pages/UserExplorerPage";
import BasketCompletionPage from "./pages/BasketCompletionPage";
import AnalyticsChatPage    from "./pages/AnalyticsChatPage";
import WeeklyReportPage     from "./pages/WeeklyReportPage";
import ActivityPage         from "./pages/ActivityPage";
import SettingsPage         from "./pages/SettingsPage";

export default function AppLayout() {
  const [open, setOpen] = useState(false);
  const menu = () => setOpen(true);

  return (
    <div className="flex h-full bg-ink">
      <Sidebar open={open} onClose={() => setOpen(false)} />
      <main className="flex-1 min-w-0 overflow-y-auto">
        <Routes>
          <Route path="/"        element={<DashboardPage       onMenuClick={menu} />} />
          <Route path="/explorer"element={<UserExplorerPage    onMenuClick={menu} />} />
          <Route path="/basket"  element={<BasketCompletionPage onMenuClick={menu} />} />
          <Route path="/chat"    element={<AnalyticsChatPage   onMenuClick={menu} />} />
          <Route path="/report"  element={<WeeklyReportPage    onMenuClick={menu} />} />
          <Route path="/activity"element={<ActivityPage        onMenuClick={menu} />} />
          <Route path="/settings"element={<SettingsPage        onMenuClick={menu} />} />
        </Routes>
      </main>
    </div>
  );
}