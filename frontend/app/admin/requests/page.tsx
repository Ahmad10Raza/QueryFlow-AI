'use client';
import { useEffect, useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Loader2, Clock, CheckCircle, XCircle, AlertCircle, User } from 'lucide-react';
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
    created_at: string;
}

export default function PendingRequestsPage() {
    const [requests, setRequests] = useState<QueryRequest[]>([]);
    const [loading, setLoading] = useState(true);
    const [processing, setProcessing] = useState<number | null>(null);
    const [rejectDialog, setRejectDialog] = useState<{ open: boolean; requestId: number | null }>({ open: false, requestId: null });
    const [rejectionReason, setRejectionReason] = useState('');

    useEffect(() => {
        fetchPendingRequests();
    }, []);

    const fetchPendingRequests = async () => {
        try {
            setLoading(true);
            const res = await api.get('/query-requests/pending');
            setRequests(res.data);
        } catch (err) {
            console.error('Failed to fetch pending requests:', err);
            alert('Failed to load pending requests');
        } finally {
            setLoading(false);
        }
    };

    const handleApprove = async (requestId: number) => {
        try {
            setProcessing(requestId);
            await api.put(`/query-requests/${requestId}/approve`);
            alert('Request approved successfully');
            fetchPendingRequests();
        } catch (err: any) {
            alert(err.response?.data?.detail || 'Failed to approve request');
        } finally {
            setProcessing(null);
        }
    };

    const handleReject = async () => {
        if (!rejectDialog.requestId) return;

        try {
            setProcessing(rejectDialog.requestId);
            await api.put(`/query-requests/${rejectDialog.requestId}/reject`, {
                rejection_reason: rejectionReason
            });
            alert('Request rejected');
            setRejectDialog({ open: false, requestId: null });
            setRejectionReason('');
            fetchPendingRequests();
        } catch (err: any) {
            alert(err.response?.data?.detail || 'Failed to reject request');
        } finally {
            setProcessing(null);
        }
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
        <div className="space-y-6">
            <div>
                <h2 className="text-2xl font-bold">Pending Query Requests</h2>
                <p className="text-zinc-600">Review and approve/reject query execution requests from users</p>
            </div>

            {loading ? (
                <div className="flex justify-center p-12">
                    <Loader2 className="h-8 w-8 animate-spin text-zinc-400" />
                </div>
            ) : requests.length === 0 ? (
                <Card>
                    <CardContent className="p-12 text-center text-zinc-500">
                        <CheckCircle className="h-12 w-12 mx-auto mb-4 text-green-300" />
                        <p className="text-lg font-medium">All caught up!</p>
                        <p className="text-sm mt-2">No pending query requests to review</p>
                    </CardContent>
                </Card>
            ) : (
                <div className="space-y-4">
                    {requests.map((request) => (
                        <Card key={request.id} className="border-l-4 border-l-yellow-400">
                            <CardHeader>
                                <div className="flex justify-between items-start">
                                    <div>
                                        <CardTitle className="text-lg flex items-center gap-2">
                                            Request #{request.id}
                                            {getIntentBadge(request.intent)}
                                        </CardTitle>
                                        <CardDescription className="flex items-center gap-2 mt-1">
                                            <User className="h-4 w-4" />
                                            User ID: {request.user_id} • {request.connection_name}
                                        </CardDescription>
                                        <CardDescription>
                                            Submitted {new Date(request.created_at).toLocaleString()}
                                        </CardDescription>
                                    </div>
                                    <Badge className="bg-yellow-100 text-yellow-800">
                                        <Clock className="h-3 w-3 mr-1" />
                                        Pending
                                    </Badge>
                                </div>
                            </CardHeader>
                            <CardContent className="space-y-4">
                                <div>
                                    <h4 className="text-sm font-semibold mb-2">User's Question:</h4>
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

                                {request.intent === 'DELETE' && (
                                    <div className="p-3 rounded-md bg-red-50 border border-red-200">
                                        <p className="text-sm text-red-800 font-medium">
                                            ⚠️ This is a DELETE query - please review carefully before approving
                                        </p>
                                    </div>
                                )}

                                <div className="flex gap-3 pt-2">
                                    <Button
                                        onClick={() => handleApprove(request.id)}
                                        disabled={processing === request.id}
                                        className="flex-1 bg-green-600 hover:bg-green-700"
                                    >
                                        {processing === request.id ? (
                                            <Loader2 className="h-4 w-4 animate-spin" />
                                        ) : (
                                            <>
                                                <CheckCircle className="h-4 w-4 mr-2" />
                                                Approve
                                            </>
                                        )}
                                    </Button>
                                    <Button
                                        onClick={() => setRejectDialog({ open: true, requestId: request.id })}
                                        disabled={processing === request.id}
                                        variant="destructive"
                                        className="flex-1"
                                    >
                                        <XCircle className="h-4 w-4 mr-2" />
                                        Reject
                                    </Button>
                                </div>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            )}

            {/* Rejection Reason Dialog */}
            <Dialog open={rejectDialog.open} onOpenChange={(open) => setRejectDialog({ open, requestId: open ? rejectDialog.requestId : null })}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>Reject Request</DialogTitle>
                        <DialogDescription>
                            Provide a reason for rejection (optional but recommended)
                        </DialogDescription>
                    </DialogHeader>
                    <Textarea
                        placeholder="Enter rejection reason..."
                        value={rejectionReason}
                        onChange={(e) => setRejectionReason(e.target.value)}
                        className="min-h-[100px]"
                    />
                    <DialogFooter>
                        <Button variant="outline" onClick={() => setRejectDialog({ open: false, requestId: null })}>
                            Cancel
                        </Button>
                        <Button variant="destructive" onClick={handleReject} disabled={processing !== null}>
                            {processing !== null ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Reject Request'}
                        </Button>
                    </DialogFooter>
                </DialogContent>
            </Dialog>
        </div>
    );
}
