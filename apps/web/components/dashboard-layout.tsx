'use client';

import { ReactNode } from 'react';
import { Sidebar } from '@/components/sidebar';
import { Topbar } from '@/components/topbar';

interface DashboardLayoutProps {
  children: ReactNode;
}

export function DashboardLayout({ children }: DashboardLayoutProps) {
  return (
    <div className="min-h-screen bg-background flex">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Topbar />
        <main className="flex-1 p-6 overflow-y-auto lg:p-8">
          {children}
        </main>
      </div>
    </div>
  );
}