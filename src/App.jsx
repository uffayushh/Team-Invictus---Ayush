import { useEffect } from "react";
import { Routes, Route, useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import Navbar from "./components/Navbar";
import UploadPage from "./pages/UploadPage";
import PaperPage from "./pages/PaperPage";
import ChatPage from "./pages/ChatPage";
import FlashcardsPage from "./pages/FlashcardsPage";
import ConceptMapPage from "./pages/ConceptMapPage";
import SlidesPage from "./pages/SlidesPage";
import ComparePage from "./pages/ComparePage";

export default function App() {
  const location = useLocation();

  useEffect(() => {
    document.documentElement.classList.add("dark");
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 transition-colors duration-200 dark:bg-slate-950 dark:text-slate-100">
      <Navbar />
      <main className="mx-auto max-w-5xl p-4 sm:p-6">
        <AnimatePresence mode="wait">
          <motion.div
            key={location.pathname}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            <Routes location={location}>
              <Route path="/" element={<UploadPage />} />
              <Route path="/papers/:id" element={<PaperPage />} />
              <Route path="/papers/:id/chat" element={<ChatPage />} />
              <Route path="/papers/:id/flashcards" element={<FlashcardsPage />} />
              <Route path="/papers/:id/concept-map" element={<ConceptMapPage />} />
              <Route path="/papers/:id/slides" element={<SlidesPage />} />
              <Route path="/compare" element={<ComparePage />} />
            </Routes>
          </motion.div>
        </AnimatePresence>
      </main>
    </div>
  );
}
