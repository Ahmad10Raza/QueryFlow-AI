'use client';

import React from 'react';
import Editor, { OnMount } from '@monaco-editor/react';

interface CodeEditorProps {
    value: string;
    onChange: (value: string | undefined) => void;
    language?: string;
}

const CodeEditor: React.FC<CodeEditorProps> = ({ value, onChange, language = "sql" }) => {
    return (
        <div className="h-full w-full border rounded-md overflow-hidden">
            <Editor
                height="100%"
                defaultLanguage={language}
                language={language}
                value={value}
                onChange={onChange}
                theme="vs-dark"
                options={{
                    minimap: { enabled: false },
                    fontSize: 14,
                    scrollBeyondLastLine: false,
                }}
            />
        </div>
    );
};

export default CodeEditor;
