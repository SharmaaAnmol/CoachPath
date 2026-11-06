'use client';

import * as React from 'react';
import { Sidebar } from './sidebar';
import { Topbar } from './topbar';
import { motion } from 'framer-motion';
import { fadeIn } from '@/lib/motion';
import { LightField } from '@/components/glass';

export interface AppShellProps {
  children: React.ReactNode;
}

// `dark` switches pages not yet redesigned to their existing dark variants so they sit on the black ground.
export function AppShell({ children }: AppShellProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  return (
    <div className="cp-dark dark relative flex min-h-screen shrink-0 flex-col overflow-x-clip md:flex-row">
      <LightField tone="violet" className="left-[18%] top-[-10%] h-[420px] w-[680px]" />
      <LightField tone="lavender" className="right-[-8%] top-[45%] h-[360px] w-[420px]" />

      <Sidebar isMobileOpen={mobileMenuOpen} onMobileClose={() => setMobileMenuOpen(false)} />

      <div className="relative flex min-w-0 flex-1 flex-col">
        <Topbar onMobileMenuToggle={() => setMobileMenuOpen(true)} />
        <motion.main
          initial="hidden"
          animate="visible"
          variants={fadeIn}
          className="mx-auto w-full max-w-7xl flex-1 p-4 sm:p-6 lg:p-8"
        >
          {children}
        </motion.main>
      </div>
    </div>
  );
}
