'use client';

import { BarChart, Bar, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const data = [
  { name: 'Asymmetric', value: 423, color: '#2563EB' },
  { name: 'Symmetric', value: 289, color: '#0F766E' },
  { name: 'Hash', value: 156, color: '#64748B' },
  { name: 'Certificates', value: 187, color: '#B45309' },
  { name: 'Protocols', value: 112, color: '#7C3AED' },
  { name: 'Libraries', value: 80, color: '#B91C1C' },
];

export function InventoryChart() {
  return (
    <div className="bg-card rounded-lg border border-border p-6 flex flex-col justify-between">
      <h2 className="text-xl font-bold text-foreground mb-4">
        Cryptographic Asset Inventory
      </h2>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={data} layout="vertical">
          <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
          <XAxis type="number" tickLine={false} axisLine={false} tick={{ fontSize: 12, fill: '#64748B' }} />
          <YAxis 
            type="category" 
            dataKey="name" 
            tickLine={false} 
            axisLine={false} 
            tick={{ fontSize: 12, fill: '#64748B' }}
            width={100}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: '#FFFFFF', 
              border: '1px solid #E2E8F0',
              borderRadius: '8px',
              boxShadow: '0 1px 3px rgba(0,0,0,0.1)'
            }}
          />
          <Bar 
            dataKey="value" 
            radius={[0, 4, 4, 0]}
            maxBarSize={32}
          >
            {data.map((entry) => (
              <Cell key={entry.name} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
      </div>
    </div>
  );
}