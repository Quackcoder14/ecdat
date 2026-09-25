'use client';

import { cn } from '@/lib/utils';
import { ChevronDown, ChevronUp } from 'lucide-react';
import { useState } from 'react';

interface Column<T> {
  key: string;
  header: string;
  render?: (row: T) => React.ReactNode;
  sortable?: boolean;
  className?: string;
}

interface DataTableProps<T> {
  columns: Column<T>[];
  data: T[];
  keyExtractor: (row: T) => string;
  onRowClick?: (row: T) => void;
  className?: string;
  emptyMessage?: string;
  sorting?: {
    column: string;
    direction: 'asc' | 'desc';
  };
  onSort?: (column: string) => void;
}

export function DataTable<T>({
  columns,
  data,
  keyExtractor,
  onRowClick,
  className,
  emptyMessage = 'No data available',
  sorting,
  onSort,
}: DataTableProps<T>) {
  return (
    <div className={cn('overflow-x-auto', className)}>
      {data.length === 0 ? (
        <div className="py-12 text-center text-muted-foreground">
          {emptyMessage}
        </div>
      ) : (
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b border-border">
              {columns.map((col) => (
                <th
                  key={col.key}
                  className={cn(
                    'px-3 py-2 text-left text-xs font-semibold text-muted-foreground uppercase tracking-wider',
                    col.sortable && 'cursor-pointer hover:text-primary select-none',
                    col.className
                  )}
                  onClick={() => col.sortable && onSort?.(col.key)}
                >
                  <div className="flex items-center gap-1">
                    {col.header}
                    {col.sortable && sorting?.column === col.key && (
                      sorting.direction === 'asc' ? (
                        <ChevronUp className="h-3 w-3" />
                      ) : (
                        <ChevronDown className="h-3 w-3" />
                      )
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {data.map((row) => (
              <tr
                key={keyExtractor(row)}
                className={cn(
                  'border-b border-border/50 transition-colors',
                  onRowClick && 'cursor-pointer hover:bg-muted/50'
                )}
                onClick={() => onRowClick?.(row)}
              >
                {columns.map((col) => (
                  <td key={col.key} className={cn('px-3 py-2 text-sm', col.className)}>
                    {col.render ? col.render(row) : (row as any)[col.key]}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}