import { Link, useParams, useLocation } from "react-router-dom";
import { motion } from "framer-motion";

export default function Navbar() {
  const { id } = useParams();
  const location = useLocation();

  const tabs = id
    ? [
        { to: `/papers/${id}`, label: "Viewer", icon: "📖" },
        { to: `/papers/${id}/chat`, label: "Chat", icon: "💬" },
        { to: `/papers/${id}/flashcards`, label: "Flashcards", icon: "🗂️" },
        { to: `/papers/${id}/concept-map`, label: "Concept Map", icon: "🧠" },
        { to: `/papers/${id}/slides`, label: "Slides", icon: "📊" },
      ]
    : [];

  return (
    <header className="sticky top-0 z-40 border-b border-slate-200/50 bg-gradient-to-r from-white/90 to-white/80 shadow-sm backdrop-blur dark:border-slate-800/50 dark:from-slate-950/90 dark:to-slate-950/80">
      <div className="mx-auto flex min-h-16 max-w-5xl flex-wrap items-center justify-between gap-3 px-4 py-3">
        <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.98 }}>
          <Link to="/" className="text-lg font-bold bg-gradient-to-r from-blue-600 to-blue-700 bg-clip-text text-transparent dark:from-blue-400 dark:to-blue-300">
            📄 Paper Briefing
          </Link>
        </motion.div>

        <nav className="flex flex-wrap items-center gap-1 text-sm">
          {tabs.map((tab, idx) => {
            const active = location.pathname === tab.to;
            return (
              <motion.div
                key={tab.to}
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: idx * 0.05 }}
              >
                <Link
                  to={tab.to}
                  className={`group relative inline-flex items-center rounded-full px-3 py-1.5 text-sm font-medium transition-all ${
                    active
                      ? "bg-gradient-to-r from-blue-100 to-blue-50 text-blue-700 shadow-sm dark:from-blue-950/60 dark:to-blue-950/40 dark:text-blue-300"
                      : "text-slate-600 hover:bg-slate-100/50 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-800/50 dark:hover:text-slate-100"
                  }`}
                >
                  <motion.span className="mr-1" animate={{ y: active ? [0, -2, 0] : 0 }} transition={{ duration: 0.6 }}>
                    {tab.icon}
                  </motion.span>
                  {tab.label}
                  {active && (
                    <motion.div
                      layoutId="activeNav"
                      className="absolute inset-0 rounded-full border-2 border-blue-400/30 dark:border-blue-500/30"
                      transition={{ type: "spring", stiffness: 380, damping: 30 }}
                    />
                  )}
                </Link>
              </motion.div>
            );
          })}
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: tabs.length * 0.05 }}
          >
            <Link
              to="/compare"
              className={`group relative inline-flex items-center rounded-full px-3 py-1.5 text-sm font-medium transition-all ${
                location.pathname === "/compare"
                  ? "bg-gradient-to-r from-blue-100 to-blue-50 text-blue-700 shadow-sm dark:from-blue-950/60 dark:to-blue-950/40 dark:text-blue-300"
                  : "text-slate-600 hover:bg-slate-100/50 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-800/50 dark:hover:text-slate-100"
              }`}
            >
              <span className="mr-1">⚖️</span>
              Compare
              {location.pathname === "/compare" && (
                <motion.div
                  layoutId="activeNav"
                  className="absolute inset-0 rounded-full border-2 border-blue-400/30 dark:border-blue-500/30"
                  transition={{ type: "spring", stiffness: 380, damping: 30 }}
                />
              )}
            </Link>
          </motion.div>
        </nav>
      </div>
    </header>
  );
}
