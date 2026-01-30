"use client";

import { useEffect, useState } from "react";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Button } from "@/components/ui/button";
import { Clock, MessageSquare, PlayCircle, History, AlertCircle } from "lucide-react";
import api from "@/lib/api";
import { formatDistanceToNow } from "date-fns";
import { useQueryStore } from "@/store/queryStore";

interface HistoryItem {
    id: number;
    question: string;
    generated_sql: string;
    intent: string;
    execution_status: string;
    created_at: string;
    connection_name: string;
    insights: any;
}

interface QueryHistoryPanelProps {
    onReplay?: (question: string) => void;
}

export function QueryHistoryPanel({ onReplay }: QueryHistoryPanelProps) {
    const [history, setHistory] = useState<HistoryItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const { setCurrentSql, addMessage, setGeneratedPlan } = useQueryStore();

    const fetchHistory = async () => {
        setLoading(true);
        try {
            const res = await api.get("/history/");
            setHistory(res.data);
            setError(null);
        } catch (err: any) {
            console.error("Failed to fetch history:", err);
            setError("Failed to load history");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchHistory();
    }, []);

    const handleReplay = (item: HistoryItem) => {
        // 1. Set the SQL in the editor
        setCurrentSql(item.generated_sql);

        // 2. Add as a message to chat for context
        addMessage("user", item.question);

        // 3. Populate insights/plan if they exist
        if (item.insights) {
            setGeneratedPlan({
                intent: item.intent,
                sql_query: item.generated_sql,
                insights: item.insights,
                explanation: "Loaded from history"
            } as any);
        }

        // 4. Actually re-run the query if callback is provided
        if (onReplay) {
            addMessage("assistant", "Replaying query from history...");
            onReplay(item.question);
        } else {
            addMessage("assistant", "Query loaded from history. Press Execute to run it.");
        }
    };

    if (loading) {
        return (
            <div className="flex-1 flex items-center justify-center p-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-zinc-500"></div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="flex-1 flex flex-col items-center justify-center p-4 text-center space-y-2">
                <AlertCircle className="h-8 w-8 text-red-500/50" />
                <p className="text-sm text-zinc-400">{error}</p>
                <Button variant="outline" size="sm" onClick={fetchHistory}>Retry</Button>
            </div>
        );
    }

    if (history.length === 0) {
        return (
            <div className="flex-1 flex flex-col items-center justify-center p-4 text-center">
                <History className="h-8 w-8 text-zinc-600 mb-2" />
                <p className="text-sm text-zinc-500 italic">No query history yet</p>
            </div>
        );
    }

    return (
        <ScrollArea className="flex-1">
            <div className="p-2 space-y-2">
                {history.map((item) => (
                    <div
                        key={item.id}
                        className="group flex flex-col p-3 rounded-lg border border-zinc-800 bg-zinc-900/50 hover:border-zinc-700 hover:bg-zinc-900 transition-all cursor-pointer"
                        onClick={() => handleReplay(item)}
                    >
                        <div className="flex items-start justify-between gap-2 mb-2">
                            <div className="flex items-center gap-1.5 min-w-0">
                                <MessageSquare className="h-3 w-3 text-zinc-500 shrink-0" />
                                <span className="text-xs font-medium text-zinc-200 truncate">
                                    {item.question}
                                </span>
                            </div>
                            <span className="text-[10px] text-zinc-500 shrink-0 whitespace-nowrap">
                                {formatDistanceToNow(new Date(item.created_at), { addSuffix: true })}
                            </span>
                        </div>

                        <div className="flex items-center gap-3 mt-1">
                            <div className="flex items-center gap-1">
                                <div className={`h-1.5 w-1.5 rounded-full ${item.execution_status === 'SUCCESS' ? 'bg-green-500' : 'bg-red-500'}`} />
                                <span className="text-[10px] uppercase text-zinc-500">{item.execution_status}</span>
                            </div>
                            <div className="flex items-center gap-1">
                                <PlayCircle className="h-3 w-3 text-zinc-500" />
                                <span className="text-[10px] text-zinc-500">{item.connection_name}</span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </ScrollArea>
    );
}
