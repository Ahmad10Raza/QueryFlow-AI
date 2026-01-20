'use client';

import { useEffect, useState } from 'react';
import api from '@/lib/api';
import { Users, Activity, AlertTriangle, CheckCircle, Loader2 } from 'lucide-react';

interface SystemStats {
    total_users: number;
    active_users_today: number;
    total_queries: number;
    queries_today: number;
    failed_queries_today: number;
    pending_approvals: number;
}

export default function AdminOverviewPage() {
    const [stats, setStats] = useState<SystemStats | null>(null);
    const [loading, setLoading] = useState(true);

    const fetchStats = async () => {
        try {
            const res = await api.get('/admin/stats');
            setStats(res.data);
        } catch (error) {
            console.error("Failed to fetch stats:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchStats();
        // Refresh every 30 seconds
        const interval = setInterval(fetchStats, 30000);
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return <div className="flex justify-center p-8"><Loader2 className="h-8 w-8 animate-spin text-zinc-400" /></div>;
    }

    const failureRate = stats && stats.queries_today > 0
        ? ((stats.failed_queries_today / stats.queries_today) * 100).toFixed(1)
        : '0.0';

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold tracking-tight">System Overview</h1>
                <p className="text-zinc-500">Platform health and key metrics.</p>
            </div>

            {/* Stat Cards */}
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                <div className="rounded-xl border bg-white p-6 shadow-sm">
                    <div className="flex flex-row items-center justify-between pb-2">
                        <h3 className="text-sm font-medium text-zinc-500">Total Users</h3>
                        <Users className="h-4 w-4 text-zinc-400" />
                    </div>
                    <div className="text-2xl font-bold">{stats?.total_users || 0}</div>
                    <p className="text-xs text-zinc-500">{stats?.active_users_today || 0} active today</p>
                </div>
                <div className="rounded-xl border bg-white p-6 shadow-sm">
                    <div className="flex flex-row items-center justify-between pb-2">
                        <h3 className="text-sm font-medium text-zinc-500">Queries Today</h3>
                        <Activity className="h-4 w-4 text-zinc-400" />
                    </div>
                    <div className="text-2xl font-bold">{stats?.queries_today || 0}</div>
                    <p className="text-xs text-zinc-500">{stats?.total_queries || 0} total</p>
                </div>
                <div className="rounded-xl border bg-white p-6 shadow-sm">
                    <div className="flex flex-row items-center justify-between pb-2">
                        <h3 className="text-sm font-medium text-zinc-500">Failed Queries</h3>
                        <AlertTriangle className="h-4 w-4 text-red-400" />
                    </div>
                    <div className="text-2xl font-bold text-red-600">{stats?.failed_queries_today || 0}</div>
                    <p className="text-xs text-zinc-500">{failureRate}% failure rate</p>
                </div>
                <div className="rounded-xl border bg-white p-6 shadow-sm">
                    <div className="flex flex-row items-center justify-between pb-2">
                        <h3 className="text-sm font-medium text-zinc-500">Pending Approvals</h3>
                        <CheckCircle className="h-4 w-4 text-yellow-400" />
                    </div>
                    <div className="text-2xl font-bold text-yellow-600">{stats?.pending_approvals || 0}</div>
                    <p className="text-xs text-zinc-500">Awaiting review</p>
                </div>
            </div>
        </div>
    );
}
