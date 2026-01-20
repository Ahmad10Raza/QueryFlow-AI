'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { ArrowRight, Database, Shield, Zap } from "lucide-react";

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    // Check if user is authenticated
    const token = localStorage.getItem('token');
    if (token) {
      // Redirect to dashboard if already logged in
      router.push('/dashboard');
    }
  }, [router]);
  return (
    <div className="flex min-h-screen flex-col bg-white text-zinc-900">
      {/* Hero Section */}
      <header className="flex h-16 items-center justify-between px-6 border-b">
        <div className="font-bold text-xl">QueryFlow AI</div>
        <div className="flex gap-4">
          <Link href="/login">
            <Button variant="ghost">Login</Button>
          </Link>
          <Link href="/login">
            <Button>Get Started</Button>
          </Link>
        </div>
      </header>

      <main className="flex-1 flex flex-col items-center justify-center text-center p-10 gap-8">
        <h1 className="text-5xl font-extrabold tracking-tight sm:text-6xl max-w-4xl">
          Talk to your Database <br />
          <span className="text-blue-600">Securely & Intelligently</span>
        </h1>
        <p className="text-xl text-zinc-500 max-w-2xl">
          QueryFlow AI turns natural language into optimized SQL.
          Built with role-based governance, impact analysis, and explainability.
        </p>

        <div className="flex gap-4 mt-4">
          <Link href="/login">
            <Button size="lg" className="h-12 px-8 text-lg">
              Start Querying <ArrowRight className="ml-2 h-5 w-5" />
            </Button>
          </Link>
        </div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-16 max-w-5xl">
          <div className="p-6 border rounded-xl bg-zinc-50 flex flex-col items-center">
            <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center mb-4">
              <Zap className="h-6 w-6 text-blue-600" />
            </div>
            <h3 className="font-bold text-lg mb-2">Instant SQL</h3>
            <p className="text-zinc-500">Ask questions in plain English and get optimized SQL instantly.</p>
          </div>
          <div className="p-6 border rounded-xl bg-zinc-50 flex flex-col items-center">
            <div className="h-12 w-12 bg-green-100 rounded-full flex items-center justify-center mb-4">
              <Shield className="h-6 w-6 text-green-600" />
            </div>
            <h3 className="font-bold text-lg mb-2">Safe & Governed</h3>
            <p className="text-zinc-500">RBAC built-in. Risky queries require approval. Impact analysis included.</p>
          </div>
          <div className="p-6 border rounded-xl bg-zinc-50 flex flex-col items-center">
            <div className="h-12 w-12 bg-amber-100 rounded-full flex items-center justify-center mb-4">
              <Database className="h-6 w-6 text-amber-600" />
            </div>
            <h3 className="font-bold text-lg mb-2">Schema Aware</h3>
            <p className="text-zinc-500">Automatically introspects your database schema for accurate context.</p>
          </div>
        </div>
      </main>

      <footer className="py-6 text-center text-zinc-400 text-sm border-t">
        © 2026 QueryFlow AI. All rights reserved.
      </footer>
    </div>
  );
}
