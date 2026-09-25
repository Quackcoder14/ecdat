'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ShieldCheck, Lock, Mail, ArrowRight, ShieldAlert, KeyRound, Sparkles } from 'lucide-react';

export default function LoginPage() {
  const [email, setEmail] = useState('admin@ecdat.demo');
  const [password, setPassword] = useState('demo123');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Invalid email or password');
      }

      const data = await response.json().catch(() => ({}));
      if (data?.access_token) {
        localStorage.setItem('auth_token', data.access_token);
      }
      if (data?.user) {
        localStorage.setItem('user', JSON.stringify(data.user));
      }

      // Redirect to dashboard on successful login
      window.location.href = '/';
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setIsLoading(false);
    }
  };

  const fillDemoCredentials = () => {
    setEmail('admin@ecdat.demo');
    setPassword('demo123');
  };

  return (
    <div className="min-h-screen flex bg-background text-foreground">
      {/* Brand Hero Column */}
      <div className="flex-1 bg-gradient-to-br from-slate-900 via-slate-800 to-indigo-950 hidden lg:flex flex-col justify-between p-12 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,_var(--tw-gradient-stops))] from-indigo-500/20 via-transparent to-transparent pointer-events-none" />
        
        <div className="relative z-10 flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-white/10 backdrop-blur-md border border-white/20 flex items-center justify-center text-primary-foreground">
            <ShieldCheck className="h-6 w-6 text-indigo-400" />
          </div>
          <div>
            <span className="text-xl font-bold tracking-tight">ECDAT</span>
            <span className="text-xs ml-2 px-2 py-0.5 rounded-full bg-indigo-500/20 text-indigo-300 border border-indigo-400/30">
              v1.0 Quantum Ready
            </span>
          </div>
        </div>

        <div className="relative z-10 max-w-lg space-y-6">
          <h1 className="text-4xl font-extrabold tracking-tight leading-tight">
            Cryptographic Discovery & Quantum Readiness Platform
          </h1>
          <p className="text-base text-slate-300 leading-relaxed">
            Automate continuous cryptographic asset inventory, Mosca theorem quantum vulnerability assessments, and NIST-aligned PQC migration planning for enterprise estates.
          </p>

          <div className="grid grid-cols-2 gap-4 pt-4">
            <div className="p-4 rounded-xl bg-white/5 border border-white/10 backdrop-blur-sm">
              <div className="flex items-center gap-2 text-indigo-300 font-semibold text-sm mb-1">
                <KeyRound className="h-4 w-4" />
                CBOM Standard
              </div>
              <p className="text-xs text-slate-400">
                CycloneDX 1.6 compliant Cryptographic Bill of Materials generation.
              </p>
            </div>
            <div className="p-4 rounded-xl bg-white/5 border border-white/10 backdrop-blur-sm">
              <div className="flex items-center gap-2 text-emerald-300 font-semibold text-sm mb-1">
                <ShieldAlert className="h-4 w-4" />
                FIPS 203 / 204
              </div>
              <p className="text-xs text-slate-400">
                Automated ML-KEM & ML-DSA migration path recommendations.
              </p>
            </div>
          </div>
        </div>

        <div className="relative z-10 text-xs text-slate-400">
          Enterprise Cryptographic Discovery and Transition (ECDAT) &copy; 2026
        </div>
      </div>

      {/* Form Column */}
      <div className="flex-1 flex items-center justify-center p-8 sm:p-12">
        <div className="w-full max-w-md space-y-8">
          <div className="space-y-2 text-center lg:text-left">
            <div className="lg:hidden flex items-center justify-center gap-2 mb-6">
              <div className="h-9 w-9 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center">
                <ShieldCheck className="h-5 w-5 text-primary" />
              </div>
              <span className="font-bold text-xl">ECDAT</span>
            </div>
            <h2 className="text-2xl font-bold tracking-tight text-foreground">
              Sign in to your account
            </h2>
            <p className="text-sm text-muted-foreground">
              Enter credentials to access the cryptographic discovery console
            </p>
          </div>

          {/* Quick Demo Credentials Pill */}
          <div className="p-3.5 rounded-lg border border-primary/20 bg-primary/5 flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-primary shrink-0" />
              <div>
                <span className="font-semibold text-foreground">Demo Account:</span>{' '}
                <code className="text-muted-foreground">admin@ecdat.demo</code>
              </div>
            </div>
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={fillDemoCredentials}
              className="h-7 text-[11px] px-2.5 border-primary/30 text-primary hover:bg-primary/10"
            >
              Auto-fill
            </Button>
          </div>

          <form className="space-y-5" onSubmit={handleSubmit}>
            <div className="space-y-1.5">
              <label htmlFor="email" className="text-xs font-semibold text-foreground">
                Email address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="pl-9"
                  placeholder="admin@ecdat.demo"
                />
              </div>
            </div>

            <div className="space-y-1.5">
              <label htmlFor="password" className="text-xs font-semibold text-foreground">
                Password
              </label>
              <div className="relative">
                <Lock className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                <Input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="pl-9"
                  placeholder="••••••••"
                />
              </div>
            </div>

            {error && (
              <div className="p-3 rounded-lg border border-destructive/30 bg-destructive/10 text-xs text-destructive flex items-center gap-2">
                <ShieldAlert className="h-4 w-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <Button
              type="submit"
              disabled={isLoading}
              className="w-full h-10 gap-2 font-medium bg-primary hover:bg-primary/90 text-primary-foreground"
            >
              {isLoading ? 'Verifying credentials...' : 'Sign In'}
              <ArrowRight className="h-4 w-4" />
            </Button>
          </form>

          <div className="pt-2 text-center text-xs text-muted-foreground">
            Local verification environment &bull; SQLite fallback enabled
          </div>
        </div>
      </div>
    </div>
  );
}