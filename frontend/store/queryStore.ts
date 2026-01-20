import { create } from 'zustand';
import { AIQueryResponse } from '@/lib/types';

interface Message {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: number;
}

interface QueryState {
    messages: Message[];
    currentSql: string;
    generatedPlan: AIQueryResponse | null;
    result: any | null;
    isExecuting: boolean;

    addMessage: (role: 'user' | 'assistant', content: string) => void;
    setCurrentSql: (sql: string) => void;
    setGeneratedPlan: (plan: AIQueryResponse | null) => void;
    setResult: (result: any) => void;
    setExecuting: (executing: boolean) => void;
    clearSession: () => void;
}

export const useQueryStore = create<QueryState>((set) => ({
    messages: [],
    currentSql: '',
    generatedPlan: null,
    result: null,
    isExecuting: false,

    addMessage: (role, content) => set((state) => ({
        messages: [...state.messages, {
            id: `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
            role,
            content,
            timestamp: Date.now()
        }]
    })),
    setCurrentSql: (sql) => set({ currentSql: sql }),
    setGeneratedPlan: (plan) => set({ generatedPlan: plan }),
    setResult: (result) => set({ result }),
    setExecuting: (executing) => set({ isExecuting: executing }),
    clearSession: () => set({ messages: [], currentSql: '', generatedPlan: null, result: null }),
}));
