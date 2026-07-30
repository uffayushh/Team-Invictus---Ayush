// a couple of small pieces reused across pages, nothing fancy

import { motion } from "framer-motion";

export function Button({ children, className = "", ...props }) {
  return (
    <motion.button
      whileHover={{ scale: 1.02, y: -2 }}
      whileTap={{ scale: 0.98 }}
      transition={{ type: "spring", stiffness: 260, damping: 20 }}
      {...props}
      className={`bg-gradient-to-r from-blue-600 to-blue-700 px-4 py-2.5 rounded-xl text-sm font-semibold text-white shadow-[0_4px_12px_rgba(37,99,235,0.3)] transition-all hover:shadow-[0_8px_20px_rgba(37,99,235,0.4)] disabled:cursor-not-allowed disabled:opacity-50 dark:from-blue-500 dark:to-blue-600 dark:shadow-[0_4px_12px_rgba(59,130,246,0.2)] dark:hover:shadow-[0_8px_20px_rgba(59,130,246,0.3)] ${className}`}
    >
      {children}
    </motion.button>
  );
}

export function Card({ children, className = "", interactive = false }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25, ease: "easeOut" }}
      whileHover={interactive ? { y: -2 } : undefined}
      className={`rounded-2xl border border-slate-200/60 bg-gradient-to-br from-white to-slate-50/50 p-5 shadow-[0_4px_16px_rgba(0,0,0,0.04)] transition-all duration-200 dark:border-slate-700/50 dark:from-slate-900 dark:to-slate-900/80 dark:shadow-[0_4px_16px_rgba(0,0,0,0.3)] ${interactive ? "hover:shadow-[0_16px_32px_rgba(0,0,0,0.08)] dark:hover:shadow-[0_16px_32px_rgba(0,0,0,0.4)]" : ""} ${className}`}
    >
      {children}
    </motion.div>
  );
}

export function ErrorBox({ message }) {
  if (!message) return null;
  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      className="mt-3 rounded-xl border border-red-200/70 bg-gradient-to-r from-red-50 to-red-50/50 p-3 text-sm text-red-700 shadow-[0_2px_8px_rgba(220,38,38,0.1)] dark:border-red-900/50 dark:from-red-950/40 dark:to-red-950/20 dark:text-red-300"
    >
      {message}
    </motion.div>
  );
}

export function CitationTag({ page }) {
  return (
    <motion.span
      whileHover={{ scale: 1.05 }}
      className="rounded-full border border-blue-200/70 bg-gradient-to-br from-blue-50 to-blue-50/50 px-2.5 py-1 text-xs font-semibold text-blue-700 shadow-[0_1px_3px_rgba(59,130,246,0.1)] transition-all dark:border-blue-900/50 dark:from-blue-950/40 dark:to-blue-950/20 dark:text-blue-300"
    >
      p.{page}
    </motion.span>
  );
}

export function Badge({ label, type = "default" }) {
  const typeStyles = {
    default: "border-slate-200/70 bg-slate-50/80 text-slate-700 dark:border-slate-700/50 dark:bg-slate-800/50 dark:text-slate-300",
    success: "border-emerald-200/70 bg-emerald-50/80 text-emerald-700 dark:border-emerald-900/50 dark:bg-emerald-950/40 dark:text-emerald-300",
    warning: "border-amber-200/70 bg-amber-50/80 text-amber-700 dark:border-amber-900/50 dark:bg-amber-950/40 dark:text-amber-300",
    info: "border-blue-200/70 bg-blue-50/80 text-blue-700 dark:border-blue-900/50 dark:bg-blue-950/40 dark:text-blue-300",
  };

  return (
    <span className={`inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold shadow-[0_1px_2px_rgba(0,0,0,0.05)] ${typeStyles[type]}`}>
      {label}
    </span>
  );
}

export function SectionTitle({ eyebrow, title, description, action }) {
  return (
    <div className="mb-5 flex flex-wrap items-start justify-between gap-3">
      <div>
        {eyebrow && <p className="mb-1 text-xs font-semibold uppercase tracking-[0.2em] text-blue-600 dark:text-blue-400">{eyebrow}</p>}
        <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100">{title}</h2>
        {description && <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{description}</p>}
      </div>
      {action}
    </div>
  );
}

