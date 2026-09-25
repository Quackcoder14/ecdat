'use client';

const riskData = [
  { level: 'Critical', count: 12, color: '#7F1D1D', bgColor: '#FEF2F2', trackColor: '#FECACA' },
  { level: 'High', count: 177, color: '#B91C1C', bgColor: '#FEF2F2', trackColor: '#FECACA' },
  { level: 'Medium', count: 342, color: '#B45309', bgColor: '#FFFBEB', trackColor: '#FDE68A' },
  { level: 'Low', count: 523, color: '#166534', bgColor: '#F0FDF4', trackColor: '#BBF7D0' },
  { level: 'Informational', count: 193, color: '#0F766E', bgColor: '#ECFDF5', trackColor: '#99F6E4' },
];

export function RiskDistribution() {
  return (
    <div className="bg-card rounded-lg border border-border p-6">
      <h2 className="text-xl font-bold text-foreground mb-6">
        Risk Distribution
      </h2>
      
      <div className="space-y-4">
        {riskData.map((item) => (
          <div key={item.level} className="flex items-center gap-4">
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between text-sm mb-1">
                <span className="font-semibold text-foreground">{item.level}</span>
                <span className="font-mono text-foreground">{item.count}</span>
              </div>
              <div className="h-3 bg-muted/60 rounded-full overflow-hidden">
                <div 
                  className="h-full rounded-full transition-all duration-500"
                  style={{ 
                    width: `${(item.count / 1248) * 100}%`,
                    backgroundColor: item.color,
                  }}
                />
              </div>
            </div>
          </div>
        ))}
        
        <div className="mt-6 p-4 bg-muted/50 rounded-lg">
          <h3 className="text-sm font-semibold text-foreground mb-2">
            Why these assets are exposed
          </h3>
          <ul className="text-sm text-muted-foreground space-y-1">
            <li>• 189 assets use quantum-vulnerable asymmetric algorithms (RSA, ECDSA, ECDH)</li>
            <li>• 67 assets protect sensitive data with long retention periods (more than 10 years)</li>
            <li>• 45 assets belong to critical payment/identity systems</li>
            <li>• 23 assets have migration lead time exceeding threat horizon</li>
          </ul>
        </div>
      </div>
    </div>
  );
}