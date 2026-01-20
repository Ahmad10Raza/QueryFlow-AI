'use client';
import { useEffect, useState } from 'react';
import Navbar from '@/components/Navbar';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Badge } from "@/components/ui/badge";
import { Loader2, CheckCircle, XCircle, Clock } from 'lucide-react';
import api from '@/lib/api';

interface Approval {
    id: number;
    requested_by_user_id: number;
    db_connection_id: number;
    prompt_text: string;
    generated_sql: string;
    impact_summary: string;
    risk_level: string;
    status: string;
    created_at: string;
    reviewer_comment?: string;
}

export default function ApprovalsPage() {
    const [approvals, setApprovals] = useState<Approval[]>([]);
    const [loading, setLoading] = useState(true);
    const [processingId, setProcessingId] = useState<number | null>(null);
    const [comments, setComments] = useState<Record<number, string>>({});

    useEffect(() => {
        fetchApprovals();
    }, []);

    const fetchApprovals = async () => {
        try {
            setLoading(true);
            const res = await api.get('/approvals/');
            setApprovals(res.data);
        } catch (err) {
            console.error('Failed to fetch approvals:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleApprove = async (approvalId: number) => {
        setProcessingId(approvalId);
        try {
            await api.post(`/approvals/${approvalId}/approve`, {
                comment: comments[approvalId] || ''
            });
            await fetchApprovals();
        } catch (err) {
            console.error('Failed to approve:', err);
        } finally {
            setProcessingId(null);
        }
    };

    const handleReject = async (approvalId: number) => {
        setProcessingId(approvalId);
        try {
            await api.post(`/approvals/${approvalId}/reject`, {
                comment: comments[approvalId] || ''
            });
            await fetchApprovals();
        } catch (err) {
            console.error('Failed to reject:', err);
        } finally {
            setProcessingId(null);
        }
    };

    const getRiskBadge = (risk: string) => {
        const colors = {
            HIGH: 'bg-red-100 text-red-800',
            MEDIUM: 'bg-yellow-100 text-yellow-800',
            LOW: 'bg-green-100 text-green-800'
        };
        return <Badge className={colors[risk as keyof typeof colors] || colors.MEDIUM}>{risk}</Badge>;
    };

    return (
        <div className="min-h-screen flex flex-col bg-zinc-50">
            <Navbar />
            <div className="flex-1 container mx-auto p-8 max-w-6xl">
                <div className="mb-6">
                    <h1 className="text-3xl font-bold">Approval Console</h1>
                    <p className="text-zinc-600 mt-2">Review and approve pending query requests</p>
                </div>

                {loading ? (
                    <div className="flex justify-center p-12">
                        <Loader2 className="h-8 w-8 animate-spin text-zinc-400" />
                    </div>
                ) : approvals.length === 0 ? (
                    <Card>
                        <CardContent className="p-12 text-center text-zinc-500">
                            <Clock className="h-12 w-12 mx-auto mb-4 text-zinc-300" />
                            <p>No pending approvals</p>
                        </CardContent>
                    </Card>
                ) : (
                    <div className="space-y-4">
                        {approvals.map((approval) => (
                            <Card key={approval.id}>
                                <CardHeader>
                                    <div className="flex justify-between items-start">
                                        <div>
                                            <CardTitle className="text-lg">Approval Request #{approval.id}</CardTitle>
                                            <CardDescription>
                                                Requested {new Date(approval.created_at).toLocaleString()}
                                            </CardDescription>
                                        </div>
                                        {getRiskBadge(approval.risk_level)}
                                    </div>
                                </CardHeader>
                                <CardContent className="space-y-4">
                                    <div>
                                        <h4 className="text-sm font-semibold mb-2">User Question:</h4>
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

                                    {approval.impact_summary && (
                                        <div>
                                            <h4 className="text-sm font-semibold mb-2">Impact Analysis:</h4>
                                            <div className="bg-yellow-50 border border-yellow-200 p-3 rounded-md text-sm">
                                                <pre className="text-yellow-900 whitespace-pre-wrap">
                                                    {JSON.stringify(JSON.parse(approval.impact_summary), null, 2)}
                                                </pre>
                                            </div>
                                        </div>
                                    )}

                                    <div>
                                        <h4 className="text-sm font-semibold mb-2">Reviewer Comment (Optional):</h4>
                                        <Textarea
                                            value={comments[approval.id] || ''}
                                            onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setComments({ ...comments, [approval.id]: e.target.value })}
                                            placeholder="Add a comment for the requester..."
                                            className="min-h-[80px]"
                                        />
                                    </div>

                                    <div className="flex gap-3 justify-end">
                                        <Button
                                            variant="outline"
                                            onClick={() => handleReject(approval.id)}
                                            disabled={processingId === approval.id}
                                            className="border-red-200 text-red-700 hover:bg-red-50"
                                        >
                                            {processingId === approval.id ? (
                                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                            ) : (
                                                <XCircle className="mr-2 h-4 w-4" />
                                            )}
                                            Reject
                                        </Button>
                                        <Button
                                            onClick={() => handleApprove(approval.id)}
                                            disabled={processingId === approval.id}
                                            className="bg-green-600 hover:bg-green-700"
                                        >
                                            {processingId === approval.id ? (
                                                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                            ) : (
                                                <CheckCircle className="mr-2 h-4 w-4" />
                                            )}
                                            Approve
                                        </Button>
                                    </div>
                                </CardContent>
                            </Card>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}
