'use client';
import { useState, useEffect } from 'react';
import Navbar from '@/components/Navbar';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import api from '@/lib/api';

export default function AIModelSelectionPage() {
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [provider, setProvider] = useState('openai');
    const [model, setModel] = useState('');
    const [apiKey, setApiKey] = useState('');
    const [hasApiKey, setHasApiKey] = useState(false);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    useEffect(() => {
        fetchConfig();
    }, []);

    const fetchConfig = async () => {
        try {
            setLoading(true);
            const res = await api.get('/users/me/llm-config');
            if (res.data.llm_provider) setProvider(res.data.llm_provider);
            if (res.data.llm_model) setModel(res.data.llm_model);
            setHasApiKey(res.data.has_api_key);
        } catch (err: any) {
            setError("Failed to load settings");
        } finally {
            setLoading(false);
        }
    };

    const handleSave = async () => {
        setError('');
        setSuccess('');
        setSaving(true);
        try {
            await api.put('/users/me/llm-config', {
                llm_provider: provider,
                llm_model: model,
                llm_api_key: apiKey || undefined
            });
            setSuccess("Settings saved successfully.");
            setHasApiKey(data => apiKey ? true : data);
            setApiKey(''); // Clear input after save for security

            // Clear success message after 3 seconds
            setTimeout(() => setSuccess(''), 3000);
        } catch (err: any) {
            setError("Failed to save settings: " + (err.response?.data?.detail || err.message));
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="h-screen flex flex-col bg-zinc-50">
            <Navbar />
            <div className="flex-1 container mx-auto p-8 max-w-2xl">
                <Card>
                    <CardHeader>
                        <CardTitle>AI Model Configuration</CardTitle>
                        <CardDescription>Select the AI model you want to use for generating queries.</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-6">
                        {loading ? (
                            <div className="flex justify-center p-8">
                                <Loader2 className="h-8 w-8 animate-spin text-zinc-400" />
                            </div>
                        ) : (
                            <>
                                {error && (
                                    <div className="bg-red-50 text-red-600 p-3 rounded-md text-sm flex items-center gap-2">
                                        <AlertCircle className="h-4 w-4" /> {error}
                                    </div>
                                )}

                                {success && (
                                    <div className="bg-green-50 text-green-600 p-3 rounded-md text-sm flex items-center gap-2">
                                        <CheckCircle className="h-4 w-4" /> {success}
                                    </div>
                                )}

                                <div className="space-y-2">
                                    <Label>Provider</Label>
                                    <Select value={provider} onValueChange={setProvider}>
                                        <SelectTrigger>
                                            <SelectValue placeholder="Select Provider" />
                                        </SelectTrigger>
                                        <SelectContent>
                                            <SelectItem value="openai">OpenAI</SelectItem>
                                            <SelectItem value="gemini">Google Gemini</SelectItem>
                                            <SelectItem value="anthropic">Anthropic Claude</SelectItem>
                                            <SelectItem value="ollama">Ollama (Local)</SelectItem>
                                        </SelectContent>
                                    </Select>
                                </div>

                                <div className="space-y-2">
                                    <Label>Model Name</Label>
                                    <Input
                                        value={model}
                                        onChange={(e) => setModel(e.target.value)}
                                        placeholder={provider === 'openai' ? 'gpt-4o' : provider === 'gemini' ? 'gemini-1.5-flash' : 'llama3'}
                                    />
                                    <p className="text-xs text-zinc-500">
                                        Enter the specific model ID (e.g., gpt-4-turbo, claude-3-opus).
                                    </p>
                                </div>

                                <div className="space-y-2">
                                    <Label>API Key {hasApiKey && <span className="text-green-600 text-xs font-normal ml-2">(Current key set)</span>}</Label>
                                    <Input
                                        type="password"
                                        value={apiKey}
                                        onChange={(e) => setApiKey(e.target.value)}
                                        placeholder={hasApiKey ? "Leave blank to keep current key" : "sk-..."}
                                    />
                                </div>
                            </>
                        )}
                    </CardContent>
                    <CardFooter className="flex justify-end">
                        <Button onClick={handleSave} disabled={saving || loading}>
                            {saving && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            Save Changes
                        </Button>
                    </CardFooter>
                </Card>
            </div>
        </div>
    );
}
