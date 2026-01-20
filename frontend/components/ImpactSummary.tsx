import React from 'react';
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { AlertTriangle, Info, CheckCircle } from "lucide-react";

interface ImpactProps {
    impact: {
        table: string;
        affected_rows_estimate: number;
        risk_score: string;
        cols_modified?: string[];
    };
    explanation?: string;
}

export function ImpactSummary({ impact, explanation }: ImpactProps) {
    const isHighRisk = impact.risk_score.toLowerCase() === 'high';
    const isMediumRisk = impact.risk_score.toLowerCase() === 'medium';

    let icon = <Info className="h-5 w-5 text-blue-500" />;
    let borderColor = "border-blue-200";
    let bgColor = "bg-blue-50/50";

    if (isHighRisk) {
        icon = <AlertTriangle className="h-5 w-5 text-red-600" />;
        borderColor = "border-red-200";
        bgColor = "bg-red-50/50";
    } else if (isMediumRisk) {
        icon = <AlertTriangle className="h-5 w-5 text-yellow-600" />;
        borderColor = "border-yellow-200";
        bgColor = "bg-yellow-50/50";
    }

    return (
        <div className="flex flex-col gap-3">
            {explanation && (
                <div className="p-3 bg-white rounded border text-sm text-zinc-700 shadow-sm">
                    <strong>AI Explanation:</strong> {explanation}
                </div>
            )}

            <Alert className={`${bgColor} ${borderColor}`}>
                <div className="flex items-start gap-3">
                    {icon}
                    <div className="flex-1">
                        <AlertTitle className="mb-2 font-semibold">
                            Impact Analysis
                            <Badge variant={isHighRisk ? "destructive" : "outline"} className="ml-2 uppercase text-[10px]">
                                {impact.risk_score} Risk
                            </Badge>
                        </AlertTitle>
                        <AlertDescription className="text-sm grid grid-cols-2 gap-2">
                            <div>
                                <span className="text-zinc-500 block text-xs">Target Table</span>
                                <span className="font-mono font-medium">{impact.table}</span>
                            </div>
                            <div>
                                <span className="text-zinc-500 block text-xs">Est. Rows Affected</span>
                                <span className="font-mono font-medium">{impact.affected_rows_estimate >= 0 ? impact.affected_rows_estimate : "Unknown"}</span>
                            </div>
                            {impact.cols_modified && impact.cols_modified.length > 0 && (
                                <div className="col-span-2">
                                    <span className="text-zinc-500 block text-xs">Columns Modified</span>
                                    <span className="font-mono text-xs">{impact.cols_modified.join(', ')}</span>
                                </div>
                            )}
                        </AlertDescription>
                    </div>
                </div>
            </Alert>
        </div>
    );
}
