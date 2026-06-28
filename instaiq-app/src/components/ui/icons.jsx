const p = { fill: "none", stroke: "currentColor", strokeWidth: "1.5", strokeLinecap: "round", strokeLinejoin: "round" };

export const IcGrid    = (props) => <svg viewBox="0 0 24 24" {...p} {...props}><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>;
export const IcUser    = (props) => <svg viewBox="0 0 24 24" {...p} {...props}><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-6 8-6s8 2 8 6"/></svg>;
export const IcBasket  = (props) => <svg viewBox="0 0 24 24" {...p} {...props}><path d="M5 8h14l-1.5 11.5a2 2 0 0 1-2 1.5H8.5a2 2 0 0 1-2-1.5L5 8z"/><path d="M9 8V6a3 3 0 0 1 6 0v2"/><path d="M9.5 12v4m5-4v4"/></svg>;
export const IcChat    = (props) => <svg viewBox="0 0 24 24" {...p} {...props}><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>;
export const IcReport  = (props) => <svg viewBox="0 0 24 24" {...p} {...props}><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6M16 13H8m8 4H8m2-8H8"/></svg>;
export const IcSearch  = (props) => <svg viewBox="0 0 24 24" {...p} {...props}><circle cx="11" cy="11" r="7"/><path d="m21 21-4.3-4.3"/></svg>;
export const IcSend    = (props) => <svg viewBox="0 0 24 24" {...p} {...props}><path d="m22 2-7 20-4-9-9-4z"/><path d="M22 2 11 13"/></svg>;
export const IcRefresh = (props) => <svg viewBox="0 0 24 24" {...p} {...props}><path d="M21 12a9 9 0 1 1-2.6-6.4"/><path d="M21 3v6h-6"/></svg>;
export const IcLeaf    = (props) => <svg viewBox="0 0 24 24" {...p} {...props}><path d="M11 20A7 7 0 0 1 4 13c0-5 4-9 11-9 0 7-2 11-4 13"/><path d="M4 13c4 0 7 2 7 7"/></svg>;
export const IcBot     = (props) => <svg viewBox="0 0 24 24" {...p} {...props}><rect x="4" y="8" width="16" height="12" rx="2"/><path d="M12 2v4"/><circle cx="9" cy="14" r="1" fill="currentColor" stroke="none"/><circle cx="15" cy="14" r="1" fill="currentColor" stroke="none"/><path d="M9 18h6"/></svg>;
export const IcMenu    = (props) => <svg viewBox="0 0 24 24" {...p} {...props}><path d="M4 7h16M4 12h16M4 17h16"/></svg>;
export const IcAlert   = (props) => <svg viewBox="0 0 24 24" {...p} {...props}><circle cx="12" cy="12" r="10"/><path d="M12 8v5m0 3v.01"/></svg>;
export const IcTrend   = (props) => <svg viewBox="0 0 24 24" {...p} {...props}><path d="M22 7 13.5 15.5l-5-5L2 17"/><path d="M16 7h6v6"/></svg>;
export const IcZap     = (props) => <svg viewBox="0 0 24 24" {...p} {...props}><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" fill="currentColor" stroke="none"/></svg>;
export const IcX       = (props) => <svg viewBox="0 0 24 24" {...p} {...props}><path d="M18 6 6 18M6 6l12 12"/></svg>;
