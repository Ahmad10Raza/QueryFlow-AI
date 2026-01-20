'use client';

import { useEffect, useState } from 'react';
import api from '@/lib/api';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Loader2, Clock, User, Activity } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneLight } from 'react-syntax-highlighter/dist/esm/styles/prism';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";

interface AuditLog {
    _id: string;
    user_id: number;
    user_email: string;
    action: string;
    target_id: number;
    target_type: string;
    details: any;
    timestamp: string;
}

export default function AdminAuditPage() {
    const [logs, setLogs] = useState<AuditLog[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchLogs = async () => {
        try {
            const res = await api.get('/admin/users/audit/logs');
            setLogs(res.data);
        } catch (error) {
            console.error("Failed to fetch logs:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLogs();
    }, []);

    if (loading) {
        return <div className="flex justify-center p-8"><Loader2 className="h-8 w-8 animate-spin text-zinc-400" /></div>;
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">Audit Logs</h1>
                    <p className="text-zinc-500">Track all administrative actions.</p>
                </div>
            </div>

            <div className="rounded-md border bg-white">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Timestamp</TableHead>
                            <TableHead>User</TableHead>
                            <TableHead>Action</TableHead>
                            <TableHead>Target</TableHead>
                            <TableHead className="text-right">Details</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {logs.map((log) => (
                            <TableRow key={log._id}>
                                <TableCell className="text-zinc-500 text-sm">
                                    <div className="flex items-center gap-2">
                                        <Clock className="h-3 w-3" />
                                        {new Date(log.timestamp + 'Z').toLocaleString()}
                                    </div>
                                </TableCell>
                                <TableCell>
                                    <div className="flex flex-col">
                                        <span className="font-medium text-sm">{log.user_email || 'Unknown'}</span>
                                        <span className="text-xs text-zinc-400">ID: {log.user_id}</span>
                                    </div>
                                </TableCell>
                                <TableCell>
                                    <Badge
                                        variant="secondary"
                                        className={`font-semibold tracking-wide ${log.action === 'EXECUTE_QUERY' ? 'bg-blue-100 text-blue-700' :
                                            log.action === 'DELETE_USER' ? 'bg-red-100 text-red-700' :
                                                log.action === 'CREATE_USER' ? 'bg-green-100 text-green-700' :
                                                    'bg-gray-100 text-gray-700'
                                            }`}
                                    >
                                        {log.action.replace('_', ' ')}
                                    </Badge>
                                </TableCell>
                                <TableCell>
                                    <div className="flex flex-col">
                                        <span className="text-sm font-medium">{log.target_type || '-'}</span>
                                        {log.target_id && (
                                            <span className="text-xs text-zinc-400">ID: {log.target_id}</span>
                                        )}
                                        {log.details?.database && (
                                            <span className="text-xs text-blue-600">DB: {log.details.database}</span>
                                        )}
                                    </div>
                                </TableCell>
                                <TableCell className="text-right">
                                    <Dialog>
                                        <DialogTrigger asChild>
                                            <Button variant="ghost" size="sm" className="h-8 text-xs">
                                                View Details
                                            </Button>
                                        </DialogTrigger>
                                        <DialogContent className="max-w-2xl max-h-[80vh]">
                                            <DialogHeader>
                                                <DialogTitle>Activity Log Details</DialogTitle>
                                                <DialogDescription>
                                                    {log.action.replace('_', ' ')} by {log.user_email} on {new Date(log.timestamp + 'Z').toLocaleString()}
                                                </DialogDescription>
                                            </DialogHeader>
                                            <div className="max-h-[500px] overflow-auto rounded-md border text-xs">
                                                <SyntaxHighlighter language="json" style={oneLight} customStyle={{ margin: 0 }}>
                                                    {JSON.stringify(log, null, 2)}
                                                </SyntaxHighlighter>
                                            </div>
                                        </DialogContent>
                                    </Dialog>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </div>
        </div>
    );
}
