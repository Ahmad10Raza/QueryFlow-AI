'use client';
import { useEffect, useState, useRef } from 'react';
import { useSearchParams } from 'next/navigation';
import Navbar from '@/components/Navbar';
import CodeEditor from '@/components/Editor';
import ResultTable from '@/components/ResultTable';
import { Button } from "@/components/ui/button";
import { Play, Loader2, List, SidebarClose, SidebarOpen, Layout, Download, Copy, FileSpreadsheet, FileText, ClipboardCopy } from 'lucide-react';
import api from '@/lib/api';
import { ChatPanel } from '@/components/ide/ChatPanel';
import { ExplainabilityPanel } from '@/components/ide/ExplainabilityPanel';
import { useWorkspaceStore } from '@/store/workspaceStore';
import { useQueryStore } from '@/store/queryStore';
import { useUIStore } from '@/store/uiStore';
import { SchemaExplorer } from '@/components/ide/SchemaExplorer';
import { QueryHistoryPanel } from '@/components/ide/QueryHistoryPanel';
import { ScrollArea } from '@/components/ui/scroll-area';
import { AIQueryResponse } from '@/lib/types';
import ApprovalRequestDialog from '@/components/ApprovalRequestDialog';
import TableDisambiguationDialog from '@/components/ide/TableDisambiguationDialog';
import { QueryInsightsPanel } from '@/components/insights/QueryInsightsPanel';
import { ResizableHandle, ResizablePanel, ResizablePanelGroup } from "@/components/ui/resizable";

