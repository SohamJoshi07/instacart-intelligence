import { NavLink } from "react-router-dom";

export default function NavItem({ to, icon, label, onNavigate }) {
  return (
    <NavLink
      to={to}
      onClick={onNavigate}
      className={({ isActive }) =>
        `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-colors group ${
          isActive ? "text-white bg-brand-soft" : "text-slate-400 hover:text-white hover:bg-white/5"
        }`
      }
    >
      {({ isActive }) => (
        <>
          <span className={`flex-shrink-0 w-5 h-5 ${isActive ? "text-brand" : ""}`}>{icon}</span>
          <span>{label}</span>
          {isActive && <span className="ml-auto w-1.5 h-1.5 rounded-full bg-brand" />}
        </>
      )}
    </NavLink>
  );
}
