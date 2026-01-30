'use client';

import { ReactNode } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import Navbar from '@/components/Navbar';
import { cn } from '@/lib/utils';
import { Users, Activity, BarChart3, ShieldAlert, ClipboardList } from 'lucide-react';

export default function AdminLayout({ children }: { children: ReactNode }) {
    const pathname = usePathname();

    const navItems = [
        { name: 'System Overview', href: '/admin', icon: BarChart3 },
        { name: 'Pending Requests', href: '/admin/requests', icon: ClipboardList },
        { name: 'User Management', href: '/admin/users', icon: Users },
        { name: 'Audit Logs', href: '/admin/audit', icon: Activity },
    ];

    return (
        <div className="min-h-screen bg-zinc-50 flex flex-col">
            <Navbar />
            <div className="flex flex-1">
                {/* Admin Sidebar */}
                <aside className="w-64 bg-white border-r h-[calc(100vh-64px)] overflow-y-auto">
                    <div className="p-4 border-b">
                        <h2 className="font-semibold text-zinc-900 flex items-center gap-2">
                            <ShieldAlert className="h-5 w-5 text-indigo-600" />
                            Admin Console
                        </h2>
                    </div>
                    <nav className="p-4 space-y-1">
                        {navItems.map((item) => {
                            const isActive = pathname === item.href;
                            const Icon = item.icon;
                            return (
                                <Link
                                    key={item.href}
                                    href={item.href}
                                    className={cn(
                                        "flex items-center gap-3 px-3 py-2 text-sm font-medium rounded-md transition-colors",
                                        isActive
                                            ? "bg-indigo-50 text-indigo-600"
                                            : "text-zinc-600 hover:bg-zinc-100 hover:text-zinc-900"
                                    )}
                                >
                                    <Icon className="h-4 w-4" />
                                    {item.name}
                                </Link>
                            );
                        })}
                    </nav>
                </aside>

                {/* Main Content */}
                <main className="flex-1 p-8 overflow-auto h-[calc(100vh-64px)]">
                    <div className="max-w-6xl mx-auto">
                        {children}
                    </div>
                </main>
            </div>
        </div>
    );
}
