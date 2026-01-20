'use client';
import { useEffect, useState } from 'react';
import Navbar from '@/components/Navbar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Loader2, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import api from '@/lib/api';

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
    const [approvals, setApprovals] = useState<Approval[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchMyRequests();
    }, []);

    const fetchMyRequests = async () => {
        try {
            setLoading(true);
            const res = await api.get('/approvals/my-requests');
            setApprovals(res.data);
        } catch (err) {
            console.error('Failed to fetch requests:', err);
        } finally {
            setLoading(false);
        }
    };

    const getStatusBadge = (status: string) => {
        const config = {
            PENDING: { icon: Clock, color: 'bg-yellow-100 text-yellow-800', label: 'Pending' },
            APPROVED: { icon: CheckCircle, color: 'bg-green-100 text-green-800', label: 'Approved' },
            REJECTED: { icon: XCircle, color: 'bg-red-100 text-red-800', label: 'Rejected' }
        };
        const { icon: Icon, color, label } = config[status as keyof typeof config] || config.PENDING;
        return (
            <Badge className={color}>
                <Icon className="h-3 w-3 mr-1" />
                {label}
            </Badge>
        );
    };

    return (
        <div className="min-h-screen flex flex-col bg-zinc-50">
            <Navbar />
            <div className="flex-1 container mx-auto p-8 max-w-6xl">
                <div className="mb-6">
                    <h1 className="text-3xl font-bold">My Approval Requests</h1>
                    <p className="text-zinc-600 mt-2">Track the status of your query approval requests</p>
                </div>

                {loading ? (
                    <div className="flex justify-center p-12">
                        <Loader2 className="h-8 w-8 animate-spin text-zinc-400" />
                    </div>
                ) : approvals.length === 0 ? (
                    <Card>
                        <CardContent className="p-12 text-center text-zinc-500">
                            <AlertCircle className="h-12 w-12 mx-auto mb-4 text-zinc-300" />
                            <p>No approval requests yet</p>
                        </CardContent>
                    </Card>
                ) : (
                    <div className="space-y-4">
                        {approvals.map((approval) => (
                            <Card key={approval.id}>
                                <CardHeader>
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <CardTitle className="text-lg">Request #{approval.id}</CardTitle>
                                            <CardDescription>
                                                Submitted {new Date(approval.created_at).toLocaleString()}
                                            </CardDescription>
                                        </div>
                                        {getStatusBadge(approval.status)}
                                    </div>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div>
                                        <h4 className="text-sm font-semibold mb-2">Your Question:</h4>
                                        <p className="text-sm text-zinc-700 bg-zinc-50 p-3 rounded-md">
                                            {approval.prompt_text}
                                        </p>
                                    </div>

                                    <div>
                                        <h4 className="text-sm font-semibold mb-2">Generated SQL:</h4>
                                        <pre className="bg-zinc-900 text-zinc-100 p-3 rounded-md text-sm overflow-x-auto">
                                            {approval.generated_sql}
                                        </pre>
                                    </div>

                                    {approval.status !== 'PENDING' && approval.reviewed_at && (
                                        <div className={`p-3 rounded-md border ${approval.status === 'APPROVED'
                                                ? 'bg-green-50 border-green-200'
                                                : 'bg-red-50 border-red-200'
                                            }`}>
                                            <h4 className="text-sm font-semibold mb-1">
                                                {approval.status === 'APPROVED' ? 'Approved' : 'Rejected'} on{' '}
                                                {new Date(approval.reviewed_at).toLocaleString()}
                                            </h4>
                                            {approval.reviewer_comment && (
                                                <p className="text-sm mt-2">
                                                    <strong>Reviewer Comment:</strong> {approval.reviewer_comment}
                                                </p>
                                            )}
                                        </div>
                                    )}
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
