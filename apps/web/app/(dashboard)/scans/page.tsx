'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { ScanProgress } from '@/components/scan-progress';
import {
  Radar,
  Play,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Search,
  Filter,
  Layers,
  ArrowRight,
  Database,
  FileCode,
} from 'lucide-react';
import Link from 'next/link';

interface ScanItem {
  id: string;
  projectName: string;
  artifactName: string;
  scanType: string;
  status: 'COMPLETED' | 'RUNNING' | 'QUEUED' | 'FAILED';
  findingsCount: number;
  progressPercentage: number;
  currentStage: string;
  startedAt: string;
  duration: string;
}

const mockScansList: ScanItem[] = [
  {
    id: 'scan-101',
    projectName: 'Acme Payments Platform',
    artifactName: 'payments-api',
    scanType: 'DemoScanner (Full Pipeline)',
    status: 'COMPLETED',
    findingsCount: 5,
    progressPercentage: 100,
    currentStage: 'COMPLETED',
    startedAt: 'Today, 14:32',
    duration: '1m 24s',
  },
  {
    id: 'scan-102',
    projectName: 'Acme Payments Platform',
    artifactName: 'identity-service',
    scanType: 'Dependency Syft Scanner',
    status: 'COMPLETED',
    findingsCount: 3,
    progressPercentage: 100,
    currentStage: 'COMPLETED',
    startedAt: 'Yesterday, 18:15',
    duration: '45s',
  },
  {
    id: 'scan-103',
    projectName: 'Acme Payments Platform',
    artifactName: 'edge-gateway',
    scanType: 'Container Trivy Scanner',
    status: 'COMPLETED',
    findingsCount: 4,
    progressPercentage: 100,
    currentStage: 'COMPLETED',
    startedAt: '2 days ago',
    duration: '2m 10s',
  },
];

