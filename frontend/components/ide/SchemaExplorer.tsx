'use client';
import { useState, useEffect } from 'react';
import { ChevronRight, ChevronDown, Database, Table, Eye, Key, Settings, Zap, Calendar, Loader2, FolderOpen, Folder } from 'lucide-react';
import api from '@/lib/api';

interface SchemaObject {
    name: string;
    column_count?: number;
    row_count?: number;
    table_name?: string;
    type?: string;
    status?: string;
}

interface DatabaseStructure {
    database_name: string;
    tables: SchemaObject[];
    views: SchemaObject[];
    indexes: SchemaObject[];
    procedures: SchemaObject[];
    triggers: SchemaObject[];
    events: SchemaObject[];
}

interface MultiDbSchemaResponse {
    is_multi_db: boolean;
    databases: DatabaseStructure[];
}

interface SchemaExplorerProps {
    connectionId: number | null;
}

export function SchemaExplorer({ connectionId }: SchemaExplorerProps) {
    const [data, setData] = useState<MultiDbSchemaResponse | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [expandedNodes, setExpandedNodes] = useState<Set<string>>(new Set());

    useEffect(() => {
        if (connectionId) {
            fetchSchema();
        }
    }, [connectionId]);

    const fetchSchema = async () => {
        if (!connectionId) return;

        setLoading(true);
        setError(null);
        try {
            const response = await api.get(`/schema_explorer/${connectionId}/structure`);
            const result = response.data;

            // Normalize response if it's the old single-db format
            if (!result.is_multi_db) {
                setData({
                    is_multi_db: true,
                    databases: [result]
                });
                // Expand the first database by default
                setExpandedNodes(new Set([result.database_name]));
            } else {
                setData(result);
                // Expand the first database by default if it exists
                if (result.databases.length > 0) {
                    setExpandedNodes(new Set([result.databases[0].database_name]));
                }
            }
        } catch (err: any) {
            setError(err.response?.data?.detail || 'Failed to load schema');
        } finally {
            setLoading(false);
        }
    };

    const toggleNode = (nodeId: string) => {
        const newExpanded = new Set(expandedNodes);
        if (newExpanded.has(nodeId)) {
            newExpanded.delete(nodeId);
        } else {
            newExpanded.add(nodeId);
        }
        setExpandedNodes(newExpanded);
    };

    const isExpanded = (nodeId: string) => expandedNodes.has(nodeId);

    if (!connectionId) {
        return (
            <div className="p-4 text-sm text-zinc-500">
                No database selected
            </div>
        );
    }

    if (loading) {
        return (
            <div className="p-4 flex items-center gap-2 text-sm text-zinc-500">
                <Loader2 className="h-4 w-4 animate-spin" />
                Loading schema...
            </div>
        );
    }

    if (error) {
        return (
            <div className="p-4 text-sm text-red-500">
                {error}
            </div>
        );
    }

    if (!data) return null;

    const renderObjectFolder = (dbName: string, title: string, objects: SchemaObject[], icon: any, colorClass: string, folderKey: string) => {
        if (objects.length === 0) return null;
        const nodeId = `${dbName}-${folderKey}`;
        const Icon = icon;

        return (
            <div key={nodeId}>
                <button
                    onClick={() => toggleNode(nodeId)}
                    className="w-full flex items-center gap-1 px-2 py-1 text-xs hover:bg-zinc-100 rounded"
                >
                    {isExpanded(nodeId) ? (
                        <ChevronDown className="h-3 w-3" />
                    ) : (
                        <ChevronRight className="h-3 w-3" />
                    )}
                    <Folder className="h-3.5 w-3.5 text-amber-500 fill-amber-500/20" />
                    <span className="font-medium text-zinc-700">{title}</span>
                    <span className="ml-auto text-[10px] text-zinc-400">({objects.length})</span>
                </button>
                {isExpanded(nodeId) && (
                    <div className="ml-5 space-y-0.5 border-l border-zinc-200 pl-1 mt-0.5">
                        {objects.map((obj, i) => (
                            <div
                                key={`${nodeId}-${obj.name}-${i}`}
                                className="flex items-center gap-1.5 px-2 py-0.5 text-xs hover:bg-zinc-100 rounded cursor-pointer group"
                            >
                                <Icon className={`h-3 w-3 ${colorClass}`} />
                                <span className="flex-1 truncate text-zinc-600 group-hover:text-zinc-900">{obj.name}</span>
                                {obj.column_count && (
                                    <span className="text-[10px] text-zinc-400">({obj.column_count})</span>
                                )}
                            </div>
                        ))}
                    </div>
                )}
            </div>
        );
    };

    return (
        <div className="h-full overflow-y-auto bg-white">
            <div className="p-2 space-y-1">
                {data.databases.map((db) => (
                    <div key={db.database_name}>
                        <button
                            onClick={() => toggleNode(db.database_name)}
                            className="w-full flex items-center gap-1 px-2 py-1.5 text-sm hover:bg-zinc-100 rounded"
                        >
                            {isExpanded(db.database_name) ? (
                                <ChevronDown className="h-4 w-4" />
                            ) : (
                                <ChevronRight className="h-4 w-4" />
                            )}
                            <Database className="h-4 w-4 text-blue-600 fill-blue-600/10" />
                            <span className="font-semibold text-zinc-800 truncate">{db.database_name}</span>
                        </button>

                        {isExpanded(db.database_name) && (
                            <div className="ml-4 space-y-1">
                                {renderObjectFolder(db.database_name, 'Tables', db.tables, Table, 'text-blue-500', 'tables')}
                                {renderObjectFolder(db.database_name, 'Views', db.views, Eye, 'text-purple-500', 'views')}
                                {renderObjectFolder(db.database_name, 'Indexes', db.indexes, Key, 'text-amber-500', 'indexes')}
                                {renderObjectFolder(db.database_name, 'Procedures', db.procedures, Settings, 'text-green-500', 'procedures')}
                                {renderObjectFolder(db.database_name, 'Triggers', db.triggers, Zap, 'text-red-500', 'triggers')}
                                {renderObjectFolder(db.database_name, 'Events', db.events, Calendar, 'text-indigo-500', 'events')}
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}
