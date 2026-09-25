'use client';

import { MetricCard } from '@/components/ui/metric-card';
import { InventoryChart } from '@/components/inventory-chart';
import { RecentScansTable } from '@/components/recent-scans-table';
import { RiskDistribution } from '@/components/risk-distribution';

export default function DashboardPage() {
  return (
    <div className="space-y-8">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight text-foreground">
          Cryptographic Readiness Dashboard
        </h1>
        <p className="text-sm text-muted-foreground">
          Overview of enterprise cryptographic assets, quantum exposure, and post-quantum migration readiness.
        </p>
      </div>
      
      <div className="grid grid-cols-1 gap-5 md:grid-cols-2 lg:grid-cols-4">
        <MetricCard
          title="Discovered Crypto Assets"
          value="1,247"
          subtitle="Findings across active services"
          icon="KeyRound"
          trend={{ value: 5.2, positive: true }}
        />
        <MetricCard
          title="Quantum-Vulnerable Assets"
          value="423"
          subtitle="Shor's algorithm exposure"
          icon="ShieldAlert"
          variant="destructive"
          trend={{ value: -2.1, positive: true }}
        />
        <MetricCard
          title="High-Priority Risks"
          value="189"
          subtitle="Mosca theorem priority >= 7"
          icon="AlertTriangle"
          variant="warning"
          trend={{ value: 0, positive: false }}
        />
        <MetricCard
          title="Migration Candidates"
          value="312"
          subtitle="ML-KEM / ML-DSA targets"
          icon="ArrowUpRight"
          variant="success"
          trend={{ value: 12.5, positive: true }}
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <InventoryChart />
        <RiskDistribution />
      </div>

      <RecentScansTable />
    </div>
  );
}