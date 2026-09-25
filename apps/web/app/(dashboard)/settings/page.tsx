'use client';

import { ShieldCheck, AlertTriangle, Search, Cpu, HardDrive, Database, Server, Wifi, Settings, Key, Bot, Sparkles, Bell, Shield, User, ChevronRight } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { useState } from 'react';

const scannerStatus = [
  { name: 'Semgrep', status: 'Available', version: '1.85.0', icon: Search },
  { name: 'Syft', status: 'Available', version: '0.86.0', icon: Database },
  { name: 'Trivy', status: 'Available', version: '0.48.3', icon: Shield },
  { name: 'OpenSSL', status: 'Available', version: '3.0.12', icon: Key },
];

const llmProviders = [
  { id: 'mock', name: 'Mock (Demo)', description: 'Built-in deterministic responses for demo' },
  { id: 'openai_compatible', name: 'OpenAI Compatible', description: 'Any OpenAI-compatible API endpoint' },
  { id: 'ollama', name: 'Ollama', description: 'Local LLM via Ollama' },
];

export default function SettingsPage() {
  const [activeProvider, setActiveProvider] = useState('mock');
  const [apiKey, setApiKey] = useState('');
  const [baseUrl, setBaseUrl] = useState('https://api.openai.com/v1');
  const [model, setModel] = useState('gpt-4-turbo-preview');

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-foreground">Settings</h1>
        <p className="text-muted-foreground">Manage ECDAT configuration</p>
      </div>

      <Tabs defaultValue="general" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="scanners">Scanners</TabsTrigger>
          <TabsTrigger value="llm">LLM Provider</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Application Settings</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <Label>Demo Mode</Label>
                  <p className="text-sm text-muted-foreground">Use built-in demo data for all scans</p>
                </div>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label>Auto-refresh Dashboard</Label>
                  <p className="text-sm text-muted-foreground">Automatically refresh dashboard data</p>
                </div>
                <Switch defaultChecked />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label>Scan Timeout</Label>
                  <p className="text-sm text-muted-foreground">Maximum time for scan operations (seconds)</p>
                </div>
                <Input type="number" defaultValue="300" className="w-24" />
              </div>
              <div className="flex items-center justify-between">
                <div>
                  <Label>Max Artifact Size</Label>
                  <p className="text-sm text-muted-foreground">Maximum upload size in MB</p>
                </div>
                <Input type="number" defaultValue="100" className="w-24" />
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Artifact Storage</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label>Storage Path</Label>
                <Input defaultValue="/app/artifacts" className="font-mono text-sm" />
                <p className="text-sm text-muted-foreground mt-1">Local filesystem path for artifact storage</p>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="scanners" className="space-y-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>Scanner Capabilities</CardTitle>
              <div className="flex items-center gap-2 text-sm text-green-600">
                <ShieldCheck className="h-4 w-4" />
                All scanners available
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {scannerStatus.map((scanner) => (
                  <div key={scanner.name} className="flex items-center justify-between p-4 bg-muted/50 rounded-lg">
                    <div className="flex items-center gap-3">
                      <scanner.icon className="h-5 w-5 text-primary" />
                      <div>
                        <p className="font-medium text-foreground">{scanner.name}</p>
                        <p className="text-sm text-muted-foreground">Version {scanner.version}</p>
                      </div>
                    </div>
                    <Badge variant="outline" className="bg-green-100 text-green-700">
                      {scanner.status}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>External Scanner Binaries</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-sm text-muted-foreground">
              <p>ECDAT uses external scanner binaries for production scans. Ensure these are installed in your PATH:</p>
              <ul className="list-disc list-inside space-y-1 ml-4">
                <li><code>semgrep</code> - Source code analysis</li>
                <li><code>syft</code> - Dependency/SBOM analysis</li>
                <li><code>trivy</code> - Container/image scanning</li>
                <li><code>openssl</code> - Certificate analysis</li>
              </ul>
              <p className="mt-2">In demo mode, built-in mock scanners are used instead.</p>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="llm" className="space-y-6">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <CardTitle>LLM Provider Configuration</CardTitle>
              <Badge variant="outline" className={activeProvider === 'mock' ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-700'}>
                {activeProvider === 'mock' ? 'Active' : 'Inactive'}
              </Badge>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <Label>Provider</Label>
                <Select value={activeProvider} onValueChange={setActiveProvider}>
                  <SelectTrigger className="w-[300px]">
                    <SelectValue placeholder="Select provider" />
                  </SelectTrigger>
                  <SelectContent>
                    {llmProviders.map(p => (
                      <SelectItem key={p.id} value={p.id}>
                        {p.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                <p className="text-sm text-muted-foreground">
                  {llmProviders.find(p => p.id === activeProvider)?.description}
                </p>
              </div>

              {activeProvider !== 'mock' && (
                <div className="space-y-3 border-t border-border pt-4">
                  <div className="space-y-3">
                    <div className="space-y-2">
                      <Label>API Base URL</Label>
                      <Input
                        value={baseUrl}
                        onChange={(e) => setBaseUrl(e.target.value)}
                        placeholder="https://api.openai.com/v1"
                      />
                    </div>
                    <div className="space-y-2">
                      <Label>API Key</Label>
                      <Input
                        type="password"
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                        placeholder="sk-..."
                      />
                      <p className="text-sm text-muted-foreground">Key is masked and never logged</p>
                    </div>
                    <div className="space-y-2">
                      <Label>Model</Label>
                      <Select value={model} onValueChange={setModel}>
                        <SelectTrigger className="w-[300px]">
                          <SelectValue placeholder="Select model" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="gpt-4-turbo-preview">GPT-4 Turbo Preview</SelectItem>
                          <SelectItem value="gpt-4">GPT-4</SelectItem>
                          <SelectItem value="gpt-3.5-turbo">GPT-3.5 Turbo</SelectItem>
                          <SelectItem value="claude-3-opus">Claude 3 Opus</SelectItem>
                          <SelectItem value="claude-3-sonnet">Claude 3 Sonnet</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <Button variant="outline" onClick={() => alert('Connection test would run here')}>
                      Test Connection
                    </Button>
                    <Button>Save Configuration</Button>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="security" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Audit & Security</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Audit Logging</Label>
                    <p className="text-sm text-muted-foreground">Log all user actions and system events</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Secret Redaction</Label>
                    <p className="text-sm text-muted-foreground">Automatically redact secrets from AI context</p>
                  </div>
                  <Switch defaultChecked />
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <Label>Session Timeout</Label>
                    <p className="text-sm text-muted-foreground">Minutes of inactivity before logout</p>
                  </div>
                  <Input type="number" defaultValue="60" className="w-24" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>API Security</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="space-y-2">
                  <Label>JWT Secret</Label>
                  <Input type="password" value="••••••••••••••••" disabled />
                  <p className="text-sm text-muted-foreground">Regenerate secret to invalidate all sessions</p>
                </div>
                <Button variant="destructive" onClick={() => alert('Would regenerate JWT secret')}>
                  Regenerate Secret
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}