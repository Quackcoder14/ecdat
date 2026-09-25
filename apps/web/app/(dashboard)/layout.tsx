'use client';

import { DashboardLayout } from '@/components/dashboard-layout';
import { DataModeProvider } from '@/app/providers/DataModeProvider';

export default function DashboardGroupLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <DataModeProvider>
      <DashboardLayout>{children}</DashboardLayout>
    </DataModeProvider>
  );
}