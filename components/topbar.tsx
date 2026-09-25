'use client';

import Link from 'next/link';
import { Bell, Search as SearchIcon, ChevronDown } from 'lucide-react';
import { useDataMode } from '@/app/providers/DataModeProvider';

export function Topbar() {
  const { mode, setMode } = useDataMode();

  const modeLabels: Record<string, { label: string; description: string }> = {
    simulation: { label: 'SIMULATION', description: 'Seeded data' },
    demo: { label: 'DEMO', description: 'Live data' },
  };

  const modeTooltips: Record<string, string> = {
    simulation: 'Explore ECDAT using deterministic seeded demonstration data.',
    demo: 'Analyze only repositories and artefacts supplied to ECDAT. No seeded findings are used.',
  };

  return (
    <header className="bg-card border-b border-border px-6 py-4 flex items-center justify-between">
      <div className="flex items-center space-x-4">
        <Link href="/" className="flex items-center space-x-2">
          <span className="text-xl font-bold text-primary-foreground">
            ECDAT
          </span>
        </Link>
        
        <div className="hidden md:flex items-center space-x-4">
          <div className="relative">
            <input
              type="text"
              placeholder="Search or execute command..."
              className="pl-8 pr-4 py-2 bg-muted/50 border border-border rounded-md w-64 focus:outline-none focus:ring-2 focus:ring-primary text-sm"
              onKeyDown={(e) => {
                if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
                  alert('Command palette would open here (Cmd/Ctrl+Enter)');
                }
              }}
            />
          </div>
          
          <div className="relative">
            <Bell className="h-5 w-5 text-muted-foreground" />
            <span className="absolute -top-1 -right-1 bg-destructive text-xs text-primary-foreground flex h-3 w-3 items-center justify-center rounded-full">
              3
            </span>
          </div>
        </div>
      </div>
      
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-3">
          <span className="text-sm font-medium text-primary-foreground">
            {modeLabels[mode].label}
          </span>
          <span className="text-xs text-muted-foreground px-2 py-0.5 rounded bg-muted">
            {modeLabels[mode].description}
          </span>
          <button
            onClick={() => setMode(mode === 'simulation' ? 'demo' : 'simulation')}
            title={modeTooltips[mode]}
            className="flex items-center gap-1 px-3 py-1.5 text-sm font-medium text-primary-foreground bg-muted rounded-lg border border-border hover:bg-primary/10 transition-colors"
          >
            <span className="flex items-center gap-1">
              {mode === 'simulation' ? '⚙' : '🔴'}
              <ChevronDown className="h-4 w-4" />
            </span>
          </button>
        </div>

        <div className="relative">
          <Bell className="h-5 w-5 text-muted-foreground" />
          <span className="absolute -top-1 -right-1 bg-destructive text-xs text-primary-foreground flex h-3 w-3 items-center justify-center rounded-full">
            3
          </span>
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="relative">
            <img
              src="/placeholder-user.jpg"
              alt="User avatar"
              className="h-8 w-8 rounded-full border border-border"
            />
            <span className="absolute -top-1 -right-0 bg-success text-xs text-primary-foreground flex h-3 w-3 items-center justify-center rounded-full">
              ●
            </span>
          </div>
          <div className="space-x-2 text-sm">
            <span className="font-medium text-primary-foreground">Demo User</span>
            <span className="text-muted-foreground">Admin</span>
          </div>
        </div>
      </div>
    </header>
  );
}