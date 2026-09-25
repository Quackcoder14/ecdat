'use client';

import Link from 'next/link';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { ArrowRight, CheckCircle2, Clock, Play, ShieldAlert, FileCode2 } from 'lucide-react';

const mockScans = [
  {
    id: 'scan-1',
    projectName: 'Acme Payments Platform',
    artifactName: 'payments-api (Git Repo)',
    scanType: 'Source Analysis + AST',
    status: 'COMPLETED',
    findingsCount: 5,
    criticalCount: 2,
    date: 'Today, 14:32',
    duration: '1m 24s',
  },
  {
    id: 'scan-2',
    projectName: 'Acme Payments Platform',
    artifactName: 'identity-service (Git Repo)',
    scanType: 'Dependency Scanner (Syft)',
    status: 'COMPLETED',
    findingsCount: 3,
    criticalCount: 1,
    date: 'Yesterday, 18:15',
    duration: '45s',
  },
  {
    id: 'scan-3',
    projectName: 'Acme Payments Platform',
    artifactName: 'edge-gateway (Container)',
    scanType: 'Container Scanner (Trivy)',
    status: 'COMPLETED',
    findingsCount: 4,
    criticalCount: 1,
    date: '2 days ago',
    duration: '2m 10s',
  },
  {
    id: 'scan-4',
    projectName: 'Acme Payments Platform',
    artifactName: 'certificate-bundle',
    scanType: 'X.509 OpenSSL Scanner',
    status: 'COMPLETED',
    findingsCount: 2,
    criticalCount: 0,
    date: '3 days ago',
    duration: '18s',
  },
];

export function RecentScansTable() {
  return (
    <Card className="border-border">
      <CardHeader className="flex flex-row items-center justify-between pb-3">
        <div>
          <CardTitle className="text-lg font-semibold text-foreground">
            Recent Cryptographic Scans
          </CardTitle>
          <p className="text-sm text-muted-foreground mt-0.5">
            Discovery scans executed across monitored repositories and services
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Link href="/scans">
            <Button size="sm" variant="outline" className="gap-1.5 text-xs">
              View All Scans
              <ArrowRight className="h-3.5 w-3.5" />
            </Button>
          </Link>
          <Link href="/scans">
            <Button size="sm" className="gap-1.5 text-xs bg-primary hover:bg-primary/90">
              <Play className="h-3.5 w-3.5" />
              New Scan
            </Button>
          </Link>
        </div>
      </CardHeader>

      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs uppercase bg-muted/50 text-muted-foreground border-y border-border">
              <tr>
                <th className="py-3 px-4 font-semibold">Target / Artifact</th>
                <th className="py-3 px-4 font-semibold">Scanner Pipeline</th>
                <th className="py-3 px-4 font-semibold">Status</th>
                <th className="py-3 px-4 font-semibold">Findings</th>
                <th className="py-3 px-4 font-semibold">Executed</th>
                <th className="py-3 px-4 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {mockScans.map((scan) => (
                <tr key={scan.id} className="hover:bg-muted/30 transition-colors">
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-2.5">
                      <div className="p-2 rounded-md bg-primary/10 text-primary">
                        <FileCode2 className="h-4 w-4" />
                      </div>
                      <div>
                        <div className="font-medium text-foreground">{scan.artifactName}</div>
                        <div className="text-xs text-muted-foreground">{scan.projectName}</div>
                      </div>
                    </div>
                  </td>
                  <td className="py-3.5 px-4 text-muted-foreground">
                    {scan.scanType}
                  </td>
                  <td className="py-3.5 px-4">
                    <Badge variant="outline" className="gap-1 border-emerald-500/30 text-emerald-600 bg-emerald-500/10 font-normal text-xs">
                      <CheckCircle2 className="h-3 w-3" />
                      Completed
                    </Badge>
                  </td>
                  <td className="py-3.5 px-4">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-foreground">{scan.findingsCount}</span>
                      {scan.criticalCount > 0 && (
                        <Badge variant="destructive" className="text-[10px] px-1.5 py-0 h-4">
                          {scan.criticalCount} high risk
                        </Badge>
                      )}
                    </div>
                  </td>
                  <td className="py-3.5 px-4 text-xs text-muted-foreground">
                    <div className="flex items-center gap-1.5">
                      <Clock className="h-3.5 w-3.5" />
                      <span>{scan.date}</span>
                    </div>
                  </td>
                  <td className="py-3.5 px-4 text-right">
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
  );
}
