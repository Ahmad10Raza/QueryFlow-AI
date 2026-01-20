import React, { useState, useRef, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Send, User, Bot, Trash2 } from "lucide-react";
import { useQueryStore } from '@/store/queryStore';
import { CodeBlock } from '@/components/ui/code-block';
import { parseMarkdown } from '@/lib/markdown-parser';

interface ChatPanelProps {
    onSendMessage: (message: string) => void;
    loading: boolean;
}

export function ChatPanel({ onSendMessage, loading }: ChatPanelProps) {
    const { messages, clearSession } = useQueryStore();
    const [input, setInput] = useState("");
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [messages]);

    const handleSend = () => {
        if (!input.trim() || loading) return;
        onSendMessage(input);
        setInput("");
    };

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    return (
        <div className="flex flex-col h-full bg-white border-l">
            <div className="p-3 border-b flex justify-between items-center bg-zinc-50">
                <span className="font-semibold text-sm">AI Assistant</span>
                <Button variant="ghost" size="icon" onClick={clearSession} title="Clear Context">
                    <Trash2 className="h-4 w-4 text-zinc-500" />
                </Button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-4" ref={scrollRef}>
                {messages.length === 0 && (
                    <div className="text-center text-zinc-400 text-sm mt-10">
                        Ask a question to start exploring your data.
                    </div>
                )}

                {messages.map((msg) => (
                    <div key={msg.id} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${msg.role === 'user' ? 'bg-blue-100' : 'bg-zinc-100'}`}>
                            {msg.role === 'user' ? <User className="h-4 w-4 text-blue-600" /> : <Bot className="h-4 w-4 text-zinc-600" />}
                        </div>
                        <div className={`rounded-lg text-sm max-w-[85%] ${msg.role === 'user' ? 'bg-blue-600 text-white p-3' : 'bg-zinc-100 text-zinc-800'}`}>
                            {msg.role === 'assistant' ? (
                                <div className="space-y-2">
                                    {parseMarkdown(msg.content).map((part, i) =>
                                        part.type === 'code' ? (
                                            <CodeBlock key={i} code={part.content} language={part.language} />
                                        ) : (
                                            <p key={i} className="p-3 whitespace-pre-wrap">{part.content}</p>
                                        )
                                    )}
                                </div>
                            ) : (
                                <span className="whitespace-pre-wrap">{msg.content}</span>
                            )}
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="flex gap-3">
                        <div className="w-8 h-8 rounded-full bg-zinc-100 flex items-center justify-center">
                            <Bot className="h-4 w-4 text-zinc-600" />
                        </div>
                        <div className="bg-zinc-100 rounded-lg p-3">
                            <span className="animate-pulse">Thinking...</span>
                        </div>
                    </div>
                )}
            </div>

            <div className="p-3 border-t bg-white">
                <div className="flex gap-2 relative">
                    <textarea
                        className="flex-1 w-full rounded-md border border-zinc-200 bg-transparent px-3 py-2 text-sm shadow-sm placeholder:text-zinc-500 focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-blue-600 disabled:cursor-not-allowed disabled:opacity-50 resize-none min-h-[40px] max-h-[120px]"
                        placeholder="Type your question..."
                        rows={1}
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        onKeyDown={handleKeyDown}
                        disabled={loading}
                    />
                    <Button
                        size="icon"
                        className="absolute right-1 bottom-1 h-8 w-8"
                        onClick={handleSend}
                        disabled={!input.trim() || loading}
                    >
                        <Send className="h-4 w-4" />
                    </Button>
                </div>
            </div>
        </div>
    );
}
