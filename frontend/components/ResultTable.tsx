import React from 'react';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";

interface ResultTableProps {
    data: {
        columns?: string[];
        rows?: Record<string, any>[];
        error?: string;
    } | null;
}

const ResultTable: React.FC<ResultTableProps> = ({ data }) => {
    if (!data) return null;

    if (data.error) {
        return (
            <div className="p-4 text-sm text-red-600 bg-red-50 border border-red-200 rounded-md">
                <span className="font-semibold">Execution Error:</span> {data.error}
            </div>
        );
    }

    if (!data.columns || data.columns.length === 0) {
        return null;
    }

    return (
        <div className="border rounded-md overflow-hidden">
            <Table>
                <TableHeader>
                    <TableRow>
                        {data.columns.map((col) => (
                            <TableHead key={col}>{col}</TableHead>
                        ))}
                    </TableRow>
                </TableHeader>
                <TableBody>
                    {data.rows && data.columns && data.rows.map((row, idx) => (
                        <TableRow key={idx}>
                            {data.columns!.map((col) => (
                                <TableCell key={`${idx}-${col}`}>
                                    {row[col] !== null ? String(row[col]) : <span className="text-zinc-400">null</span>}
                                </TableCell>
                            ))}
                        </TableRow>
                    ))}
                    {(!data.rows || data.rows.length === 0) && (
                        <TableRow>
                            <TableCell colSpan={data.columns ? data.columns.length : 1} className="text-center h-24 text-zinc-500">
                                No results found.
                            </TableCell>
                        </TableRow>
                    )}
                </TableBody>
            </Table>
        </div>
    );
};

export default ResultTable;
