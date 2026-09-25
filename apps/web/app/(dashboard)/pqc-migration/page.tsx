'use client';

import { ArrowRight, Download, FileText, Info, ShieldCheck, AlertTriangle, Clock3, ChevronRight } from 'lucide-react';
import { DataTable } from '@/components/ui/data-table';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { useState } from 'react';

interface MigrationRec {
  id: string;
  currentCrypto: string;
  usage: string;
  candidate: string;
  complexity: string;
  affectedComponents: string[];
  compatibilityNotes: string;
  performanceNotes: string;
  hybridOption: string;
  priority: string;
}

const mockMigrations: MigrationRec[] = [
  { 
    id: '1', 
    currentCrypto: 'RSA-2048', 
    usage: 'Digital Signature', 
    candidate: 'ML-DSA-65', 
    complexity: 'MEDIUM', 
    affectedComponents: ['payments-api', 'identity-service'], 
    compatibilityNotes: 'Requires protocol updates for JWT/SAML', 
    performanceNotes: 'Larger signatures (2.4KB vs 256 bytes)', 
    hybridOption: 'RSA-2048 + ML-DSA-65',
    priority: 'HIGH' 
  },
  { 
    id: '2', 
    currentCrypto: 'ECDH P-256', 
    usage: 'Key Establishment', 
    candidate: 'ML-KEM-768', 
    complexity: 'HIGH', 
    affectedComponents: ['edge-gateway'], 
    compatibilityNotes: 'TLS 1.3 hybrid KEM support required', 
    performanceNotes: 'Larger keys (1184 bytes vs 65 bytes)', 
    hybridOption: 'ECDH P-256 + ML-KEM-768',
    priority: 'HIGH' 
  },
  { 
    id: '3', 
    currentCrypto: 'ECDSA P-256', 
    usage: 'Authentication', 
    candidate: 'ML-DSA-65', 
    complexity: 'MEDIUM', 
    affectedComponents: ['edge-gateway'], 
    compatibilityNotes: 'TLS 1.3 certificate updates needed', 
    performanceNotes: 'Larger signatures', 
    hybridOption: 'ECDSA P-256 + ML-DSA-65',
    priority: 'HIGH' 
  },
  { 
    id: '4', 
    currentCrypto: 'RSA-3072', 
    usage: 'JWT Signing', 
    candidate: 'ML-DSA-87', 
    complexity: 'MEDIUM', 
    affectedComponents: ['identity-service'], 
    compatibilityNotes: 'SAML assertion format changes', 
    performanceNotes: 'Significantly larger signatures (4.6KB)', 
    hybridOption: 'RSA-3072 + ML-DSA-87',
    priority: 'CRITICAL' 
  },
  { 
    id: '5', 
    currentCrypto: 'AES-256-GCM', 
    usage: 'Data Encryption', 
    candidate: 'Retain (AES-256)', 
    complexity: 'LOW', 
    affectedComponents: ['payments-api'], 
    compatibilityNotes: 'No changes needed - AES-256 is quantum-resistant', 
    performanceNotes: 'No performance impact', 
    hybridOption: 'N/A',
    priority: 'LOW' 
  },
  { 
    id: '6', 
    currentCrypto: 'SHA-256', 
    usage: 'Hashing', 
    candidate: 'Retain (SHA-256)', 
    complexity: 'LOW', 
    affectedComponents: ['identity-service', 'payments-api'], 
    compatibilityNotes: 'Adequate for current use cases', 
    performanceNotes: 'No performance impact', 
    hybridOption: 'N/A',
    priority: 'LOW' 
  },
  { 
    id: '7', 
    currentCrypto: '3DES', 
    usage: 'Data Encryption', 
    candidate: 'AES-256-GCM', 
    complexity: 'MEDIUM', 
    affectedComponents: ['legacy-clearing'], 
    compatibilityNotes: 'Legacy system migration required', 
    performanceNotes: 'Better performance than 3DES', 
    hybridOption: 'N/A (Classical upgrade)',
    priority: 'MEDIUM' 
  },
];

