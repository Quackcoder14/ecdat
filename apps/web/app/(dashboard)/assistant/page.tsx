'use client';

import { AIAssistant } from '@/components/ai-assistant';

export default function AssistantPage() {
  return (
    <div className="space-y-6">
      <div className="space-y-1">
        <h1 className="text-2xl font-bold tracking-tight text-foreground">
          AI Cryptographic Assistant
        </h1>
        <p className="text-sm text-muted-foreground">
          Explain cryptographic findings, Mosca-style quantum risk calculations, and post-quantum migration paths with strict context sanitization.
        </p>
      </div>

      <AIAssistant />
    </div>
  );
}
