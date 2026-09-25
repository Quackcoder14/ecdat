'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  FolderKanban,
  Plus,
  Search,
  ExternalLink,
  ShieldAlert,
  Play,
  Database,
  FileCode2,
  Box,
  Layers,
  Calendar,
  CheckCircle2,
} from 'lucide-react';
import Link from 'next/link';

interface ProjectItem {
  id: string;
  name: string;
  description: string;
  status: 'ACTIVE' | 'ARCHIVED';
  artifactsCount: number;
  findingsCount: number;
  criticalCount: number;
  lastScan: string;
  artifacts: { name: string; type: string; status: string }[];
}

const initialProjects: ProjectItem[] = [
  {
    id: 'proj-1',
    name: 'Acme Payments Platform',
    description: 'Representative payment, identity, and API infrastructure used for ECDAT cryptographic discovery.',
    status: 'ACTIVE',
    artifactsCount: 6,
    findingsCount: 5,
    criticalCount: 2,
    lastScan: 'Today, 14:32',
    artifacts: [
      { name: 'payments-api', type: 'Git Repository', status: 'Scanned' },
      { name: 'identity-service', type: 'Git Repository', status: 'Scanned' },
      { name: 'edge-gateway', type: 'Git Repository', status: 'Scanned' },
      { name: 'legacy-clearing-service', type: 'Git Repository', status: 'Scanned' },
      { name: 'certificate-bundle', type: 'Certificates (PEM)', status: 'Scanned' },
      { name: 'container-image', type: 'OCI Container', status: 'Scanned' },
    ],
  },
  {
    id: 'proj-2',
    name: 'Customer Identity & Access (CIAM)',
    description: 'OAuth2/OIDC provider and biometric authentication service cluster.',
    status: 'ACTIVE',
    artifactsCount: 3,
    findingsCount: 4,
    criticalCount: 1,
    lastScan: 'Yesterday, 19:40',
    artifacts: [
      { name: 'auth-server-v2', type: 'Git Repository', status: 'Scanned' },
      { name: 'token-signer-hsm', type: 'PKCS#11 Library', status: 'Scanned' },
      { name: 'gateway-ingress-tls', type: 'Certificate Bundle', status: 'Scanned' },
    ],
  },
];

