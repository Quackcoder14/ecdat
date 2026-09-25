'use client';

import { AlertTriangle, ShieldCheck, Clock3, ArrowRight, Download, FileText, Info, ChevronRight } from 'lucide-react';
import { DataTable } from '@/components/ui/data-table';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { useState } from 'react';

interface RiskAsset {
  id: string;
  asset: string;
  algorithm: string;
  usage: string;
  criticality: string;
  dataLifetime: string;
  migrationLeadTime: string;
  quantumStatus: string;
  risk: string;
}

const mockRiskAssets: RiskAsset[] = [
  { id: '1', asset: 'payments-api', algorithm: 'RSA-2048', usage: 'Digital Signature', criticality: 'Critical', dataLifetime: '10 years', migrationLeadTime: '3 years', quantumStatus: 'VULNERABLE', risk: 'HIGH' },
  { id: '2', asset: 'edge-gateway', algorithm: 'ECDH P-256', usage: 'Key Establishment', criticality: 'High', dataLifetime: '7 years', migrationLeadTime: '4 years', quantumStatus: 'VULNERABLE', risk: 'HIGH' },
  { id: '3', asset: 'identity-service', algorithm: 'RSA-3072', usage: 'JWT Signing', criticality: 'Critical', dataLifetime: '15 years', migrationLeadTime: '3 years', quantumStatus: 'VULNERABLE', risk: 'CRITICAL' },
  { id: '4', asset: 'edge-gateway', algorithm: 'ECDSA P-256', usage: 'Authentication', criticality: 'High', dataLifetime: '7 years', migrationLeadTime: '4 years', quantumStatus: 'VULNERABLE', risk: 'HIGH' },
  { id: '5', asset: 'legacy-clearing', algorithm: '3DES', usage: 'Data Encryption', criticality: 'Medium', dataLifetime: '20 years', migrationLeadTime: '2 years', quantumStatus: 'NOT_PRIMARY_TARGET', risk: 'MEDIUM' },
  { id: '6', asset: 'payments-api', algorithm: 'AES-256-GCM', usage: 'Data Encryption', criticality: 'Critical', dataLifetime: '10 years', migrationLeadTime: 'N/A', quantumStatus: 'NOT_PRIMARY_TARGET', risk: 'LOW' },
  { id: '7', asset: 'identity-service', algorithm: 'SHA-256', usage: 'Hashing', criticality: 'High', dataLifetime: '15 years', migrationLeadTime: 'N/A', quantumStatus: 'CONDITIONAL', risk: 'MEDIUM' },
];

const riskColors: Record<string, string> = {
  CRITICAL: 'bg-red-100 text-red-700',
  HIGH: 'bg-red-100 text-red-700',
  MEDIUM: 'bg-amber-100 text-amber-700',
  LOW: 'bg-green-100 text-green-700',
  INFORMATIONAL: 'bg-slate-100 text-slate-700',
};

const riskIcons: Record<string, any> = {
  CRITICAL: AlertTriangle,
  HIGH: AlertTriangle,
  MEDIUM: Info,
  LOW: ShieldCheck,
  INFORMATIONAL: ShieldCheck,
};

