import React from 'react';
import { ImpactSummary } from '@/components/ImpactSummary';
import { ScrollArea } from '@/components/ui/scroll-area';
import { AIQueryResponse } from '@/lib/types';
import { Lightbulb } from 'lucide-react';

interface ExplainabilityPanelProps {
    plan: AIQueryResponse | null;
}

export function ExplainabilityPanel({ plan }: ExplainabilityPanelProps) {
    if (!plan) {
        return (
            <div className="h-full flex flex-col items-center justify-center text-zinc-400 p-4 text-center">
                <Lightbulb className="h-8 w-8 mb-2 opacity-50" />
                <span className="text-sm">AI Explanation will appear here after generation.</span>
            </div>
        );
    }

    // Default impact if missing (safe read)
    const impact = plan.impact || { table: 'N/A', affected_rows_estimate: 0, risk_score: 'LOW' };

    return (
        <div className="h-full flex flex-col bg-white">
            <div className="p-3 border-b font-semibold text-sm flex items-center gap-2">
                <Lightbulb className="h-4 w-4 text-amber-500" />
                Query Insights
            </div>
            <div className="flex-1 overflow-y-auto p-4">
                <ImpactSummary
                    impact={impact}
                    explanation={plan.explanation}
                />

                {plan.validation_error && (
                    <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm">
                        <strong>Guardrail Warning:</strong> {plan.validation_error}
                    </div>
                )}
            </div>
        </div>
    );
}
