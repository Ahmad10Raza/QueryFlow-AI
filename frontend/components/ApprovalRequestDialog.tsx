'use client';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { AlertTriangle } from "lucide-react";
import Link from "next/link";

interface ApprovalRequestDialogProps {
    open: boolean;
    onClose: () => void;
    approvalId: number;
    sqlQuery: string;
    impact?: {
        table?: string;
        affected_rows_estimate?: number;
        risk_score?: string;
    };
}

export default function ApprovalRequestDialog({
    open,
    onClose,
    approvalId,
    sqlQuery,
    impact
}: ApprovalRequestDialogProps) {
    return (
        <Dialog open={open} onOpenChange={onClose}>
            <DialogContent className="max-w-2xl">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                        <AlertTriangle className="h-5 w-5 text-yellow-600" />
                        Approval Required
                    </DialogTitle>
                    <DialogDescription>
                        This query requires administrator approval before execution.
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-4">
                    <div>
                        <h4 className="text-sm font-semibold mb-2">Generated SQL:</h4>
                        <pre className="bg-zinc-900 text-zinc-100 p-3 rounded-md text-sm overflow-x-auto">
                            {sqlQuery}
                        </pre>
                    </div>

                    {impact && (
                        <div className="bg-yellow-50 border border-yellow-200 p-3 rounded-md">
                            <h4 className="text-sm font-semibold mb-2 text-yellow-900">Impact Analysis:</h4>
                            <ul className="text-sm text-yellow-800 space-y-1">
                                {impact.table && <li>• Table: <span className="font-mono">{impact.table}</span></li>}
                                {impact.affected_rows_estimate !== undefined && (
                                    <li>• Estimated Rows Affected: {impact.affected_rows_estimate}</li>
                                )}
                                {impact.risk_score && (
                                    <li>• Risk Level: <span className="font-semibold">{impact.risk_score}</span></li>
                                )}
                            </ul>
                        </div>
                    )}

                    <div className="bg-blue-50 border border-blue-200 p-3 rounded-md">
                        <p className="text-sm text-blue-900">
                            Your request has been submitted for approval.
                            <br />
                            <strong>Approval ID:</strong> #{approvalId}
                        </p>
                    </div>
                </div>

                <DialogFooter className="flex justify-between">
                    <Link href="/my-requests">
                        <Button variant="outline">
                            View My Requests
                        </Button>
                    </Link>
                    <Button onClick={onClose}>
                        Close
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
