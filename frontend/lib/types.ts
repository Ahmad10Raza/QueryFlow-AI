export interface AIQueryResponse {
    intent: string;
    sql_query: string;
    // Execution Results (if executed)
    result?: {
        columns: string[];
        rows: Record<string, any>[];
        error?: string;
    };
    // Top-level error
    error?: string;
    // Phase 2: Metadata
    impact?: {
        table: string;
        affected_rows_estimate: number;
        risk_score: string;
        cols_modified?: string[];
    };
    explanation?: string;
    access_status?: 'APPROVED' | 'REJECTED' | 'NEEDS_APPROVAL' | 'PENDING' | 'PENDING_APPROVAL';
    access_message?: string;
    validation_error?: string;
    approval_id?: number;
    // Phase 4
    is_ambiguous?: boolean;
    disambiguation_options?: { message: string }[];
    // Phase 5
    query_id?: number;
    insights?: {
        impact: string;
        data_scope: string;
        business_meaning: string;
        performance_note: string;
        risk_assessment: string;
    };
}

export interface SchemaMetadata {
    table_name: string;
    columns: { name: string; type: string }[];
}
