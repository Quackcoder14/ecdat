'use client';

import { Bell, Search, Cpu, FlaskConical, Database } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { useDataMode } from '@/app/providers/DataModeProvider';
import { cn } from '@/lib/utils';

export function Topbar() {
  const { mode, setMode } = useDataMode();

  return (
    <header className="bg-card border-b border-border px-6 py-3 flex items-center justify-between sticky top-0 z-30">
      <div className="flex items-center space-x-4 flex-1 max-w-xl">
        <div className="relative w-full max-w-md">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input
            type="text"
            placeholder="Search algorithms, CBOM assets, projects..."
            className="w-full pl-9 pr-4 py-1.5 bg-muted/50 border border-border rounded-lg focus:outline-none focus:ring-2 focus:ring-primary text-sm placeholder:text-muted-foreground"
          />
        </div>
      </div>

      <div className="flex items-center space-x-3">
        {/* Data Mode Toggle */}
        <div
          role="group"
          aria-label="Data engine mode"
          className="flex items-center rounded-lg border border-border bg-muted/40 p-0.5 gap-0.5"
        >
          <button
            id="mode-simulation"
            onClick={() => setMode('simulation')}
            title="Simulation engine – data generated from seeded demo DB"
            className={cn(
              'flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-semibold transition-colors',
              mode === 'simulation'
                ? 'bg-primary text-primary-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground hover:bg-muted'
            )}
          >
            <FlaskConical className="h-3.5 w-3.5" />
            Simulation
          </button>
          <button
            id="mode-demo"
            onClick={() => setMode('demo')}
            title="Demo engine – live backend data"
            className={cn(
              'flex items-center gap-1.5 px-3 py-1 rounded-md text-xs font-semibold transition-colors',
              mode === 'demo'
                ? 'bg-primary text-primary-foreground shadow-sm'
                : 'text-muted-foreground hover:text-foreground hover:bg-muted'
            )}
          >
            <Database className="h-3.5 w-3.5" />
            Demo
          </button>
        </div>

        <Badge variant="outline" className="hidden md:inline-flex items-center gap-1.5 px-2.5 py-1 text-xs border-emerald-500/30 text-emerald-600 dark:text-emerald-400 bg-emerald-500/5">
          <Cpu className="h-3.5 w-3.5" />
          <span>PQC Ready: FIPS 203/204</span>
        </Badge>

        <button className="relative p-2 text-muted-foreground hover:text-foreground hover:bg-muted rounded-lg transition-colors">
          <Bell className="h-4 w-4" />
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-destructive" />
        </button>

        <div className="h-4 w-px bg-border mx-1" />

        <div className="flex items-center space-x-2.5 pl-1">
          <div className="h-8 w-8 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center font-bold text-xs text-primary">
            DA
          </div>
          <div className="hidden sm:block text-left text-xs">
            <p className="font-semibold text-foreground leading-none">Demo Admin</p>
            <p className="text-muted-foreground text-[10px] mt-0.5">admin@ecdat.demo</p>
          </div>
        </div>
      </div>
    </header>
  );
}