export default function EditorPage() {
    const searchParams = useSearchParams();
    const dbId = searchParams.get('db');

    // Stores
    const { isSidebarOpen, toggleSidebar, activeDbId, setActiveDbId } = useWorkspaceStore();
    const { developerMode } = useUIStore();
    const {
        currentSql, setCurrentSql,
        generatedPlan, setGeneratedPlan,
        result, setResult,
        messages, addMessage,
        isExecuting, setExecuting
    } = useQueryStore();

    // Approval dialog state
    const [approvalDialogOpen, setApprovalDialogOpen] = useState(false);
    const [approvalData, setApprovalData] = useState<{
        approvalId: number;
        sqlQuery: string;
        impact?: any;
    } | null>(null);

    // Ambiguity state
    const [ambiguityOpen, setAmbiguityOpen] = useState(false);
    const [ambiguityOptions, setAmbiguityOptions] = useState<{ message: string }[]>([]);

    // Sidebar Tab state
    const [sidebarTab, setSidebarTab] = useState<'schema' | 'history'>('schema');

    // Approved Request Execution State
    const [approvedRequestId, setApprovedRequestId] = useState<number | null>(null);
    const [approvedSql, setApprovedSql] = useState<string | null>(null);
    const processedRequestIdRef = useRef<number | null>(null);
    const editorRef = useRef<any>(null);

    const handleEditorDidMount = (editor: any, monaco: any) => {
        editorRef.current = editor;
    };

    useEffect(() => {
        if (dbId) setActiveDbId(parseInt(dbId));
    }, [dbId, setActiveDbId]);

    // Clear approved status if user edits the query
    useEffect(() => {
        if (approvedRequestId && approvedSql && currentSql !== approvedSql) {
            console.log("Query modified, switching to normal execution mode");
            setApprovedRequestId(null);
            setApprovedSql(null);
        }
    }, [currentSql, approvedRequestId, approvedSql]);

    useEffect(() => {
        const requestId = searchParams.get('requestId');
        if (requestId) {
            const id = parseInt(requestId);

            // Prevent duplicate processing
            if (processedRequestIdRef.current === id) return;
            processedRequestIdRef.current = id;

            setApprovedRequestId(id);
            // Fetch request details
            api.get('/query-requests/')
                .then((res) => {
                    const req = res.data.find((r: any) => r.id === id);
                    if (req) {
                        setCurrentSql(req.generated_sql);
                        setApprovedSql(req.generated_sql);
                        if (req.connection_id) setActiveDbId(req.connection_id);
                        addMessage('assistant', `✅ **Loaded Approved Request #${id}**\n\nReady to execute. Click the "Run" button to proceed.\n\n*Note: Editing this query will switch to normal execution mode.*`);
                    }
                })
                .catch(err => console.error("Failed to load request:", err));
        }
    }, [searchParams, setActiveDbId, setCurrentSql, addMessage]);

    const handleRunAI = async (text: string) => {
        if (!dbId) return alert("No database selected");

        addMessage('user', text);
        setExecuting(true);
        try {
            const res = await api.post('/query/nl', {
                connection_id: parseInt(dbId),
                question: text
            });
            const data: AIQueryResponse = res.data;

            console.log("AI Response:", data);

            console.log("Processing AI Response data...");
            setGeneratedPlan(data);
            console.log("Generated plan set.");

            if (data.error) {
                console.log("Handling error case");
                setResult({ columns: [], rows: [], error: data.error });
                addMessage('assistant', `⚠️ Error: ${data.error}`);
            } else if (data.access_status === 'NEEDS_APPROVAL' && data.approval_id) {
                console.log("Handling approval case (legacy)");
                // Show approval dialog
                setApprovalData({
                    approvalId: data.approval_id,
                    sqlQuery: data.sql_query || '',
                    impact: data.impact
                });
                setApprovalDialogOpen(true);
                addMessage('assistant', `⚠️ This query requires admin approval. Approval request #${data.approval_id} has been created.`);
            } else if (data.access_status === 'PENDING_APPROVAL' && data.approval_id) {
                console.log("Handling RBAC approval case");
                // Show the generated query and inform user
                if (data.sql_query) {
                    setCurrentSql(data.sql_query);
                }
                addMessage('assistant', `🔒 **Approval Required**\n\nThis ${data.intent || 'query'} operation requires admin approval.\n\n**Generated Query:**\n\`\`\`sql\n${data.sql_query}\n\`\`\`\n\n✅ Request #${data.approval_id} has been created. Check "My Requests" to track its status.`);
            } else if (data.is_ambiguous) {
                console.log("Handling ambiguity case");
                setAmbiguityOptions(data.disambiguation_options || []);
                setAmbiguityOpen(true);
                addMessage('assistant', `🤔 I need clarification. Please see the dialog.`);
            } else {
                console.log("Handling success case");
                if (data.sql_query) {
                    console.log("Setting current SQL:", data.sql_query);
                    setCurrentSql(data.sql_query);
                    // Also show in chat for visibility
                    addMessage('assistant', `Generated SQL:\n\`\`\`sql\n${data.sql_query}\n\`\`\``);
                }
                if (data.result) {
                    console.log("Setting execution result:", data.result);
                    setResult(data.result);
                }

                // Only show explanation if it provides extra value
                if (data.explanation && data.explanation !== "No query generated.") {
                    addMessage('assistant', data.explanation);
                } else if (!data.sql_query && !data.error) {
                    // Fallback if nothing happened
                    addMessage('assistant', "I couldn't generate a query for that.");
                }
                console.log("Success handling complete.");
            }

        } catch (err: any) {
            console.error("Error in handleRunAI:", err);
            addMessage('assistant', `Error: ${err.message}`);
        } finally {
            console.log("Setting executing to false");
            setExecuting(false);
            console.log("Execution state cleared");
        }
    };

    const handleRunSql = async () => {
        if (!activeDbId) return alert("No database selected");

        let sqlToRun = currentSql;
        if (editorRef.current) {
            const selection = editorRef.current.getSelection();
            const selectedText = editorRef.current.getModel().getValueInRange(selection);
            if (selectedText && selectedText.trim().length > 0) {
                sqlToRun = selectedText;
            }
        }

        if (!sqlToRun) return alert("No SQL query to run");

        setExecuting(true);
        // Clear previous results
        setResult(null);

        try {
            let res;

            if (approvedRequestId && sqlToRun === approvedSql) {
                // Execute Approved Request ONLY if text matches exactly
                res = await api.post(`/query-requests/${approvedRequestId}/execute`);
            } else {
                if (approvedRequestId) {
                    addMessage('assistant', 'Running modified/selected text as normal query.');
                }
                // Normal Execution
                res = await api.post('/query/run', {
                    connection_id: activeDbId,
                    sql_query: sqlToRun
                });
            }

            const data = res.data;

            if (data.error) {
                setResult({ columns: [], rows: [], error: data.error });
            } else if (data.result) {
                setResult(data.result);
                addMessage('assistant', approvedRequestId
                    ? `✅ Approved request #${approvedRequestId} executed successfully.`
                    : "Query executed successfully.");

                // If it was an approved request, we might want to refresh the state or redirect?
                // For now just stay here.
                if (approvedRequestId) {
                    setApprovedRequestId(null); // Clear it so next run is normal (if they edit user query)
                    // But wait, if they didn't edit, running again as normal user might fail if it's DELETE.
                    // That's fine, normal checks apply.
                }
            }

        } catch (err: any) {
            console.error("Execution error:", err);
            const errorMsg = err.response?.data?.detail || err.message || "Unknown error occurred";
            setResult({ columns: [], rows: [], error: errorMsg });
            addMessage('assistant', `❌ Execution Failed: ${errorMsg}`);
        } finally {
            setExecuting(false);
        }
    };

    // Export and Copy Functions
    const handleExport = (format: 'csv' | 'excel' | 'txt') => {
        if (!result || !result.rows || result.rows.length === 0) return alert("No results to export");

        const headers = result.columns;
        const rows = result.rows;

        if (format === 'excel') {
            // Dynamic import to avoid SSR issues if any, though client component is fine
            import('xlsx').then(XLSX => {
                const worksheet = XLSX.utils.json_to_sheet(rows); // detailed rows map? 
                // json_to_sheet uses keys as headers. result.rows likely keyed by column name?
                // Let's verify result data structure: { columns: ['id'], rows: [{'id': 1}, ...] }
                // Yes, mostly likely.

                const workbook = XLSX.utils.book_new();
                XLSX.utils.book_append_sheet(workbook, worksheet, "Results");
                XLSX.writeFile(workbook, `query_results_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.xlsx`);
            });
            return;
        }

        let content = "";
        let mimeType = "text/plain";
        let extension = "txt";

        if (format === 'csv') {
            const separator = ",";
            const headerRow = headers.join(separator);
            const dataRows = rows.map((row: any) =>
                headers.map((col: any) => {
                    const val = row[col];
                    if (typeof val === 'string' && val.includes(',')) return `"${val}"`;
                    return val;
                }).join(separator)
            ).join("\n");

            content = `${headerRow}\n${dataRows}`;
            mimeType = "text/csv";
            extension = 'csv';
        } else {
            // TXT
            const separator = "\t";
            const headerRow = headers.join(separator);
            const dataRows = rows.map((row: any) => headers.map((col: any) => row[col]).join(separator)).join("\n");
            content = `${headerRow}\n${dataRows}`;
        }

        const blob = new Blob([content], { type: mimeType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `query_results_${new Date().toISOString().slice(0, 19).replace(/:/g, '-')}.${extension}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    };

    const handleCopyTable = async () => {
        if (!result || !result.rows || result.rows.length === 0) return alert("No results to copy");

        const headers = result.columns;
        const rows = result.rows;
        const separator = "\t"; // TSV is best for pasting into Excel/Sheets

        const headerRow = headers.join(separator);
        const dataRows = rows.map((row: any) => headers.map((col: any) => row[col]).join(separator)).join("\n");
        const content = `${headerRow}\n${dataRows}`;

        try {
            await navigator.clipboard.writeText(content);
            alert("Table copied to clipboard! You can paste it into Excel or Google Sheets.");
        } catch (err) {
            console.error("Failed to copy:", err);
            alert("Failed to copy table.");
        }
    };

    return (
        <div className="h-screen flex flex-col bg-zinc-50 overflow-hidden">
            <Navbar />

            {/* Resizable Main Layout */}
            <ResizablePanelGroup direction="horizontal" className="flex-1 overflow-hidden" id="main-layout-group">
                {/* ... Sidebar ... */}
                {/* (Keeping existing layout code structure implicitly via context of replace) */}
                {/* I will only replace the surrounding block if I had access to full file, but here I am inserting functions. 
                    Wait, replace_file_content replaces a block.
                    The current tool call targets line 280 which is inside return().
                    I must insert the functions BEFORE return() and then update the JSX.
                    
                    I will split this into two edits or ONE large replacement covering from 'const handleRunSql...' to the 'Results' header.
                    
                    Let's look at lines 128-280. That's a huge block.
                    
                    Better strategy: 
                    1. Insert functions after 'handleRunSql' (around line 156).
                    2. Update the 'Results' header (around line 280).
                */}


                {/* 1. Sidebar Panel */}
                {isSidebarOpen && (
                    <>
                        <ResizablePanel
                            id="sidebar-panel"
                            defaultSize={20}
                            minSize="200px"
                            className="bg-white border-r flex flex-col"
                        >
                            <div className="p-3 border-b flex justify-between items-center bg-zinc-50">
                                <div className="flex gap-2">
                                    <Button
                                        variant={sidebarTab === 'schema' ? 'secondary' : 'ghost'}
                                        size="sm"
                                        className="h-8 text-xs px-2"
                                        onClick={() => setSidebarTab('schema')}
                                    >
                                        Schema
                                    </Button>
                                    <Button
                                        variant={sidebarTab === 'history' ? 'secondary' : 'ghost'}
                                        size="sm"
                                        className="h-8 text-xs px-2"
                                        onClick={() => setSidebarTab('history')}
                                    >
                                        History
                                    </Button>
                                </div>
                                <Button variant="ghost" size="icon" onClick={toggleSidebar}>
                                    <SidebarClose className="h-4 w-4 text-zinc-500" />
                                </Button>
                            </div>
                            <div className="flex-1 flex flex-col overflow-hidden">
                                {sidebarTab === 'schema' ? (
                                    <SchemaExplorer connectionId={dbId ? parseInt(dbId) : null} />
                                ) : (
                                    <QueryHistoryPanel onReplay={handleRunAI} />
                                )}
                            </div>
                        </ResizablePanel>
                        <ResizableHandle />
                    </>
                )}

                {!isSidebarOpen && (
                    <div className="border-r bg-white py-4 flex flex-col items-center gap-4 w-12 bg-zinc-50">
                        <Button variant="ghost" size="icon" onClick={toggleSidebar} title="Open Sidebar">
                            <SidebarOpen className="h-4 w-4 text-zinc-500" />
                        </Button>
                    </div>
                )}

                {/* 2. Main Content Area */}
                <ResizablePanel id="content-panel" defaultSize={80}>
                    <ResizablePanelGroup direction="horizontal" id="content-group">

                        {/* Chat Panel (AI Assistant) */}
                        <ResizablePanel
                            id="chat-panel"
                            defaultSize={25}
                            minSize="300px"
                            className="bg-white border-r flex flex-col"
                        >
                            <ChatPanel onSendMessage={handleRunAI} loading={isExecuting} />
                        </ResizablePanel>

                        <ResizableHandle />

                        {/* Center Workspace (SQL & Results) */}
                        <ResizablePanel id="workspace-panel" defaultSize={50}>
                            <ResizablePanelGroup direction="vertical" id="workspace-group">
                                {/* SQL Editor (Dev Mode Only) */}
                                {developerMode && (
                                    <>
                                        <ResizablePanel
                                            id="sql-editor-panel"
                                            defaultSize={40}
                                            minSize="150px"
                                            className="bg-white flex flex-col border-b"
                                        >
                                            <div className="flex justify-between items-center px-4 py-2 border-b bg-zinc-50">
                                                <span className="text-xs font-semibold uppercase text-zinc-500 flex items-center gap-2">
                                                    <Play className="h-3 w-3" /> SQL Editor
                                                </span>
                                                <div className="flex gap-2">
                                                    <Button size="sm" variant="secondary" className="h-7 text-xs">Format</Button>
                                                    <Button
                                                        size="sm"
                                                        className="h-7 text-xs bg-green-600 hover:bg-green-700 text-white"
                                                        onClick={handleRunSql}
                                                        disabled={isExecuting}
                                                    >
                                                        {isExecuting && <Loader2 className="mr-2 h-3 w-3 animate-spin" />}
                                                        Run Query
                                                    </Button>
                                                </div>
                                            </div>
                                            <div className="flex-1 overflow-hidden relative">
                                                <CodeEditor
                                                    value={currentSql}
                                                    onChange={(val) => setCurrentSql(val || '')}
                                                    language="sql"
                                                    onMount={handleEditorDidMount}
                                                />
                                            </div>
                                        </ResizablePanel>
                                        <ResizableHandle withHandle />
                                    </>
                                )}

                                {/* Results Table */}
                                <ResizablePanel
                                    id="results-panel"
                                    defaultSize={developerMode ? 60 : 100}
                                    minSize="200px"
                                    className="bg-white flex flex-col"
                                >
                                    <div className="px-4 py-2 border-b font-semibold text-sm bg-zinc-50 flex justify-between items-center h-[53px] relative z-0">
                                        <span>Results</span>
                                        <div className="flex gap-1">
                                            <Button
                                                variant="outline"
                                                size="sm"
                                                className="h-7 text-xs px-2 flex gap-1"
                                                onClick={() => handleCopyTable()}
                                                title="Copy as Table (Tab Separated)"
                                            >
                                                <ClipboardCopy className="h-3 w-3" /> Copy Table
                                            </Button>
                                            <div className="h-4 w-px bg-zinc-300 mx-1 self-center" />
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                className="h-7 w-7 p-0"
                                                onClick={() => handleExport('csv')}
                                                title="Export as CSV"
                                            >
                                                <span className="font-bold text-[10px]">CSV</span>
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                className="h-7 w-7 p-0"
                                                onClick={() => handleExport('excel')}
                                                title="Export for Excel"
                                            >
                                                <FileSpreadsheet className="h-3.5 w-3.5" />
                                            </Button>
                                            <Button
                                                variant="ghost"
                                                size="sm"
                                                className="h-7 w-7 p-0"
                                                onClick={() => handleExport('txt')}
                                                title="Export as TXT"
                                            >
                                                <FileText className="h-3.5 w-3.5" />
                                            </Button>
                                        </div>
                                    </div>
                                    <div className="flex-1 overflow-auto p-2">
                                        {result ? (
                                            <ResultTable data={result} />
                                        ) : (
                                            <div className="h-full flex items-center justify-center text-zinc-400 text-sm italic">
                                                Run a query to see results
                                            </div>
                                        )}
                                    </div>
                                </ResizablePanel>
                            </ResizablePanelGroup>
                        </ResizablePanel>

                        <ResizableHandle />

                        {/* Right Panel (Insights) */}
                        <ResizablePanel
                            id="insights-panel"
                            defaultSize={25}
                            minSize="250px"
                            className="bg-white border-l"
                        >
                            <ScrollArea className="h-full">
                                <div className="flex flex-col h-full bg-white">
                                    <QueryInsightsPanel
                                        insights={generatedPlan?.insights || null}
                                        impact={generatedPlan?.impact || null}
                                    />
                                </div>
                            </ScrollArea>
                        </ResizablePanel>

                    </ResizablePanelGroup>
                </ResizablePanel>

            </ResizablePanelGroup>

            {/* Approval Dialog */}
            {approvalData && (
                <ApprovalRequestDialog
                    open={approvalDialogOpen}
                    onClose={() => setApprovalDialogOpen(false)}
                    approvalId={approvalData.approvalId}
                    sqlQuery={approvalData.sqlQuery}
                    impact={approvalData.impact}
                />
            )}

            {/* Ambiguity Dialog */}
            <TableDisambiguationDialog
                open={ambiguityOpen}
                onClose={() => setAmbiguityOpen(false)}
                options={ambiguityOptions}
                onRetry={() => { }} // Retry logic handled by user rephrasing for now
            />
        </div>
    );
}