export default function ScansPage() {
  const [scans, setScans] = useState<ScanItem[]>(mockScansList);
  const [activeScan, setActiveScan] = useState<ScanItem | null>(null);
  const [selectedArtifact, setSelectedArtifact] = useState('payments-api');
  const [selectedScanner, setSelectedScanner] = useState('demo_scanner');
  const [isTriggering, setIsTriggering] = useState(false);

  const startNewScan = () => {
    setIsTriggering(true);
    const newScanId = `scan-${Date.now()}`;
    const newScan: ScanItem = {
      id: newScanId,
      projectName: 'Acme Payments Platform',
      artifactName: selectedArtifact,
      scanType: selectedScanner === 'demo_scanner' ? 'Demo Pipeline Engine' : 'Source AST Scanner',
      status: 'RUNNING',
      findingsCount: 0,
      progressPercentage: 25,
      currentStage: 'SCANNING_SOURCE',
      startedAt: 'Just now',
      duration: 'In progress',
    };

    setActiveScan(newScan);

    // Simulate progressive stages
    setTimeout(() => {
      setActiveScan((prev) => prev ? {
        ...prev,
        progressPercentage: 55,
        currentStage: 'CORRELATING',
      } : null);
    }, 1200);

    setTimeout(() => {
      setActiveScan((prev) => prev ? {
        ...prev,
        progressPercentage: 80,
        currentStage: 'GENERATING_CBOM',
      } : null);
    }, 2400);

    setTimeout(() => {
      const completed: ScanItem = {
        ...newScan,
        status: 'COMPLETED',
        progressPercentage: 100,
        currentStage: 'COMPLETED',
        findingsCount: 5,
        duration: '3.6s',
      };
      setActiveScan(completed);
      setScans([completed, ...scans]);
      setIsTriggering(false);
    }, 3600);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            Cryptographic Scans
          </h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Execute deterministic discovery scanners across source code, container images, and certificates
          </p>
        </div>
      </div>

      {/* New Scan Launcher Card */}
      <Card className="border-border">
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-semibold flex items-center gap-2">
            <Play className="h-4 w-4 text-primary" />
            Launch Cryptographic Discovery Scan
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground">Target Artifact</label>
              <select
                value={selectedArtifact}
                onChange={(e) => setSelectedArtifact(e.target.value)}
                className="w-full h-10 px-3 rounded-md border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="payments-api">payments-api (Git Repo)</option>
                <option value="identity-service">identity-service (Git Repo)</option>
                <option value="edge-gateway">edge-gateway (Container)</option>
                <option value="certificate-bundle">certificate-bundle (PEM)</option>
              </select>
            </div>

            <div className="space-y-1.5">
              <label className="text-xs font-semibold text-muted-foreground">Scanner Pipeline</label>
              <select
                value={selectedScanner}
                onChange={(e) => setSelectedScanner(e.target.value)}
                className="w-full h-10 px-3 rounded-md border border-border bg-background text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="demo_scanner">Demo Pipeline Engine (Deterministic)</option>
                <option value="tree_sitter">Tree-sitter AST Scanner</option>
                <option value="syft">Syft Dependency Scanner</option>
                <option value="trivy">Trivy Container Scanner</option>
              </select>
            </div>

            <div>
              <Button
                onClick={startNewScan}
                disabled={isTriggering}
                className="w-full h-10 gap-2 bg-primary hover:bg-primary/90 text-primary-foreground font-medium"
              >
                <Radar className={`h-4 w-4 ${isTriggering ? 'animate-spin' : ''}`} />
                {isTriggering ? 'Executing Pipeline...' : 'Start Scan Run'}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Active Scan Progress if running/completed */}
      {activeScan && (
        <Card className="border-primary/30 bg-primary/5">
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <CardTitle className="text-sm font-semibold flex items-center gap-2">
                <Radar className="h-4 w-4 text-primary animate-pulse" />
                Active Scan Pipeline: {activeScan.artifactName}
              </CardTitle>
              <Badge variant="outline" className="border-primary/30 text-primary">
                {activeScan.status}
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <ScanProgress
              scanId={activeScan.id}
              project={activeScan.projectName}
              source={activeScan.artifactName}
              started={activeScan.startedAt}
              currentStage={activeScan.currentStage}
              progressPercentage={activeScan.progressPercentage}
            />

            {activeScan.status === 'COMPLETED' && (
              <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-between text-xs">
                <div className="flex items-center gap-2 text-emerald-600 dark:text-emerald-400">
                  <CheckCircle2 className="h-4 w-4 shrink-0" />
                  <span>Scan completed successfully! Discovered <strong>5 cryptographic findings</strong> (RSA, ECDH, AES, 3DES).</span>
                </div>
                <div className="flex gap-2">
                  <Link href="/cbom">
                    <Button size="sm" variant="outline" className="h-7 text-xs border-emerald-500/30">
                      Inspect CBOM
                    </Button>
                  </Link>
                  <Link href="/quantum-risk">
                    <Button size="sm" className="h-7 text-xs bg-emerald-600 hover:bg-emerald-700 text-white">
                      View Risk Assessment
                    </Button>
                  </Link>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Scan History Table */}
      <Card className="border-border">
        <CardHeader className="pb-3">
          <CardTitle className="text-base font-semibold">Scan Execution History</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left">
              <thead className="text-xs uppercase bg-muted/50 text-muted-foreground border-y border-border">
                <tr>
                  <th className="py-3 px-4 font-semibold">Scan ID</th>
                  <th className="py-3 px-4 font-semibold">Target / Artifact</th>
                  <th className="py-3 px-4 font-semibold">Scanner Engine</th>
                  <th className="py-3 px-4 font-semibold">Status</th>
                  <th className="py-3 px-4 font-semibold">Findings</th>
                  <th className="py-3 px-4 font-semibold">Executed</th>
                  <th className="py-3 px-4 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border">
                {scans.map((s) => (
                  <tr key={s.id} className="hover:bg-muted/30 transition-colors">
                    <td className="py-3 px-4 font-mono text-xs text-muted-foreground">
                      {s.id}
                    </td>
                    <td className="py-3 px-4">
                      <div className="font-medium text-foreground">{s.artifactName}</div>
                      <div className="text-xs text-muted-foreground">{s.projectName}</div>
                    </td>
                    <td className="py-3 px-4 text-xs text-muted-foreground">
                      {s.scanType}
                    </td>
                    <td className="py-3 px-4">
                      <Badge variant="outline" className="border-emerald-500/30 text-emerald-600 bg-emerald-500/10 text-xs">
                        {s.status}
                      </Badge>
                    </td>
                    <td className="py-3 px-4">
                      <span className="font-semibold text-foreground">{s.findingsCount} findings</span>
                    </td>
                    <td className="py-3 px-4 text-xs text-muted-foreground">
                      {s.startedAt} ({s.duration})
                    </td>
                    <td className="py-3 px-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        <Link href="/cbom">
                          <Button size="sm" variant="ghost" className="h-8 text-xs">
                            CBOM
                          </Button>
                        </Link>
                        <Link href="/quantum-risk">
                          <Button size="sm" variant="outline" className="h-8 text-xs text-destructive hover:bg-destructive/10">
                            Risk
                          </Button>
                        </Link>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
