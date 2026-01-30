'use client';
import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import api from '@/lib/api';

interface AddConnectionModalProps {
    onConnectionAdded: () => void;
}

export function AddConnectionModal({ onConnectionAdded }: AddConnectionModalProps) {
    const [open, setOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const [testing, setTesting] = useState(false);
    const [testResult, setTestResult] = useState<{ success: boolean; message: string } | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [formData, setFormData] = useState({
        name: '',
        db_type: 'postgres',
        host: 'localhost',
        port: 5432,
        username: '',
        password: '',
        database_name: ''
    });

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: name === 'port' ? parseInt(value) || 5432 : value
        }));
        setTestResult(null);
        setError(null);
    };

    const handleSelectChange = (value: string) => {
        const portMap: Record<string, number> = {
            'postgres': 5432,
            'mysql': 3306,
            'mongodb': 27017
        };
        setFormData(prev => ({
            ...prev,
            db_type: value,
            port: portMap[value] || 5432
        }));
        setTestResult(null);
        setError(null);
    };

    const handleTestConnection = async () => {
        setTesting(true);
        setTestResult(null);
        setError(null);
        try {
            const response = await api.post('/db_connections/test', formData);
            setTestResult(response.data);
        } catch (error: any) {
            setTestResult({
                success: false,
                message: error.response?.data?.detail || 'Connection test failed'
            });
        } finally {
            setTesting(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            await api.post('/db_connections/', formData);
            setOpen(false);
            onConnectionAdded();
            setFormData({
                name: '',
                db_type: 'postgres',
                host: 'localhost',
                port: 5432,
                username: '',
                password: '',
                database_name: ''
            });
            setTestResult(null);
        } catch (err: any) {
            const errorMsg = err.response?.data?.detail || 'Failed to add connection';
            setError(errorMsg);
        } finally {
            setLoading(false);
        }
    };

    return (
        <Dialog open={open} onOpenChange={setOpen}>
            <DialogTrigger asChild>
                <Button>Add Connection</Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[550px]">
                <DialogHeader>
                    <DialogTitle>Connect New Database</DialogTitle>
                </DialogHeader>
                <form onSubmit={handleSubmit} className="space-y-4 py-4">
                    <div className="space-y-2">
                        <Label htmlFor="name">Connection Name</Label>
                        <Input
                            id="name"
                            name="name"
                            value={formData.name}
                            onChange={handleChange}
                            placeholder="Production DB"
                            required
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="db_type">Database Type</Label>
                            <Select onValueChange={handleSelectChange} value={formData.db_type}>
                                <SelectTrigger>
                                    <SelectValue placeholder="Select type" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="postgres">PostgreSQL</SelectItem>
                                    <SelectItem value="mysql">MySQL</SelectItem>
                                    <SelectItem value="mongodb">MongoDB</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="port">Port</Label>
                            <Input
                                id="port"
                                name="port"
                                type="number"
                                value={formData.port}
                                onChange={handleChange}
                                required
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="host">Host</Label>
                            <Input
                                id="host"
                                name="host"
                                value={formData.host}
                                onChange={handleChange}
                                placeholder="localhost"
                                required
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="database_name">Database Name</Label>
                            <Input
                                id="database_name"
                                name="database_name"
                                value={formData.database_name}
                                onChange={handleChange}
                                required
                            />
                        </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                            <Label htmlFor="username">Username</Label>
                            <Input
                                id="username"
                                name="username"
                                value={formData.username}
                                onChange={handleChange}
                                required
                            />
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="password">Password</Label>
                            <Input
                                id="password"
                                name="password"
                                type="password"
                                value={formData.password}
                                onChange={handleChange}
                            />
                        </div>
                    </div>

                    {testResult && (
                        <Alert variant={testResult.success ? "default" : "destructive"}>
                            <div className="flex items-center gap-2">
                                {testResult.success ? (
                                    <CheckCircle2 className="h-5 w-5 text-green-600" />
                                ) : (
                                    <XCircle className="h-5 w-5" />
                                )}
                                <AlertDescription className="flex-1">
                                    {testResult.message}
                                </AlertDescription>
                            </div>
                        </Alert>
                    )}

                    {error && (
                        <Alert variant="destructive">
                            <div className="flex items-center gap-2">
                                <XCircle className="h-5 w-5" />
                                <AlertDescription className="flex-1">
                                    {error}
                                </AlertDescription>
                            </div>
                        </Alert>
                    )}

                    <div className="flex gap-3 justify-end pt-2">
                        <Button
                            type="button"
                            variant="outline"
                            onClick={handleTestConnection}
                            disabled={testing || loading}
                        >
                            {testing && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            Test Connection
                        </Button>
                        <Button type="submit" disabled={loading || testing}>
                            {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            Save Connection
                        </Button>
                    </div>
                </form>
            </DialogContent>
        </Dialog>
    );
}
