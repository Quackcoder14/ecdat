import Link from '../styles/globals.css';
import Link from 'next/link';
import {
  Dashboard,
  Users,
  Search,
  Database,
  ShieldCheck,
  ShieldAlert,
  Bot,
  FileText,
  BarChart3,
  Settings,
  LogOut,
} from 'lucide-react';

export function Sidebar() {
  return (
    <aside className="w-64 bg-card border-r border-border">
      <nav className="p-4 space-y-2">
        <Link href="/" className="flex items-center space-x-3 rounded-md p-2 text-sm font-medium hover:bg-primary/10 hover:text-primary">
          <Dashboard className="h-4 w-4" />
          <span className="whitespace-nowrap">Overview</span>
        </Link>
        
        <Link href="/projects" className="flex items-center space-x-3 rounded-md p-2 text-sm font-medium hover:bg-primary/10 hover:text-primary">
          <Users className="h-4 w-4" />
          <span className="whitespace-nowrap">Projects</span>
        </Link>
        
        <Link href="/scans" className="flex items-center space-x-3 rounded-md p-2 text-sm font-medium hover:bg-primary/10 hover:text-primary">
          <Search className="h-4 w-4" />
          <span className="whitespace-nowrap">Scans</span>
        </Link>
        
        <Link href="/cbom" className="flex items-center space-x-3 rounded-md p-2 text-sm font-medium hover:bg-primary/10 hover:text-primary">
          <Database className="h-4 w-4" />
          <span className="whitespace-nowrap">CBOM Explorer</span>
        </Link>
        
        <Link href="/quantum-risk" className="flex items-center space-x-3 rounded-md p-2 text-sm font-medium hover:bg-primary/10 hover:text-primary">
          <ShieldCheck className="h-4 w-4" />
          <span className="whitespace-nowrap">Quantum Risk</span>
        </Link>
        
        <Link href="/pqc-migration" className="flex items-center space-x-3 rounded-md p-2 text-sm font-medium hover:bg-primary/10 hover:text-primary">
          <ShieldAlert className="h-4 w-4" />
          <span className="whitespace-nowrap">PQC Migration</span>
        </Link>
        
        <Link href="/assistant" className="flex items-center space-x-3 rounded-md p-2 text-sm font-medium hover:bg-primary/10 hover:text-primary">
          <Bot className="h-4 w-4" />
          <span className="whitespace-nowrap">AI Assistant</span>
        </Link>
        
        <Link href="/reports" className="flex items-center space-x-3 rounded-md p-2 text-sm font-medium hover:bg-primary/10 hover:text-primary">
          <FileText className="h-4 w-4" />
          <span className="whitespace-nowrap">Reports</span>
        </Link>
        
        <Link href="/settings" className="flex items-center space-x-3 rounded-md p-2 text-sm font-medium hover:bg-primary/10 hover:text-primary">
          <Settings className="h-4 w-4" />
          <span className="whitespace-nowrap">Settings</span>
        </Link>
      </nav>
      
      <div className="mt-auto p-4 border-t border-border">
        <div className="flex items-center space-x-3 text-sm">
          <div className="h-8 w-8 bg-primary/20 rounded-full flex items-center justify-center">
            <LogOut className="h-4 w-4 text-primary" />
          </div>
          <div className="space-y-1">
            <p className="font-medium text-primary-foreground">Demo User</p>
            <p className="text-muted-foreground">admin@example.com</p>
          </div>
        </div>
      </div>
    </aside>
  );
}