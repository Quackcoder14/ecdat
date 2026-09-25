'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { cn } from '@/lib/utils';

interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: Source[];
}

interface Source {
  title: string;
  content: string;
  findingId?: string;
}

const mockResponses: Record<string, string> = {
  'rsa': 'RSA-2048 is flagged because the asset is used for digital signatures and belongs to an asymmetric cryptographic family affected by quantum algorithms (Shor\'s algorithm). The associated payment service also has a long data-security lifetime, increasing migration urgency.',
  'quantum': 'Quantum-vulnerable assets in this project: RSA-2048 (digital signatures, key transport), ECDSA P-256 (signatures, authentication), ECDH P-256 (key establishment). These are all vulnerable to Shor\'s algorithm which can break asymmetric cryptography on a sufficiently large quantum computer.',
  'migration': 'For RSA-2048 digital signatures, the recommended migration path is ML-DSA-65 (Dilithium) with a hybrid option of RSA-2048 + ML-DSA-65. For ECDH P-256 key establishment, ML-KEM-768 (Kyber) is recommended with hybrid ECDH + ML-KEM. Migration complexity is Medium for signatures, High for key establishment.',
  'default': 'Based on the ECDAT findings, I can explain the risk assessments and migration recommendations. The deterministic engines have classified assets based on algorithm type, key parameters, usage context, and business criticality. What specific finding would you like me to elaborate on?',
};

function getMockResponse(question: string, context: string): { answer: string; sources: Source[] } {
  const q = question.toLowerCase();
  
  if (q.includes('rsa') || q.includes('2048')) {
    return {
      answer: mockResponses.rsa,
      sources: [
        { title: 'Finding: RSA-2048 Digital Signature', content: 'Algorithm: RSA, Key Size: 2048, Purpose: digital_signature, Risk: HIGH', findingId: 'finding-001' },
        { title: 'Risk Assessment: RSA-2048', content: 'Risk Level: HIGH, Reasons: Quantum-vulnerable asymmetric algorithm, Critical application, Long data lifetime', findingId: 'finding-001' },
      ],
    };
  }
  
  if (q.includes('quantum') || q.includes('vulnerab')) {
    return {
      answer: mockResponses.quantum,
      sources: [
        { title: 'Quantum Risk Summary', content: '423 quantum-vulnerable assets across 3 algorithm families', findingId: 'summary' },
      ],
    };
  }
  
  if (q.includes('migrat') || q.includes('hybrid') || q.includes('pqc')) {
    return {
      answer: mockResponses.migration,
      sources: [
        { title: 'Migration Recommendation: RSA-2048', content: 'Candidate: ML-DSA-65, Hybrid: RSA-2048 + ML-DSA-65, Complexity: Medium', findingId: 'rec-001' },
        { title: 'Migration Recommendation: ECDH P-256', content: 'Candidate: ML-KEM-768, Hybrid: ECDH + ML-KEM-768, Complexity: High', findingId: 'rec-002' },
      ],
    };
  }
  
  return {
    answer: mockResponses.default,
    sources: [
      { title: 'Project: Acme Payments Platform', content: '4 high-risk findings, 12 medium-risk, 23 low-risk', findingId: 'project-summary' },
    ],
  };
}

export function AIAssistant() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Welcome to the ECDAT AI Assistant. I can explain findings, risk assessments, and migration recommendations based on the deterministic analysis. What would you like to know?',
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [context, setContext] = useState<'project' | 'scan' | 'finding' | 'cbom'>('project');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = { role: 'user', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 800));
    
    const { answer, sources } = getMockResponse(input, context);
    
    setMessages((prev) => [...prev, { role: 'assistant', content: answer, sources }]);
    setIsLoading(false);
  };

  return (
    <div className="flex h-[calc(100vh-200px)] flex-col">
      <div className="flex gap-4 p-4 border-b border-border">
        <h3 className="text-lg font-semibold text-foreground">AI Assistant</h3>
        <div className="flex-1" />
        <select
          value={context}
          onChange={(e) => setContext(e.target.value as typeof context)}
          className="px-3 py-1 text-sm border border-border rounded-md bg-background"
        >
          <option value="project">Current Project</option>
          <option value="scan">Current Scan</option>
          <option value="finding">Selected Finding</option>
          <option value="cbom">Entire CBOM</option>
        </select>
      </div>

      <ScrollArea className="flex-1 p-4 space-y-4">
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className={cn('flex gap-3', msg.role === 'user' && 'flex-row-reverse')}
          >
            <div
              className={cn(
                'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-sm',
                msg.role === 'user'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted text-muted-foreground'
              )}
            >
              {msg.role === 'user' ? 'U' : 'AI'}
            </div>
            <div
              className={cn(
                'max-w-[80%] p-3 rounded-lg',
                msg.role === 'user'
                  ? 'bg-primary text-primary-foreground rounded-br-none'
                  : 'bg-muted rounded-bl-none'
              )}
            >
              <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
              {msg.sources && msg.sources.length > 0 && (
                <details className="mt-2">
                  <summary className="text-xs text-muted-foreground cursor-pointer">
                    Sources ({msg.sources.length})
                  </summary>
                  <ul className="mt-1 text-xs text-muted-foreground space-y-1">
                    {msg.sources.map((src, i) => (
                      <li key={i} className="flex gap-2">
                        <span className="font-mono text-[10px] text-primary">{src.findingId || 'N/A'}</span>
                        <span>{src.title}</span>
                      </li>
                    ))}
                  </ul>
                </details>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-muted flex items-center justify-center text-sm text-muted-foreground">AI</div>
            <div className="p-3 bg-muted rounded-lg rounded-bl-none max-w-[80%]">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <span className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '100ms' }} />
                <span className="w-2 h-2 bg-primary/50 rounded-full animate-bounce" style={{ animationDelay: '200ms' }} />
              </div>
            </div>
          </div>
        )}
      </ScrollArea>

      <div className="p-4 border-t border-border">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Ask about findings, risk, or migration..."
            className="flex-1"
            disabled={isLoading}
          />
          <Button type="submit" disabled={isLoading || !input.trim()}>
            Send
          </Button>
        </form>
        <p className="mt-2 text-xs text-muted-foreground text-center">
          AI responses explain ECDAT findings; risk classification and migration mapping are generated by deterministic engines.
        </p>
      </div>
    </div>
  );
}