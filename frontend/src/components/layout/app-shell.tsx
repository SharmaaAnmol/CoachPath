'use client';

import * as React from 'react';
import { Sidebar } from './sidebar';
import { Topbar } from './topbar';
import { motion, AnimatePresence } from 'framer-motion';
import { fadeIn } from '@/lib/motion';

export interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  return (
    <div className="min-h-screen bg-slate-50/70 dark:bg-slate-950 flex flex-col md:flex-row">
      {/* Sidebar Navigation */}
      <Sidebar
        isMobileOpen={mobileMenuOpen}
        onMobileClose={() => setMobileMenuOpen(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Topbar onMobileMenuToggle={() => setMobileMenuOpen(true)} />
        <motion.main
          initial="hidden"
          animate="visible"
          variants={fadeIn}
          className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl mx-auto w-full"
        >
          {children}
        </motion.main>
      </div>
    </div>
  );
}
