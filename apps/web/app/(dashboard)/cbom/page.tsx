'use client';

import { useState } from 'react';
import { Search, Filter, ChevronDown, Download, FileText, ShieldCheck, AlertTriangle, Info } from 'lucide-react';
import { DataTable } from '@/components/ui/data-table';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface CBOMAsset {
  [key: string]: any;
  id: string;
  asset: string;
  type: string;
  purpose: string;
  parameters: string;
  quantumStatus: string;
  confidence: number;
  evidence: string;
  project: string;
}

const mockAssets: CBOMAsset[] = [
  { id: '1', asset: 'RSA', type: 'Algorithm', purpose: 'Digital Signature', parameters: 'Key Size: 2048', quantumStatus: 'VULNERABLE', confidence: 0.98, evidence: 'rsa.generate_private_key(key_size=2048)', project: 'Acme Payments' },
  { id: '2', asset: 'ECDH', type: 'Algorithm', purpose: 'Key Establishment', parameters: 'Curve: P-256', quantumStatus: 'VULNERABLE', confidence: 0.96, evidence: 'ecdh.GenerateKey(curve)', project: 'Edge Gateway' },
  { id: '3', asset: 'AES', type: 'Algorithm', purpose: 'Data Encryption', parameters: 'Key Size: 256, Mode: GCM', quantumStatus: 'NOT_PRIMARY_TARGET', confidence: 0.95, evidence: 'Cipher(AES, GCM)', project: 'Payments API' },
  { id: '4', asset: 'SHA-256', type: 'Algorithm', purpose: 'Hashing', parameters: 'Digest: 256-bit', quantumStatus: 'CONDITIONAL', confidence: 0.92, evidence: 'hashes.Hash(SHA256)', project: 'Identity Service' },
  { id: '5', asset: '3DES', type: 'Algorithm', purpose: 'Data Encryption', parameters: 'Key Size: 168', quantumStatus: 'NOT_PRIMARY_TARGET', confidence: 0.97, evidence: 'DES_set_key_checked', project: 'Legacy Clearing' },
  { id: '6', asset: 'ECDSA', type: 'Algorithm', purpose: 'Digital Signature', parameters: 'Curve: P-256', quantumStatus: 'VULNERABLE', confidence: 0.94, evidence: 'ecdsa.SignASN1', project: 'Edge Gateway' },
  { id: '7', asset: 'TLS 1.2', type: 'Protocol', purpose: 'Transport Security', parameters: 'Cipher: ECDHE_RSA_AES_256_GCM', quantumStatus: 'VULNERABLE', confidence: 0.91, evidence: 'tls.Config', project: 'Edge Gateway' },
  { id: '8', asset: 'OpenSSL', type: 'Library', purpose: 'Crypto Provider', parameters: 'Version: 3.0.8', quantumStatus: 'UNKNOWN', confidence: 0.89, evidence: 'OPENSSL_VERSION_NUMBER', project: 'Multiple' },
];

const quantumStatusColors: Record<string, string> = {
  VULNERABLE: 'bg-red-100 text-red-700',
  NOT_PRIMARY_TARGET: 'bg-green-100 text-green-700',
  CONDITIONAL: 'bg-amber-100 text-amber-700',
  UNKNOWN: 'bg-slate-100 text-slate-700',
};

const quantumStatusIcons: Record<string, any> = {
  VULNERABLE: AlertTriangle,
  NOT_PRIMARY_TARGET: ShieldCheck,
  CONDITIONAL: Info,
  UNKNOWN: Info,
};

export default function CBOMExplorer() {
  const [search, setSearch] = useState('');
  const [assetType, setAssetType] = useState('all');
  const [quantumStatus, setQuantumStatus] = useState('all');
  const [sortConfig, setSortConfig] = useState<{ column: string; direction: 'asc' | 'desc' }>({ column: 'asset', direction: 'asc' });

  const filteredAssets = mockAssets
    .filter((asset) => {
      if (search && !asset.asset.toLowerCase().includes(search.toLowerCase()) && 
          !asset.purpose.toLowerCase().includes(search.toLowerCase())) {
        return false;
      }
      if (assetType !== 'all' && asset.type !== assetType) return false;
      if (quantumStatus !== 'all' && asset.quantumStatus !== quantumStatus) return false;
      return true;
    })
    .sort((a, b) => {
      const dir = sortConfig.direction === 'asc' ? 1 : -1;
      if (a[sortConfig.column] < b[sortConfig.column]) return -1 * dir;
      if (a[sortConfig.column] > b[sortConfig.column]) return 1 * dir;
      return 0;
    });

  const columns = [
    { key: 'asset', header: 'Asset', sortable: true },
    { key: 'type', header: 'Type', sortable: true },
    { key: 'purpose', header: 'Purpose', sortable: true },
    { key: 'parameters', header: 'Parameters' },
    { 
      key: 'quantumStatus', 
      header: 'Quantum Status', 
      sortable: true,
      render: (row: CBOMAsset) => {
        const IconComponent = quantumStatusIcons[row.quantumStatus];
        return (
          <Badge variant="outline" className={cn(quantumStatusColors[row.quantumStatus], 'gap-1')}>
            {IconComponent && <IconComponent className="h-3 w-3" />}
            {row.quantumStatus}
          </Badge>
        );
      }
    },
    { 
      key: 'confidence', 
      header: 'Confidence', 
      sortable: true,
      render: (row: CBOMAsset) => (
        <span className="font-mono text-sm">{Math.round(row.confidence * 100)}%</span>
      )
    },
    { key: 'evidence', header: 'Evidence' },
    { key: 'project', header: 'Project', sortable: true },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">CBOM Explorer</h1>
          <p className="text-muted-foreground">Explore cryptographic inventory across projects</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm">
            <Download className="h-4 w-4 mr-2" />
            Export CBOM
          </Button>
          <Button variant="outline" size="sm">
            <FileText className="h-4 w-4 mr-2" />
            Export CSV
          </Button>
        </div>
      </div>

      <div className="bg-card rounded-lg border border-border p-4">
        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div className="flex-1 max-w-md">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search assets..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          <div className="flex gap-2">
            <Select value={assetType} onValueChange={setAssetType}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="All Types" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Types</SelectItem>
                <SelectItem value="Algorithm">Algorithm</SelectItem>
                <SelectItem value="Protocol">Protocol</SelectItem>
                <SelectItem value="Library">Library</SelectItem>
              </SelectContent>
            </Select>
            <Select value={quantumStatus} onValueChange={setQuantumStatus}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="All Quantum Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Quantum Status</SelectItem>
                <SelectItem value="VULNERABLE">Vulnerable</SelectItem>
                <SelectItem value="NOT_PRIMARY_TARGET">Not Primary Target</SelectItem>
                <SelectItem value="CONDITIONAL">Conditional</SelectItem>
                <SelectItem value="UNKNOWN">Unknown</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      <DataTable
        columns={columns}
        data={filteredAssets}
        keyExtractor={(row) => row.id}
        sorting={sortConfig}
        onSort={(column) => setSortConfig((prev) => ({
          column,
          direction: prev.column === column && prev.direction === 'asc' ? 'desc' : 'asc',
        }))}
      />

      <div className="text-sm text-muted-foreground">
        Showing {filteredAssets.length} of {mockAssets.length} assets
      </div>
    </div>
  );
}