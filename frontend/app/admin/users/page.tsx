'use client';

import { useEffect, useState } from 'react';
import api from '@/lib/api';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Loader2, Shield, Ban, CheckCircle } from 'lucide-react';
import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";

interface User {
    user_id: number;
    email: string;
    is_active: boolean;
    is_superuser: boolean;
    role_name: string;
    created_at: string;
    last_login_at: string | null;
}

export default function AdminUsersPage() {
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchUsers = async () => {
        try {
            const res = await api.get('/admin/users/');
            // Filter out soft-deleted users
            const activeUsers = res.data.filter((u: User) => !u.email.startsWith('deleted_'));
            setUsers(activeUsers);
        } catch (error) {
            console.error("Failed to fetch users:", error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchUsers();
    }, []);

    const handleToggleStatus = async (user: User) => {
        if (!confirm(`Are you sure you want to ${user.is_active ? 'deactivate' : 'activate'} this user?`)) return;
        try {
            await api.put(`/admin/users/${user.user_id}/status`, {
                is_active: !user.is_active
            });
            fetchUsers();
        } catch (error) {
            alert("Failed to update status");
        }
    };


    const handleUpdateRole = async (userId: number, newRole: string) => {
        try {
            await api.put(`/admin/users/${userId}/role`, {
                role_name: newRole
            });
            fetchUsers();
        } catch (error) {
            alert("Failed to update role");
        }
    };

    const [createDialogOpen, setCreateDialogOpen] = useState(false);
    const [newUser, setNewUser] = useState({ email: '', password: '', role_name: 'USER' });

    const handleCreateUser = async () => {
        if (!newUser.email || !newUser.password) {
            return alert("Email and password are required");
        }
        try {
            await api.post('/admin/users/', newUser);
            setCreateDialogOpen(false);
            setNewUser({ email: '', password: '', role_name: 'USER' });
            fetchUsers();
        } catch (error: any) {
            alert(error.response?.data?.detail || "Failed to create user");
        }
    };

    const handleDeleteUser = async (userId: number, email: string) => {
        if (!confirm(`Are you sure you want to delete ${email}? This action cannot be undone.`)) return;
        try {
            await api.delete(`/admin/users/${userId}`);
            fetchUsers();
        } catch (error) {
            alert("Failed to delete user");
        }
    };

    if (loading) {
        return <div className="flex justify-center p-8"><Loader2 className="h-8 w-8 animate-spin text-zinc-400" /></div>;
    }

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-2xl font-bold tracking-tight">User Management</h1>
                    <p className="text-zinc-500">Manage user access and roles.</p>
                </div>
                <Dialog open={createDialogOpen} onOpenChange={setCreateDialogOpen}>
                    <DialogTrigger asChild>
                        <Button>Create User</Button>
                    </DialogTrigger>
                    <DialogContent>
                        <DialogHeader>
                            <DialogTitle>Create New User</DialogTitle>
                            <DialogDescription>
                                Add a new user to the platform.
                            </DialogDescription>
                        </DialogHeader>
                        <div className="grid gap-4 py-4">
                            <div className="grid gap-2">
                                <label className="text-sm font-medium">Email</label>
                                <input
                                    type="email"
                                    className="px-3 py-2 border rounded-md"
                                    value={newUser.email}
                                    onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                                    placeholder="user@example.com"
                                />
                            </div>
                            <div className="grid gap-2">
                                <label className="text-sm font-medium">Password</label>
                                <input
                                    type="password"
                                    className="px-3 py-2 border rounded-md"
                                    value={newUser.password}
                                    onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                                    placeholder="••••••••"
                                />
                            </div>
                            <div className="grid gap-2">
                                <label className="text-sm font-medium">Role</label>
                                <select
                                    className="px-3 py-2 border rounded-md"
                                    value={newUser.role_name}
                                    onChange={(e) => setNewUser({ ...newUser, role_name: e.target.value })}
                                >
                                    <option value="USER">USER</option>
                                    <option value="MANAGER">MANAGER</option>
                                    <option value="ADMIN">ADMIN</option>
                                    <option value="SUPER_ADMIN">SUPER_ADMIN</option>
                                </select>
                            </div>
                        </div>
                        <div className="flex justify-end gap-2">
                            <Button variant="outline" onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
                            <Button onClick={handleCreateUser}>Create</Button>
                        </div>
                    </DialogContent>
                </Dialog>
            </div>

            <div className="rounded-md border bg-white">
                <Table>
                    <TableHeader>
                        <TableRow>
                            <TableHead>Email</TableHead>
                            <TableHead>Role</TableHead>
                            <TableHead>Status</TableHead>
                            <TableHead>Last Login</TableHead>
                            <TableHead className="text-right">Actions</TableHead>
                        </TableRow>
                    </TableHeader>
                    <TableBody>
                        {users.map((user) => (
                            <TableRow key={user.user_id}>
                                <TableCell className="font-medium">{user.email}</TableCell>
                                <TableCell>
                                    <div className="flex items-center gap-2">
                                        <Badge
                                            variant={user.role_name === 'SUPER_ADMIN' ? 'default' : 'secondary'}
                                            className={user.role_name === 'SUPER_ADMIN' ? 'bg-indigo-600' : ''}
                                        >
                                            {user.role_name}
                                        </Badge>
                                        <Dialog>
                                            <DialogTrigger asChild>
                                                <Button variant="ghost" size="sm" className="h-6 w-6 p-0 text-zinc-400 hover:text-zinc-900">
                                                    <span className="sr-only">Edit Role</span>
                                                    ✎
                                                </Button>
                                            </DialogTrigger>
                                            <DialogContent>
                                                <DialogHeader>
                                                    <DialogTitle>Edit Role</DialogTitle>
                                                    <DialogDescription>
                                                        Change role for {user.email}.
                                                    </DialogDescription>
                                                </DialogHeader>
                                                <div className="grid gap-2 py-4">
                                                    {['USER', 'MANAGER', 'ADMIN', 'SUPER_ADMIN'].map((role) => (
                                                        <Button
                                                            key={role}
                                                            variant={user.role_name === role ? "default" : "outline"}
                                                            onClick={() => handleUpdateRole(user.user_id, role)}
                                                            className="justify-start"
                                                        >
                                                            {role}
                                                        </Button>
                                                    ))}
                                                </div>
                                            </DialogContent>
                                        </Dialog>
                                    </div>
                                </TableCell>
                                <TableCell>
                                    <div className="flex items-center gap-2">
                                        {user.is_active ? (
                                            <CheckCircle className="h-4 w-4 text-green-500" />
                                        ) : (
                                            <Ban className="h-4 w-4 text-red-500" />
                                        )}
                                        <span className="text-sm text-zinc-600">
                                            {user.is_active ? 'Active' : 'Disabled'}
                                        </span>
                                    </div>
                                </TableCell>
                                <TableCell className="text-zinc-500 text-sm">
                                    {user.last_login_at ? new Date(user.last_login_at).toLocaleDateString() : '-'}
                                </TableCell>
                                <TableCell className="text-right">
                                    <div className="flex justify-end gap-2">
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => handleToggleStatus(user)}
                                            className={user.is_active ? "text-red-600 hover:text-red-700 hover:bg-red-50" : "text-green-600 hover:text-green-700 hover:bg-green-50"}
                                        >
                                            {user.is_active ? 'Deactivate' : 'Activate'}
                                        </Button>
                                        <Button
                                            variant="ghost"
                                            size="sm"
                                            onClick={() => handleDeleteUser(user.user_id, user.email)}
                                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                        >
                                            Delete
                                        </Button>
                                    </div>
                                </TableCell>
                            </TableRow>
                        ))}
                    </TableBody>
                </Table>
            </div>
        </div>
    );
}
