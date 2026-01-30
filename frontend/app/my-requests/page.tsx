'use client';
import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Navbar from '@/components/Navbar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Loader2, Clock, CheckCircle, XCircle, AlertCircle, Play, FileText } from 'lucide-react';
import api from '@/lib/api';

interface QueryRequest {
    id: number;
    user_id: number;
    connection_id: number;
    connection_name: string;
    question: string;
    generated_sql: string;
    intent: string;
    status: string;
    approved_by?: number;
    approved_at?: string;
    rejection_reason?: string;
    created_at: string;
    executed_at?: string;
}

interface Approval {
    id: number;
    db_connection_id: number;
    prompt_text: string;
    generated_sql: string;
    impact_summary: string;
    risk_level: string;
    status: string;
    created_at: string;
    reviewed_at?: string;
    reviewer_comment?: string;
}

export default function MyRequestsPage() {
    const router = useRouter();
    const [queryRequests, setQueryRequests] = useState<QueryRequest[]>([]);
    const [approvals, setApprovals] = useState<Approval[]>([]);
    const [loading, setLoading] = useState(true);
    const [executing, setExecuting] = useState<number | null>(null);

    useEffect(() => {
        fetchAllRequests();
    }, []);

    const fetchAllRequests = async () => {
        try {
            setLoading(true);
            // Fetch only query requests (legacy data has been migrated)
            const res = await api.get('/query-requests/');
            setQueryRequests(res.data);
            // setApprovals([]); // Clear legacy state if needed, but we removed fetch logic
        } catch (err) {
            console.error('Failed to fetch requests:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleExecute = async (requestId: number) => {
        try {
            setExecuting(requestId);
            const res = await api.post(`/query-requests/${requestId}/execute`);
            alert('Query executed successfully!');
            // Refresh list
            fetchAllRequests();
        } catch (err: any) {
            alert(err.response?.data?.detail || 'Failed to execute query');
        } finally {
            setExecuting(null);
        }
    };

    const getStatusBadge = (status: string) => {
        const config: Record<string, { icon: React.ElementType; color: string; label: string }> = {
            PENDING: { icon: Clock, color: 'bg-yellow-100 text-yellow-800', label: 'Pending' },
            APPROVED: { icon: CheckCircle, color: 'bg-green-100 text-green-800', label: 'Approved' },
            REJECTED: { icon: XCircle, color: 'bg-red-100 text-red-800', label: 'Rejected' },
            EXECUTED: { icon: Play, color: 'bg-blue-100 text-blue-800', label: 'Executed' }
        };
        const { icon: Icon, color, label } = config[status] || config.PENDING;
        return (
            <Badge className={color}>
                <Icon className="h-3 w-3 mr-1" />
                {label}
            </Badge>
        );
    };

    const getIntentBadge = (intent: string) => {
        const colors: Record<string, string> = {
            READ: 'bg-blue-100 text-blue-800',
            UPDATE: 'bg-orange-100 text-orange-800',
            DELETE: 'bg-red-100 text-red-800'
        };
        return <Badge className={colors[intent] || 'bg-gray-100 text-gray-800'}>{intent}</Badge>;
    };

    return (
        <div className="min-h-screen flex flex-col bg-zinc-50">
            <Navbar />
            <div className="flex-1 container mx-auto p-8 max-w-6xl">
                <div className="mb-6">
                    <h1 className="text-3xl font-bold">My Requests</h1>
                    <p className="text-zinc-600 mt-2">Track the status of your query approval requests</p>
                </div>

                {loading ? (
                    <div className="flex justify-center p-12">
                        <Loader2 className="h-8 w-8 animate-spin text-zinc-400" />
                    </div>
                ) : (
                    <Tabs defaultValue="query-requests" className="w-full">
                        <TabsList className="grid w-full grid-cols-1 mb-6">
                            <TabsTrigger value="query-requests">
                                Query Requests ({queryRequests.length})
                            </TabsTrigger>
                        </TabsList>

                        <TabsContent value="query-requests">
                            {queryRequests.length === 0 ? (
                                <Card>
                                    <CardContent className="p-12 text-center text-zinc-500">
                                        <FileText className="h-12 w-12 mx-auto mb-4 text-zinc-300" />
                                        <p>No query requests yet</p>
                                        <p className="text-sm mt-2">UPDATE or DELETE queries that require approval will appear here</p>
                                    </CardContent>
                                </Card>
                            ) : (
                                <div className="space-y-4">
                                    {queryRequests.map((request) => (
                                        <Card key={request.id}>
                                            <CardHeader>
                                                <div className="flex justify-between items-start">
                                                    <div>
                                                        <CardTitle className="text-lg flex items-center gap-2">
                                                            Request #{request.id}
                                                            {getIntentBadge(request.intent)}
                                                        </CardTitle>
                                                        <CardDescription>
                                                            {request.connection_name} • Submitted {new Date(request.created_at).toLocaleString()}
                                                        </CardDescription>
                                                    </div>
                                                    {getStatusBadge(request.status)}
                                                </div>
                                            </CardHeader>
                                            <CardContent className="space-y-4">
                                                <div>
                                                    <h4 className="text-sm font-semibold mb-2">Your Question:</h4>
                                                    <p className="text-sm text-zinc-700 bg-zinc-50 p-3 rounded-md">
                                                        {request.question}
                                                    </p>
                                                </div>

                                                <div>
                                                    <h4 className="text-sm font-semibold mb-2">Generated Query:</h4>
                                                    <pre className="bg-zinc-900 text-zinc-100 p-3 rounded-md text-sm overflow-x-auto">
                                                        {request.generated_sql}
                                                    </pre>
                                                </div>

                                                {request.status === 'APPROVED' && (
                                                    <Button
                                                        onClick={() => router.push(`/editor?requestId=${request.id}&db=${request.connection_id}`)}
                                                        className="w-full"
                                                    >
                                                        <Play className="h-4 w-4 mr-2" />
                                                        Open in Editor to Execute
                                                    </Button>
                                                )}

                                                {request.status === 'REJECTED' && request.rejection_reason && (
                                                    <div className="p-3 rounded-md border bg-red-50 border-red-200">
                                                        <h4 className="text-sm font-semibold mb-1 text-red-800">Rejection Reason:</h4>
                                                        <p className="text-sm text-red-700">{request.rejection_reason}</p>
                                                    </div>
                                                )}

                                                {request.status === 'EXECUTED' && request.executed_at && (
                                                    <div className="p-3 rounded-md border bg-blue-50 border-blue-200">
                                                        <h4 className="text-sm font-semibold text-blue-800">
                                                            Executed on {new Date(request.executed_at).toLocaleString()}
                                                        </h4>
                                                    </div>
                                                )}
                                            </CardContent>
                                        </Card>
                                    ))}
                                </div>
                            )}
                        </TabsContent>

                    </Tabs>
                )}
            </div>
        </div>
    );
}
