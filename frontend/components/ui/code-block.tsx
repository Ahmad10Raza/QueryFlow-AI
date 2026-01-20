'use client'

import { useState } from 'react'
import { Check, Copy } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface CodeBlockProps {
    code: string
    language?: string
}

export function CodeBlock({ code, language = 'sql' }: CodeBlockProps) {
    const [copied, setCopied] = useState(false)

    const handleCopy = async () => {
        await navigator.clipboard.writeText(code)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
    }

    return (
        <div className="relative group my-4 rounded-xl overflow-hidden border border-zinc-200 bg-white shadow-[0_8px_30px_rgb(0,0,0,0.12)] transition-shadow hover:shadow-[0_8px_30px_rgb(0,0,0,0.16)]">
            <div className="flex items-center justify-between bg-zinc-50 border-b border-zinc-100 px-4 py-2">
                <span className="text-xs font-semibold text-zinc-500 uppercase tracking-wide flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full bg-blue-500" />
                    {language}
                </span>
                <Button
                    variant="ghost"
                    size="sm"
                    onClick={handleCopy}
                    className="h-7 text-xs hover:bg-zinc-200 text-zinc-500 hover:text-zinc-800 transition-colors"
                >
                    {copied ? (
                        <>
                            <Check className="h-3 w-3 mr-1 text-green-600" /> <span className="text-green-600 font-medium">Copied</span>
                        </>
                    ) : (
                        <>
                            <Copy className="h-3 w-3 mr-1" /> Copy
                        </>
                    )}
                </Button>
            </div>
            <pre className="bg-white text-zinc-800 p-4 overflow-x-auto text-sm font-mono leading-relaxed selection:bg-blue-100 selection:text-blue-900 border-t border-zinc-50">
                <code>{code}</code>
            </pre>
        </div>
    )
}
