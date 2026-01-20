'use client';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { Button } from "@/components/ui/button";
import { LogOut } from 'lucide-react';
import { DeveloperModeToggle } from './modes/DeveloperModeToggle';

const Navbar = () => {
    const router = useRouter();

    const handleLogout = () => {
        // Clear token from localStorage
        if (typeof window !== 'undefined') {
            localStorage.removeItem('access_token');
        }
        // Redirect to login
        router.push('/login');
    };

    return (
        <nav className="border-b p-4 flex items-center justify-between bg-zinc-950 text-white">
            <div className="font-bold text-xl tracking-tight">
                <Link href="/dashboard">QueryFlow AI</Link>
            </div>
            <div className="flex gap-3 items-center">
                <Link href="/dashboard">
                    <Button variant="ghost" className="text-white hover:bg-zinc-800 hover:text-white">
                        Dashboard
                    </Button>
                </Link>
                <Link href="/editor">
                    <Button variant="ghost" className="text-white hover:bg-zinc-800 hover:text-white">
                        New Query
                    </Button>
                </Link>
                <Link href="/aimodelselection">
                    <Button variant="ghost" className="text-white hover:bg-zinc-800 hover:text-white">
                        AI Settings
                    </Button>
                </Link>
                <Link href="/my-requests">
                    <Button variant="ghost" className="text-white hover:bg-zinc-800 hover:text-white">
                        My Requests
                    </Button>
                </Link>
                <Link href="/approvals">
                    <Button variant="ghost" className="text-white hover:bg-zinc-800 hover:text-white">
                        Approvals
                    </Button>
                </Link>
                <div className="border-l border-zinc-700 h-6 mx-2"></div>
                <DeveloperModeToggle />
                <Button
                    variant="outline"
                    onClick={handleLogout}
                    className="bg-red-600 border-red-600 text-white hover:bg-red-700 hover:border-red-700 hover:text-white"
                >
                    <LogOut className="h-4 w-4 mr-2" />
                    Logout
                </Button>
            </div>
        </nav>
    );
};

export default Navbar;