export default function QuantumRiskPage() {
  const [selectedAsset, setSelectedAsset] = useState<RiskAsset | null>(null);

  const riskCounts = mockRiskAssets.reduce((acc, asset) => {
    acc[asset.risk] = (acc[asset.risk] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const totalAtRisk = mockRiskAssets.filter(a => ['CRITICAL', 'HIGH'].includes(a.risk)).length;

  const columns = [
    { key: 'asset', header: 'Asset', sortable: true },
    { key: 'algorithm', header: 'Algorithm', sortable: true },
    { key: 'usage', header: 'Usage' },
    { key: 'criticality', header: 'Criticality' },
    { key: 'dataLifetime', header: 'Data Lifetime' },
    { key: 'migrationLeadTime', header: 'Migration Lead Time' },
    { 
      key: 'quantumStatus', 
      header: 'Quantum Status',
      render: (row: RiskAsset) => (
        <Badge variant="outline" className={row.quantumStatus === 'VULNERABLE' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}>
          {row.quantumStatus}
        </Badge>
      )
    },
    { 
      key: 'risk', 
      header: 'Risk', 
      sortable: true,
      render: (row: RiskAsset) => {
        const IconComponent = riskIcons[row.risk];
        return (
          <Badge variant="outline" className={cn(riskColors[row.risk], 'gap-1')}>
            {IconComponent && <IconComponent className="h-3 w-3" />}
            {row.risk}
          </Badge>
        );
      }
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Quantum Risk</h1>
          <p className="text-muted-foreground">
            Prioritize cryptographic assets using algorithm exposure, business context, data lifetime, and migration effort.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total at Risk</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-600">{totalAtRisk}</div>
            <p className="text-xs text-muted-foreground">Critical + High risk assets</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Quantum-Vulnerable</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-600">
              {mockRiskAssets.filter(a => a.quantumStatus === 'VULNERABLE').length}
            </div>
            <p className="text-xs text-muted-foreground">Assets using vulnerable algorithms</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Migration Concern</CardTitle>
            <Clock3 className="h-4 w-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-amber-600">
              {mockRiskAssets.filter(a => {
                const lifetime = parseInt(a.dataLifetime) || 0;
                const leadTime = parseInt(a.migrationLeadTime) || 0;
                return (lifetime + leadTime) > 10;
              }).length}
            </div>
            <p className="text-xs text-muted-foreground">Exceeds 10-year horizon</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Critical Systems</CardTitle>
            <Info className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-foreground">
              {mockRiskAssets.filter(a => a.criticality === 'Critical').length}
            </div>
            <p className="text-xs text-muted-foreground">Critical business systems</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Mosca-Style Planning Assessment</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-muted/50 rounded-lg">
                  <p className="text-sm font-medium text-foreground">Data Security Lifetime (X)</p>
                  <p className="text-2xl font-bold text-foreground">10 years</p>
                  <p className="text-xs text-muted-foreground">Weighted average across assets</p>
                </div>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <p className="text-sm font-medium text-foreground">Migration Lead Time (Y)</p>
                  <p className="text-2xl font-bold text-foreground">3.2 years</p>
                  <p className="text-xs text-muted-foreground">Estimated migration effort</p>
                </div>
                <div className="p-4 bg-muted/50 rounded-lg">
                  <p className="text-sm font-medium text-foreground">Threat Horizon (Z)</p>
                  <p className="text-2xl font-bold text-foreground">10 years</p>
                  <p className="text-xs text-muted-foreground">Planning assumption</p>
                </div>
              </div>
              <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-amber-100 rounded-lg">
                    <Clock3 className="h-5 w-5 text-amber-600" />
                  </div>
                  <div>
                    <p className="font-medium text-amber-800">Within Migration Concern Window</p>
                    <p className="text-sm text-amber-700">
                      X + Y = 13.2 years &gt; Z = 10 years. Migration should be planned now.
                    </p>
                  </div>
                </div>
              </div>
              <div className="text-xs text-muted-foreground">
                <p><strong>Formula:</strong> If (X + Y) &gt; Z, then migration concern exists.</p>
                <p><strong>Note:</strong> This is a planning horizon, not a guaranteed prediction. The threat horizon assumption of 10 years is based on current expert estimates.</p>
              </div>
            </CardContent>
          </Card>
        </div>
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>Risk Distribution</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              {[
                { level: 'CRITICAL', count: riskCounts.CRITICAL || 0 },
                { level: 'HIGH', count: riskCounts.HIGH || 0 },
                { level: 'MEDIUM', count: riskCounts.MEDIUM || 0 },
                { level: 'LOW', count: riskCounts.LOW || 0 },
                { level: 'INFORMATIONAL', count: riskCounts.INFORMATIONAL || 0 },
              ].map(({ level, count }) => (
                <div key={level} className="flex items-center gap-3">
                  <Badge variant="outline" className={cn(riskColors[level], 'w-24')}>
                    {level}
                  </Badge>
                  <div className="flex-1 h-2 bg-muted rounded-full overflow-hidden">
                    <div className="h-full bg-primary rounded-full" style={{ width: `${(count / mockRiskAssets.length) * 100}%` }} />
                  </div>
                  <span className="text-sm font-mono w-10">{count}</span>
                </div>
              ))}
            </CardContent>
          </Card>
        </div>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Risk Assets</CardTitle>
          <div className="flex gap-2">
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export CSV
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <DataTable
            columns={[
              { key: 'asset', header: 'Asset', sortable: true },
              { key: 'algorithm', header: 'Algorithm', sortable: true },
              { key: 'usage', header: 'Usage' },
              { key: 'criticality', header: 'Criticality' },
              { key: 'dataLifetime', header: 'Data Lifetime' },
              { key: 'migrationLeadTime', header: 'Migration Lead Time' },
              { 
                key: 'quantumStatus', 
                header: 'Quantum Status',
                render: (row: any) => (
                  <Badge variant="outline" className={row.quantumStatus === 'VULNERABLE' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}>
                    {row.quantumStatus}
                  </Badge>
                )
              },
              { 
                key: 'risk', 
                header: 'Risk', 
                sortable: true,
                render: (row: RiskAsset) => (
                  <Badge variant="outline" className={cn(riskColors[row.risk], 'gap-1')}>
                    {row.risk}
                  </Badge>
                )
              },
            ]}
            data={mockRiskAssets}
            keyExtractor={(row) => row.id}
            onRowClick={(row) => setSelectedAsset(row)}
          />
        </CardContent>
      </Card>

      {selectedAsset && (
        <Card className="border-primary">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Asset Risk Detail: {selectedAsset.asset}</CardTitle>
            <Button variant="ghost" size="sm" onClick={() => setSelectedAsset(null)}>Close</Button>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground">Algorithm</p>
                <p className="font-mono text-foreground font-semibold">{selectedAsset.algorithm}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Usage</p>
                <p className="font-medium text-foreground">{selectedAsset.usage}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Criticality</p>
                <p className={cn('font-medium', selectedAsset.criticality === 'Critical' && 'text-red-600')}>
                  {selectedAsset.criticality}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Risk Level</p>
                <p className={cn('font-bold', riskColors[selectedAsset.risk])}>
                  <Badge variant="outline" className={cn(riskColors[selectedAsset.risk], 'gap-1')}>
                    {selectedAsset.risk}
                  </Badge>
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Data Lifetime</p>
                <p className="font-medium text-foreground">{selectedAsset.dataLifetime}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Migration Lead Time</p>
                <p className="font-medium text-foreground">{selectedAsset.migrationLeadTime}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Quantum Status</p>
                <Badge variant="outline" className={selectedAsset.quantumStatus === 'VULNERABLE' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'}>
                  {selectedAsset.quantumStatus}
                </Badge>
              </div>
            </div>
            <div className="p-4 bg-muted/50 rounded-lg">
              <h4 className="font-medium text-foreground mb-2">Why this asset is at risk</h4>
              <ul className="text-sm text-muted-foreground space-y-1 list-disc list-inside">
                <li>Uses quantum-vulnerable asymmetric algorithm: {selectedAsset.algorithm}</li>
                <li>Protects {selectedAsset.criticality.toLowerCase()} business system</li>
                <li>Data security lifetime: {selectedAsset.dataLifetime}</li>
                <li>Migration lead time: {selectedAsset.migrationLeadTime}</li>
                <li>Mosca concern: {(parseInt(selectedAsset.dataLifetime) || 0) + (parseInt(selectedAsset.migrationLeadTime) || 0)} &gt; 10 years</li>
              </ul>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}