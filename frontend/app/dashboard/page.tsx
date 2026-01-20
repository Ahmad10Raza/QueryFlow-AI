'use client';
import { useEffect, useState } from 'react';
import Navbar from '@/components/Navbar';
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import api from '@/lib/api';
import Link from 'next/link';
import { PlusCircle, Database } from 'lucide-react';
import { AddConnectionModal } from '@/components/AddConnectionModal';

interface DBConnection {
    id: number;
    name: string;
    db_type: string;
    host: string;
}

export default function DashboardPage() {
    const [connections, setConnections] = useState<DBConnection[]>([]);

    const fetchConnections = async () => {
        try {
            const res = await api.get('/db_connections/');
            setConnections(res.data);
        } catch (error) {
            console.error("Failed to fetch connections", error);
        }
    };

    useEffect(() => {
        fetchConnections();
    }, []);

    return (
        <div className="min-h-screen bg-zinc-50">
            <Navbar />
            <div className="p-8 max-w-7xl mx-auto space-y-6">
                <div className="flex justify-between items-center">
                    <h1 className="text-3xl font-bold tracking-tight text-zinc-900">Dashboard</h1>
                    <AddConnectionModal onConnectionAdded={fetchConnections} />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {connections.map((conn) => (
                        <Card key={conn.id}>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">
                                    {conn.name}
                                </CardTitle>
                                <Database className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold capitalize">{conn.db_type}</div>
                                <p className="text-xs text-muted-foreground">
                                    {conn.host}
                                </p>
                                <div className="mt-4 flex gap-2">
                                    <Link href={`/editor?db=${conn.id}`} className="flex-1">
                                        <Button variant="outline" className="w-full">Query</Button>
                                    </Link>
                                    <Button
                                        variant="secondary"
                                        size="sm"
                                        onClick={async () => {
                                            try {
                                                await api.post(`/schema/${conn.id}/ingest`);
                                                alert("Ingestion started!");
                                            } catch (e) {
                                                alert("Ingestion failed");
                                            }
                                        }}
                                    >
                                        Ingest
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    ))}

                    {connections.length === 0 && (
                        <div className="col-span-3 text-center py-12 text-zinc-500">
                            No database connections found. Click "Add Connection" to start.
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
