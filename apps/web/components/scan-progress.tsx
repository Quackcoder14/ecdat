'use client';

import { cn } from '@/lib/utils';

interface ScanProgressProps {
  scanId: string;
  project: string;
  source: string;
  started: string;
  currentStage: string;
  progressPercentage: number;
  stages?: Stage[];
}

interface Stage {
  id: string;
  name: string;
  status: 'completed' | 'current' | 'pending';
}

const STAGE_ORDER = [
  'QUEUED',
  'PREPARING',
  'SCANNING_SOURCE',
  'SCANNING_DEPENDENCIES',
  'SCANNING_CONTAINERS',
  'SCANNING_CERTIFICATES',
  'SCANNING_BINARIES',
  'CORRELATING',
  'GENERATING_CBOM',
  'ASSESSING_RISK',
  'GENERATING_RECOMMENDATIONS',
  'COMPLETED',
  'FAILED',
];

const STAGE_LABELS: Record<string, string> = {
  'QUEUED': 'Queued',
  'PREPARING': 'Preparing',
  'SCANNING_SOURCE': 'Source Analysis',
  'SCANNING_DEPENDENCIES': 'Dependency Analysis',
  'SCANNING_CONTAINERS': 'Container Analysis',
  'SCANNING_CERTIFICATES': 'Certificate Analysis',
  'SCANNING_BINARIES': 'Binary Analysis',
  'CORRELATING': 'Correlation',
  'GENERATING_CBOM': 'CBOM Generation',
  'ASSESSING_RISK': 'Risk Assessment',
  'GENERATING_RECOMMENDATIONS': 'Recommendations',
  'COMPLETED': 'Completed',
  'FAILED': 'Failed',
};

export function ScanProgress({ 
  scanId, 
  project, 
  source, 
  started, 
  currentStage, 
  progressPercentage,
  stages = [],
}: ScanProgressProps) {
  const stageList = stages.length > 0 
    ? stages 
    : STAGE_ORDER.map((id) => ({
        id,
        name: STAGE_LABELS[id] || id,
        status: (
          STAGE_ORDER.indexOf(id) < STAGE_ORDER.indexOf(currentStage) ? 'completed' :
          id === currentStage ? 'current' : 'pending'
        ) as 'completed' | 'current' | 'pending',
      }));

  return (
    <div className="bg-card rounded-lg border border-border p-6 space-y-6">
      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        <div>
          <p className="text-sm text-muted-foreground">Scan ID</p>
          <p className="font-mono text-sm text-foreground">{scanId}</p>
        </div>
        <div>
          <p className="text-sm text-muted-foreground">Project</p>
          <p className="font-medium text-foreground">{project}</p>
        </div>
        <div>
          <p className="text-sm text-muted-foreground">Source</p>
          <p className="font-mono text-sm text-muted-foreground">{source}</p>
        </div>
        <div>
          <p className="text-sm text-muted-foreground">Started</p>
          <p className="font-mono text-sm text-muted-foreground">{new Date(started).toLocaleString()}</p>
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-foreground">Progress</span>
          <span className="text-sm font-mono text-foreground">{progressPercentage}%</span>
        </div>
        <div className="h-2 bg-muted rounded-full overflow-hidden">
          <div 
            className="h-full bg-primary rounded-full transition-all duration-300"
            style={{ width: `${progressPercentage}%` }}
          />
        </div>
      </div>

      <div className="border-t border-border pt-6">
        <h3 className="text-sm font-semibold text-foreground mb-4">Activity Timeline</h3>
        <div className="space-y-3">
          {stageList.map((stage, idx) => (
            <div key={stage.id} className="flex items-start gap-3">
              <div className={cn(
                'flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium mt-1',
                stage.status === 'completed' && 'bg-green-500 text-white',
                stage.status === 'current' && 'bg-primary text-white animate-pulse',
                stage.status === 'pending' && 'bg-muted text-muted-foreground'
              )}>
                {stage.status === 'completed' && '✓'}
                {stage.status === 'current' && '→'}
                {stage.status === 'pending' && '○'}
              </div>
              <div className="flex-1 min-w-0">
                <p className={cn(
                  'text-sm',
                  stage.status === 'completed' && 'text-muted-foreground',
                  stage.status === 'current' && 'text-foreground font-medium',
                  stage.status === 'pending' && 'text-muted-foreground'
                )}>
                  {stage.name}
                </p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}