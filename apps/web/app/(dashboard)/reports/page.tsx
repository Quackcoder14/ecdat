'use client';

import { FileText, Download, Calendar, Clock3, ShieldCheck, AlertTriangle, Info, Plus, Search, Filter, Settings } from 'lucide-react';
import { DataTable } from '@/components/ui/data-table';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { useState, ChangeEvent } from 'react';

interface Report {
  id: string;
  name: string;
  type: string;
  project: string;
  generatedAt: string;
  status: string;
}

const mockReports: Report[] = [
  { id: '1', name: 'Executive Summary - Q1 2025', type: 'Executive', project: 'Acme Payments', generatedAt: '2025-01-15', status: 'Completed' },
  { id: '2', name: 'Technical Report - Payments API', type: 'Technical', project: 'Acme Payments', generatedAt: '2025-01-10', status: 'Completed' },
  { id: '3', name: 'CBOM Export - Edge Gateway', type: 'CBOM', project: 'Edge Gateway', generatedAt: '2025-01-08', status: 'Completed' },
  { id: '4', name: 'Risk Assessment - Identity Service', type: 'Risk', project: 'Identity Service', generatedAt: '2025-01-05', status: 'Completed' },
  { id: '5', name: 'Migration Plan - Legacy Clearing', type: 'Migration', project: 'Legacy Clearing', generatedAt: '2025-01-03', status: 'Completed' },
];

export default function ReportsPage() {
  const [search, setSearch] = useState('');

  const filteredReports = mockReports.filter(r => 
    r.name.toLowerCase().includes(search.toLowerCase()) ||
    r.type.toLowerCase().includes(search.toLowerCase()) ||
    r.project.toLowerCase().includes(search.toLowerCase())
  );

  const columns = [
    { key: 'name', header: 'Report Name', sortable: true },
    { 
      key: 'type', 
      header: 'Type', 
      sortable: true,
      render: (row: Report) => (
        <Badge variant="outline">{row.type}</Badge>
      )
    },
    { key: 'project', header: 'Project', sortable: true },
    { key: 'generatedAt', header: 'Generated', sortable: true },
    { 
      key: 'status', 
      header: 'Status',
      render: (row: Report) => (
        <Badge variant="outline" className="bg-green-100 text-green-700">
          <ShieldCheck className="h-3 w-3 mr-1" />
          {row.status}
        </Badge>
      )
    },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Reports</h1>
          <p className="text-muted-foreground">Generate and manage reports</p>
        </div>
        <Button>
          <Plus className="h-4 w-4 mr-2" />
          Generate Report
        </Button>
      </div>

      <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Executive Summary</CardTitle>
            <FileText className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">High-level overview for leadership</p>
            <div className="mt-4 flex gap-2">
              <Button size="sm" variant="outline">
                <FileText className="h-4 w-4 mr-2" />
                Generate
              </Button>
              <Button size="sm" variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Technical Report</CardTitle>
            <Info className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">Detailed technical findings</p>
            <div className="mt-4 flex gap-2">
              <Button size="sm" variant="outline">
                <FileText className="h-4 w-4 mr-2" />
                Generate
              </Button>
              <Button size="sm" variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">CBOM Export</CardTitle>
            <Download className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground">CycloneDX 1.7 compatible CBOM</p>
            <div className="mt-4 flex gap-2">
              <Button size="sm" variant="outline">
                <FileText className="h-4 w-4 mr-2" />
                Generate
              </Button>
              <Button size="sm" variant="outline">
                <Download className="h-4 w-4 mr-2" />
                Export JSON
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Generated Reports</CardTitle>
          <div className="flex gap-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search reports..."
                value={search}
                onChange={(e: ChangeEvent<HTMLInputElement>) => setSearch(e.target.value)}
                className="pl-10 w-64"
              />
            </div>
          </div>
        </CardHeader>
        <CardContent>
          <DataTable
            columns={[
              { key: 'name', header: 'Report Name', sortable: true },
              { 
                key: 'type', 
                header: 'Type', 
                sortable: true,
                render: (row: Report) => (
                  <Badge variant="outline">{row.type}</Badge>
                )
              },
              { key: 'project', header: 'Project', sortable: true },
              { key: 'generatedAt', header: 'Generated', sortable: true },
              { 
                key: 'status', 
                header: 'Status',
                render: (row: Report) => (
                  <Badge variant="outline" className="bg-green-100 text-green-700">
                    <ShieldCheck className="h-3 w-3 mr-1" />
                    {row.status}
                  </Badge>
                )
              },
            ]}
            data={filteredReports}
            keyExtractor={(row) => row.id}
          />
        </CardContent>
      </Card>
    </div>
  );
}