'use client';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { HelpCircle } from "lucide-react";

interface TableDisambiguationDialogProps {
    open: boolean;
    onClose: () => void;
    options: { message: string }[];
    onRetry: (clarification: string) => void;
}

export default function TableDisambiguationDialog({
    open,
    onClose,
    options,
    onRetry
}: TableDisambiguationDialogProps) {
    const message = options[0]?.message || "I'm unsure which tables to use.";

    return (
        <Dialog open={open} onOpenChange={onClose}>
            <DialogContent className="max-w-md">
                <DialogHeader>
                    <DialogTitle className="flex items-center gap-2">
                        <HelpCircle className="h-5 w-5 text-blue-600" />
                        Clarification Needed
                    </DialogTitle>
                    <DialogDescription>
                        The AI needs more information to choose the correct tables.
                    </DialogDescription>
                </DialogHeader>

                <div className="space-y-4 py-4">
                    <p className="text-sm text-zinc-700">{message}</p>

                    <div className="bg-blue-50 border border-blue-100 p-3 rounded-md text-sm text-blue-800">
                        Try rephrasing your question to be more specific. For example:
                        <ul className="list-disc ml-5 mt-1 space-y-1">
                            <li>"Show me <strong>sales orders</strong>..."</li>
                            <li>"List <strong>customer transactions</strong>..."</li>
                        </ul>
                    </div>
                </div>

                <DialogFooter>
                    <Button onClick={onClose} variant="secondary">Cancel</Button>
                    <Button onClick={() => {
                        onClose();
                        // Ideally we pre-fill the chat input or focus it
                    }}>
                        I'll Rephrase
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    );
}
