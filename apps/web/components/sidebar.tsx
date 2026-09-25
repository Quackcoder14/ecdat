'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  FolderKanban,
  Radar,
  Database,
  ShieldAlert,
  ArrowRightLeft,
  Bot,
  FileText,
  Settings,
  LogOut,
  ShieldCheck,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navItems = [
  { href: '/', label: 'Dashboard', icon: LayoutDashboard },
  { href: '/projects', label: 'Projects', icon: FolderKanban },
  { href: '/scans', label: 'Scans', icon: Radar },
  { href: '/cbom', label: 'CBOM Explorer', icon: Database },
  { href: '/quantum-risk', label: 'Quantum Risk', icon: ShieldAlert },
  { href: '/pqc-migration', label: 'PQC Migration', icon: ArrowRightLeft },
  { href: '/assistant', label: 'AI Assistant', icon: Bot },
  { href: '/reports', label: 'Reports', icon: FileText },
  { href: '/settings', label: 'Settings', icon: Settings },
];

export function Sidebar({ className }: { className?: string }) {
  const pathname = usePathname();

  const handleLogout = () => {
    // Clear cookies and redirect to login
    document.cookie = 'auth_token=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT;';
    window.location.href = '/login';
  };

  return (
    <aside className={cn('w-64 bg-card border-r border-border flex flex-col justify-between shrink-0 h-screen sticky top-0', className)}>
      <div>
        <div className="p-4 border-b border-border flex items-center gap-3">
          <div className="h-9 w-9 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center text-primary font-bold">
            <ShieldCheck className="h-5 w-5 text-primary" />
          </div>
          <div>
            <div className="font-bold text-sm tracking-wide text-foreground">ECDAT PLATFORM</div>
            <div className="text-[11px] text-muted-foreground">Quantum Discovery</div>
          </div>
        </div>

        <nav className="p-3 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href));
            return (
              <Link
                key={item.href}
                href={item.href}
                className={cn(
                  'flex items-center space-x-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors',
                  isActive
                    ? 'bg-primary text-primary-foreground shadow-sm'
                    : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                )}
              >
                <Icon className="h-4 w-4 shrink-0" />
                <span className="truncate">{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="p-3 border-t border-border">
        <div className="flex items-center justify-between p-2 rounded-lg bg-muted/40">
          <div className="flex items-center space-x-2.5 overflow-hidden">
            <div className="h-8 w-8 rounded-full bg-primary/20 flex items-center justify-center font-semibold text-xs text-primary shrink-0">
              DA
            </div>
            <div className="truncate text-xs">
              <p className="font-medium text-foreground truncate">Demo Admin</p>
              <p className="text-muted-foreground truncate">admin@ecdat.demo</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            title="Sign out"
            className="p-1.5 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-md transition-colors"
          >
            <LogOut className="h-4 w-4" />
          </button>
        </div>
      </div>
    </aside>
  );
}