const complexityColors: Record<string, string> = {
  LOW: 'bg-green-100 text-green-700',
  MEDIUM: 'bg-amber-100 text-amber-700',
  HIGH: 'bg-red-100 text-red-700',
};

const priorityColors: Record<string, string> = {
  LOW: 'bg-green-100 text-green-700',
  MEDIUM: 'bg-amber-100 text-amber-700',
  HIGH: 'bg-red-100 text-red-700',
  CRITICAL: 'bg-red-100 text-red-700',
};

export default function PQCMigrationPage() {
  const [selectedRec, setSelectedRec] = useState<MigrationRec | null>(null);

  const priorityCounts = mockMigrations.reduce((acc, rec) => {
    acc[rec.priority] = (acc[rec.priority] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  const columns = [
    { key: 'currentCrypto', header: 'Current Crypto', sortable: true },
    { key: 'usage', header: 'Usage', sortable: true },
    { 
      key: 'candidate', 
      header: 'Candidate', 
      sortable: true,
      render: (row: MigrationRec) => (
        <span className="font-mono text-sm">{row.candidate}</span>
      )
    },
    { 
      key: 'complexity', 
      header: 'Migration Complexity', 
      sortable: true,
      render: (row: MigrationRec) => (
        <Badge variant="outline" className={complexityColors[row.complexity]}>
          {row.complexity}
        </Badge>
      )
    },
    { 
      key: 'affectedComponents', 
      header: 'Affected Components',
      render: (row: MigrationRec) => (
        <span className="text-sm">{row.affectedComponents.join(', ')}</span>
      )
    },
    { 
      key: 'priority', 
      header: 'Priority', 
      sortable: true,
      render: (row: MigrationRec) => (
        <Badge variant="outline" className={priorityColors[row.priority]}>
          {row.priority}
        </Badge>
      )
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Migration Planning</h1>
          <p className="text-muted-foreground">
            Evaluate post-quantum migration candidates with trade-offs and compatibility analysis.
          </p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export CSV
          </Button>
          <Button variant="outline" size="sm">
            <FileText className="h-4 w-4 mr-2" />
            Generate Report
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">High Priority</CardTitle>
            <AlertTriangle className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-600">
              {mockMigrations.filter(r => ['HIGH', 'CRITICAL'].includes(r.priority)).length}
            </div>
            <p className="text-xs text-muted-foreground">Require near-term action</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Hybrid Candidates</CardTitle>
            <Info className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-blue-600">
              {mockMigrations.filter(r => r.hybridOption !== 'N/A').length}
            </div>
            <p className="text-xs text-muted-foreground">Support hybrid deployment</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Low Impact</CardTitle>
            <ShieldCheck className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">
              {mockMigrations.filter(r => r.priority === 'LOW').length}
            </div>
            <p className="text-xs text-muted-foreground">Retain or minimal changes</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Blocking Dependencies</CardTitle>
            <Clock3 className="h-4 w-4 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-amber-600">
              {mockMigrations.filter(r => r.compatibilityNotes.includes('legacy') || r.complexity === 'HIGH').length}
            </div>
            <p className="text-xs text-muted-foreground">Require coordination</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Migration Candidates</CardTitle>
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
              { key: 'currentCrypto', header: 'Current Crypto', sortable: true },
              { key: 'usage', header: 'Usage', sortable: true },
              { key: 'candidate', header: 'Candidate', sortable: true },
              { 
                key: 'complexity', 
                header: 'Migration Complexity', 
                sortable: true,
                render: (row: MigrationRec) => (
                  <Badge variant="outline" className={complexityColors[row.complexity]}>
                    {row.complexity}
                  </Badge>
                )
              },
              { 
                key: 'affectedComponents', 
                header: 'Affected Components',
                render: (row: MigrationRec) => (
                  <span className="text-sm">{row.affectedComponents.join(', ')}</span>
                )
              },
              { 
                key: 'priority', 
                header: 'Priority', 
                sortable: true,
                render: (row: MigrationRec) => (
                  <Badge variant="outline" className={priorityColors[row.priority]}>
                    {row.priority}
                  </Badge>
                )
              },
            ]}
            data={mockMigrations}
            keyExtractor={(row) => row.id}
            onRowClick={(row) => setSelectedRec(row)}
          />
        </CardContent>
      </Card>

      {selectedRec && (
        <Card className="border-primary">
          <CardHeader className="flex flex-row items-center justify-between">
            <CardTitle>Migration Detail: {selectedRec.currentCrypto} → {selectedRec.candidate}</CardTitle>
            <Button variant="ghost" size="sm" onClick={() => setSelectedRec(null)}>Close</Button>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-muted-foreground">Current Cryptography</p>
                  <p className="font-mono text-lg text-foreground font-semibold">{selectedRec.currentCrypto}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Usage</p>
                  <p className="font-medium text-foreground">{selectedRec.usage}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Candidate</p>
                  <p className="font-mono text-lg text-foreground font-semibold">{selectedRec.candidate}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Migration Complexity</p>
                  <Badge variant="outline" className={complexityColors[selectedRec.complexity]}>
                    {selectedRec.complexity}
                  </Badge>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Priority</p>
                  <Badge variant="outline" className={priorityColors[selectedRec.priority]}>
                    {selectedRec.priority}
                  </Badge>
                </div>
              </div>
              <div className="space-y-4 border-t border-border pt-6">
                <div>
                  <p className="text-sm text-muted-foreground">Affected Components</p>
                  <div className="flex flex-wrap gap-2">
                    {selectedRec.affectedComponents.map(comp => (
                      <Badge key={comp} variant="outline">{comp}</Badge>
                    ))}
                  </div>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Hybrid Option</p>
                  <p className="font-mono text-sm text-foreground">
                    {selectedRec.hybridOption}
                  </p>
                </div>
              </div>
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-muted-foreground">Compatibility Notes</p>
                  <p className="text-sm text-muted-foreground">{selectedRec.compatibilityNotes}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground">Performance Notes</p>
                  <p className="text-sm text-muted-foreground">{selectedRec.performanceNotes}</p>
                </div>
              </div>
            </div>

            <div className="p-4 bg-muted/50 rounded-lg">
              <h4 className="font-medium text-foreground mb-3">Suggested Migration Sequence</h4>
              <ol className="space-y-2 text-sm">
                <li className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-bold">1</span>
                  <span>Deploy hybrid mode in staging: {selectedRec.hybridOption}</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-bold">2</span>
                  <span>Validate interoperability with {selectedRec.affectedComponents.join(', ')}</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-bold">3</span>
                  <span>Monitor performance impact: {selectedRec.performanceNotes}</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-bold">4</span>
                  <span>Gradual production rollout with rollback capability</span>
                </li>
                <li className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded-full bg-primary text-primary-foreground flex items-center justify-center text-xs font-bold">5</span>
                  <span>Full migration after validation period</span>
                </li>
              </ol>
            </div>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Why These Recommendations?</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-muted-foreground">
          <p><strong>PQC Algorithm Selection:</strong> Based on NIST FIPS 203/204/205 standards (ML-KEM, ML-DSA, SLH-DSA) and IETF hybrid drafts.</p>
          <p><strong>Complexity Assessment:</strong> Based on protocol changes required, library support maturity, and testing effort.</p>
          <p><strong>Hybrid Deployment:</strong> Recommended for all asymmetric migrations to enable gradual rollout and interoperability during transition.</p>
          <p><strong>Performance Impact:</strong> PQC algorithms have larger keys/signatures; evaluate impact on bandwidth, latency, and storage.</p>
        </CardContent>
      </Card>
    </div>
  );
}