export function EmptyState({ title, description, action, icon = "📚" }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="rounded-2xl border-2 border-dashed border-slate-200/70 bg-gradient-to-br from-slate-50/80 to-slate-50/40 p-8 text-center shadow-[0_2px_8px_rgba(0,0,0,0.03)] dark:border-slate-700/50 dark:from-slate-800/40 dark:to-slate-800/20 dark:shadow-[0_2px_8px_rgba(0,0,0,0.2)]"
    >
      <motion.div
        className="mb-4 inline-flex text-5xl"
        animate={{ y: [0, -8, 0] }}
        transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
      >
        {icon}
      </motion.div>
      <h3 className="text-lg font-semibold text-slate-800 dark:text-slate-100">{title}</h3>
      <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">{description}</p>
      {action && <div className="mt-5 flex justify-center">{action}</div>}
    </motion.div>
  );
}

export function SkeletonCard() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="rounded-2xl border border-slate-200/60 bg-gradient-to-br from-white to-slate-50/50 p-5 shadow-[0_4px_16px_rgba(0,0,0,0.04)] dark:border-slate-700/50 dark:from-slate-900 dark:to-slate-900/80"
    >
      <motion.div
        className="h-4 w-1/3 rounded-full bg-gradient-to-r from-slate-200 to-slate-100 dark:from-slate-700 dark:to-slate-600"
        animate={{ opacity: [1, 0.5, 1] }}
        transition={{ duration: 1.5, repeat: Infinity }}
      />
      <motion.div
        className="mt-4 h-3 rounded-full bg-gradient-to-r from-slate-200 to-slate-100 dark:from-slate-700 dark:to-slate-600"
        animate={{ opacity: [1, 0.5, 1] }}
        transition={{ duration: 1.5, repeat: Infinity, delay: 0.1 }}
      />
      <motion.div
        className="mt-3 h-3 w-5/6 rounded-full bg-gradient-to-r from-slate-200 to-slate-100 dark:from-slate-700 dark:to-slate-600"
        animate={{ opacity: [1, 0.5, 1] }}
        transition={{ duration: 1.5, repeat: Infinity, delay: 0.2 }}
      />
    </motion.div>
  );
}

export function SkeletonText({ lines = 3 }) {
  return (
    <div className="space-y-3">
      {Array.from({ length: lines }).map((_, i) => (
        <motion.div
          key={i}
          className={`h-3 rounded-full bg-gradient-to-r from-slate-200 to-slate-100 dark:from-slate-700 dark:to-slate-600 ${
            i === lines - 1 ? "w-4/5" : "w-full"
          }`}
          animate={{ opacity: [1, 0.5, 1] }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            delay: i * 0.1,
          }}
        />
      ))}
    </div>
  );
}

export function LoadingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center py-12">
      <motion.div
        className="mb-4 flex gap-2"
        animate={{ scale: [1, 1.1, 1] }}
        transition={{ duration: 1.5, repeat: Infinity }}
      >
        {[0, 1, 2].map((i) => (
          <motion.div
            key={i}
            className="h-3 w-3 rounded-full bg-gradient-to-r from-blue-500 to-blue-600"
            animate={{ y: [0, -12, 0] }}
            transition={{
              duration: 1.2,
              repeat: Infinity,
              delay: i * 0.1,
            }}
          />
        ))}
      </motion.div>
      <p className="text-sm text-slate-600 dark:text-slate-400">Loading...</p>
    </div>
  );
}

export function ProcessingState({ title, description, progress = 0, step = "" }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 14 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className="rounded-2xl border border-blue-200/50 bg-gradient-to-br from-blue-50 to-blue-50/30 p-6 shadow-[0_4px_16px_rgba(59,130,246,0.08)] dark:border-blue-900/50 dark:from-blue-950/30 dark:to-blue-950/10"
    >
      <div className="text-center">
        <motion.div
          className="mb-3 inline-flex"
          animate={{ rotate: 360 }}
          transition={{ duration: 3, repeat: Infinity, ease: "linear" }}
        >
          <div className="text-3xl">⚙️</div>
        </motion.div>

        <h2 className="text-xl font-semibold text-slate-900 dark:text-slate-100">{title}</h2>
        <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">{description}</p>

        {step && <p className="mt-3 text-xs font-semibold text-blue-700 dark:text-blue-300">{step}</p>}

        {progress > 0 && (
          <div className="mt-4">
            <div className="h-2 overflow-hidden rounded-full bg-blue-100 dark:bg-blue-950">
              <motion.div
                className="h-full bg-gradient-to-r from-blue-500 to-blue-600"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.8, ease: "easeOut" }}
              />
            </div>
            <p className="mt-2 text-xs text-blue-700 dark:text-blue-300">{Math.round(progress)}% complete</p>
          </div>
        )}
      </div>
    </motion.div>
  );
}