export default function ProjectsPage() {
  const [projects, setProjects] = useState<ProjectItem[]>(initialProjects);
  const [search, setSearch] = useState('');
  const [showNewModal, setShowNewModal] = useState(false);
  const [newProjectName, setNewProjectName] = useState('');
  const [newProjectDesc, setNewProjectDesc] = useState('');

  const filteredProjects = projects.filter((p) =>
    p.name.toLowerCase().includes(search.toLowerCase()) ||
    p.description.toLowerCase().includes(search.toLowerCase())
  );

  const handleCreateProject = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newProjectName.trim()) return;

    const newProj: ProjectItem = {
      id: `proj-${Date.now()}`,
      name: newProjectName,
      description: newProjectDesc || 'Enterprise service monitored by ECDAT.',
      status: 'ACTIVE',
      artifactsCount: 1,
      findingsCount: 0,
      criticalCount: 0,
      lastScan: 'Just now',
      artifacts: [{ name: 'primary-service', type: 'Git Repository', status: 'Queued' }],
    };

    setProjects([newProj, ...projects]);
    setNewProjectName('');
    setNewProjectDesc('');
    setShowNewModal(false);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-foreground">
            Monitored Projects
          </h1>
          <p className="text-sm text-muted-foreground mt-0.5">
            Manage software projects, source repositories, and container artifacts scanned for cryptography
          </p>
        </div>
        <Button onClick={() => setShowNewModal(true)} className="gap-2 bg-primary hover:bg-primary/90 text-primary-foreground">
          <Plus className="h-4 w-4" />
          New Project
        </Button>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="p-4 border-border">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-primary/10 text-primary">
              <FolderKanban className="h-5 w-5" />
            </div>
            <div>
              <div className="text-xs font-medium text-muted-foreground">Total Projects</div>
              <div className="text-xl font-bold text-foreground">{projects.length}</div>
            </div>
          </div>
        </Card>
        <Card className="p-4 border-border">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-indigo-500/10 text-indigo-500">
              <Layers className="h-5 w-5" />
            </div>
            <div>
              <div className="text-xs font-medium text-muted-foreground">Total Artifacts Monitored</div>
              <div className="text-xl font-bold text-foreground">
                {projects.reduce((acc, p) => acc + p.artifactsCount, 0)}
              </div>
            </div>
          </div>
        </Card>
        <Card className="p-4 border-border">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-lg bg-destructive/10 text-destructive">
              <ShieldAlert className="h-5 w-5" />
            </div>
            <div>
              <div className="text-xs font-medium text-muted-foreground">Quantum High-Risk Assets</div>
              <div className="text-xl font-bold text-foreground">
                {projects.reduce((acc, p) => acc + p.criticalCount, 0)}
              </div>
            </div>
          </div>
        </Card>
      </div>

      {/* Search & Filter */}
      <div className="relative max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
        <Input
          placeholder="Filter projects by title or description..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-9"
        />
      </div>

      {/* Project Cards List */}
      <div className="grid grid-cols-1 gap-5">
        {filteredProjects.map((project) => (
          <Card key={project.id} className="border-border overflow-hidden">
            <div className="p-6">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-border">
                <div className="space-y-1">
                  <div className="flex items-center gap-2.5">
                    <h3 className="text-lg font-bold text-foreground">
                      {project.name}
                    </h3>
                    <Badge variant="outline" className="border-emerald-500/30 text-emerald-600 bg-emerald-500/10 text-xs">
                      {project.status}
                    </Badge>
                  </div>
                  <p className="text-sm text-muted-foreground max-w-3xl">
                    {project.description}
                  </p>
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <Link href={`/scans?project=${project.id}`}>
                    <Button size="sm" variant="outline" className="gap-1.5 text-xs">
                      <Play className="h-3.5 w-3.5 text-primary" />
                      Run Scan
                    </Button>
                  </Link>
                  <Link href="/cbom">
                    <Button size="sm" variant="outline" className="gap-1.5 text-xs">
                      <Database className="h-3.5 w-3.5" />
                      View CBOM
                    </Button>
                  </Link>
                  <Link href="/quantum-risk">
                    <Button size="sm" className="gap-1.5 text-xs bg-primary hover:bg-primary/90">
                      <ShieldAlert className="h-3.5 w-3.5" />
                      Risk Assessment
                    </Button>
                  </Link>
                </div>
              </div>

              {/* Artifacts Grid */}
              <div className="mt-4">
                <div className="text-xs font-semibold uppercase tracking-wider text-muted-foreground mb-3">
                  Registered Artifacts ({project.artifacts.length})
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5">
                  {project.artifacts.map((art, idx) => (
                    <div
                      key={idx}
                      className="p-2.5 rounded-lg border border-border bg-muted/30 flex items-center justify-between text-xs"
                    >
                      <div className="flex items-center gap-2 overflow-hidden">
                        <FileCode2 className="h-4 w-4 text-primary shrink-0" />
                        <span className="font-medium text-foreground truncate">{art.name}</span>
                      </div>
                      <span className="text-[11px] text-muted-foreground shrink-0">{art.type}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Footer Meta */}
              <div className="mt-4 pt-3 flex flex-wrap items-center justify-between gap-3 text-xs text-muted-foreground">
                <div className="flex items-center gap-4">
                  <span>Findings: <strong className="text-foreground">{project.findingsCount}</strong></span>
                  <span>Quantum Vulnerable: <strong className="text-destructive">{project.criticalCount}</strong></span>
                </div>
                <div className="flex items-center gap-1.5">
                  <Calendar className="h-3.5 w-3.5" />
                  <span>Last scanned: {project.lastScan}</span>
                </div>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {/* New Project Modal */}
      {showNewModal && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center p-4">
          <Card className="w-full max-w-lg border-border shadow-xl">
            <CardHeader>
              <CardTitle className="text-lg font-bold">Register New Monitored Project</CardTitle>
            </CardHeader>
            <form onSubmit={handleCreateProject}>
              <CardContent className="space-y-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold">Project Name</label>
                  <Input
                    placeholder="e.g. Core Banking Gateway"
                    value={newProjectName}
                    onChange={(e) => setNewProjectName(e.target.value)}
                    required
                  />
                </div>
                <div className="space-y-1.5">
                  <label className="text-xs font-semibold">Description</label>
                  <Input
                    placeholder="Brief description of application scope"
                    value={newProjectDesc}
                    onChange={(e) => setNewProjectDesc(e.target.value)}
                  />
                </div>
              </CardContent>
              <div className="p-6 pt-0 flex justify-end gap-2">
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={() => setShowNewModal(false)}
                >
                  Cancel
                </Button>
                <Button type="submit" size="sm" className="bg-primary hover:bg-primary/90 text-primary-foreground">
                  Create Project
                </Button>
              </div>
            </form>
          </Card>
        </div>
      )}
    </div>
  );
}