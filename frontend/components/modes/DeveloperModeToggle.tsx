"use client";

import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Code2 } from "lucide-react";
import { useUIStore } from "@/store/uiStore";

export function DeveloperModeToggle() {
    const { developerMode, toggleDeveloperMode } = useUIStore();

    return (
        <div className="flex items-center space-x-2">
            <Code2 className="h-4 w-4 text-muted-foreground" />
            <Label htmlFor="developer-mode" className="text-sm cursor-pointer">
                Developer Mode
            </Label>
            <Switch
                id="developer-mode"
                checked={developerMode}
                onCheckedChange={toggleDeveloperMode}
            />
        </div>
    );
}
