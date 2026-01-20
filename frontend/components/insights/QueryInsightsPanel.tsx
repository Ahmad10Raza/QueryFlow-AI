"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { AlertCircle, CheckCircle2, Info, TrendingUp, Database, AlertTriangle } from "lucide-react";

interface QueryInsights {
    impact: string;
    data_scope: string;
    business_meaning: string;
    performance_note: string;
    risk_assessment: string;
}

interface ImpactData {
    table?: string;
    affected_rows_estimate?: number;
    risk_score?: string;
    cols_modified?: string[];
}

interface QueryInsightsPanelProps {
    insights: QueryInsights | null;
    impact?: ImpactData | null;
}

export function QueryInsightsPanel({ insights, impact }: QueryInsightsPanelProps) {
    const hasData = insights || impact;

    if (!hasData) {
        return (
            <Card className="border-border bg-card text-card-foreground">
                <CardHeader>
                    <CardTitle className="text-sm font-medium flex items-center gap-2">
                        <TrendingUp className="h-4 w-4" />
                        AI Meaning Insight
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <p className="text-sm text-muted-foreground italic">Run a query to see insights</p>
                </CardContent>
            </Card>
        );
    }

    const getImpactIcon = (impactStr: string) => {
        if (impactStr.includes("Low") || impactStr.includes("Informational")) {
            return <CheckCircle2 className="h-4 w-4 text-green-500" />;
        }
        if (impactStr.includes("Medium")) {
            return <Info className="h-4 w-4 text-yellow-500" />;
        }
        return <AlertCircle className="h-4 w-4 text-red-500" />;
    };

    const getImpactColor = (impactStr: string) => {
        if (impactStr.includes("Low") || impactStr.includes("Informational")) {
            return "bg-green-500/10 text-green-500 border-green-500/20";
        }
        if (impactStr.includes("Medium")) {
            return "bg-yellow-500/10 text-yellow-500 border-yellow-500/20";
        }
        return "bg-red-500/10 text-red-500 border-red-500/20";
    };

    const getRiskColor = (risk?: string) => {
        if (!risk) return "bg-zinc-500/10 text-zinc-400 border-zinc-500/20";
        if (risk.toLowerCase().includes("low")) {
            return "bg-green-500/10 text-green-500 border-green-500/20";
        }
        if (risk.toLowerCase().includes("medium")) {
            return "bg-yellow-500/10 text-yellow-500 border-yellow-500/20";
        }
        return "bg-red-500/10 text-red-500 border-red-500/20";
    };

    return (
        <Card className="border-border bg-card text-card-foreground">
            <CardHeader>
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                    <TrendingUp className="h-4 w-4" />
                    AI Meaning Insight
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                {/* Impact Analysis Section */}
                {impact && (
                    <div className="space-y-3 pb-4 border-b border-border">
                        <div className="flex items-center gap-2">
                            <Database className="h-4 w-4 text-blue-500" />
                            <span className="text-xs font-medium text-muted-foreground">Impact Analysis</span>
                        </div>

                        <div className="grid grid-cols-2 gap-2 text-xs">
                            <div>
                                <div className="text-muted-foreground">Target Table</div>
                                <div className="font-mono">{impact.table || 'N/A'}</div>
                            </div>
                            <div>
                                <div className="text-muted-foreground">Est. Rows Affected</div>
                                <div>{impact.affected_rows_estimate || 0}</div>
                            </div>
                        </div>

                        {impact.risk_score && (
                            <Badge variant="outline" className={getRiskColor(impact.risk_score)}>
                                {impact.risk_score.toUpperCase()} RISK
                            </Badge>
                        )}

                        {impact.cols_modified && impact.cols_modified.length > 0 && (
                            <div className="text-xs">
                                <div className="text-muted-foreground mb-1">Columns Modified</div>
                                <div className="flex flex-wrap gap-1">
                                    {impact.cols_modified.map((col, i) => (
                                        <Badge key={i} variant="secondary" className="text-xs">
                                            {col}
                                        </Badge>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                )}

                {/* AI Insights Section */}
                {insights && (
                    <>
                        {/* Impact */}
                        <div className="space-y-2">
                            <div className="flex items-center gap-2">
                                {getImpactIcon(insights.impact || "Unknown")}
                                <span className="text-xs font-medium text-muted-foreground">Impact</span>
                            </div>
                            <Badge variant="outline" className={getImpactColor(insights.impact || "Unknown")}>
                                {insights.impact || "Unknown"}
                            </Badge>
                        </div>

                        {/* Data Scope */}
                        <div className="space-y-2">
                            <div className="text-xs font-medium text-muted-foreground">Data Scope</div>
                            <p className="text-sm">{insights.data_scope || "N/A"}</p>
                        </div>

                        {/* Business Meaning */}
                        <div className="space-y-2">
                            <div className="text-xs font-medium text-muted-foreground">Business Meaning</div>
                            <p className="text-sm">{insights.business_meaning || "N/A"}</p>
                        </div>

                        {/* Performance Note */}
                        {insights.performance_note && (
                            <div className="space-y-2">
                                <div className="text-xs font-medium text-muted-foreground">Performance</div>
                                <p className="text-sm text-muted-foreground italic">{insights.performance_note}</p>
                            </div>
                        )}

                        {/* Risk Assessment */}
                        <div className="space-y-2">
                            <div className="text-xs font-medium text-muted-foreground">Risk Assessment</div>
                            <p className="text-sm">{insights.risk_assessment || "N/A"}</p>
                        </div>
                    </>
                )}
            </CardContent>
        </Card>
    );
}
