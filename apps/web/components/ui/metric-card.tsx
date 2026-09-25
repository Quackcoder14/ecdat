'use client';

import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface MetricCardProps {
  title: string;
  value: string;
  subtitle?: string;
  icon: string;
  variant?: 'default' | 'destructive' | 'warning' | 'success';
  trend?: {
    value: number;
    positive: boolean;
  };
  children?: ReactNode;
}

const iconMap: Record<string, React.ComponentType<{ className?: string }>> = {
  KeyRound: () => <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="2" width="20" height="20" rx="2"/><path d="M6 10V5a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2v-5"/></svg>,
  ShieldAlert: () => <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="M12 8v4"/><path d="M12 16h.01"/></svg>,
  AlertTriangle: () => <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" x2="12" y1="9" y2="13"/><line x1="12" x2="12.01" y1="17" y2="17"/></svg>,
  ArrowUpRight: () => <svg className="h-5 w-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M7 17L17 7"/><path d="M7 7h10v10"/></svg>,
};

export function MetricCard({ 
  title, 
  value, 
  subtitle, 
  icon, 
  variant = 'default',
  trend,
  children 
}: MetricCardProps) {
  const Icon = iconMap[icon] || iconMap.KeyRound;

  const variantClasses = {
    default: 'bg-card border-border',
    destructive: 'bg-card border-border',
    warning: 'bg-card border-border',
    success: 'bg-card border-border',
  };

  const iconClasses = {
    default: 'text-primary',
    destructive: 'text-destructive',
    warning: 'text-amber-600',
    success: 'text-green-700',
  };

  return (
    <div className={cn('rounded-lg border p-6', variantClasses[variant])}>
      <div className="flex items-start justify-between">
        <div className="space-y-1">
          <p className="text-sm font-medium text-foreground/70">{title}</p>
          <p className="text-3xl font-bold text-foreground">{value}</p>
          {subtitle && <p className="text-sm text-foreground/60">{subtitle}</p>}
        </div>
        <div className={cn('p-2 rounded-lg', `bg-${variant === 'default' ? 'primary' : variant}/10`)}>
          <Icon className={cn('h-5 w-5', iconClasses[variant]?.replace?.('500', '600') || 'text-primary')} />
        </div>
      </div>
      
      {trend && (
        <div className="mt-4 flex items-center gap-1 text-sm">
          <span className={cn(trend.positive ? 'text-green-700' : 'text-red-700')}>
            {trend.positive ? '↑' : '↓'} {Math.abs(trend.value)}%
          </span>
          <span className="text-foreground/60">vs last period</span>
        </div>
      )}
      
      {children}
    </div>
  );
}

const iconClasses = {
  default: 'text-primary',
  destructive: 'text-destructive',
  warning: 'text-amber-600',
  success: 'text-green-700',
};