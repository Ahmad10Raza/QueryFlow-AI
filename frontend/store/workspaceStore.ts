import { create } from 'zustand';

interface WorkspaceState {
    activeDbId: number | null;
    isSidebarOpen: boolean;
    activePanel: 'chat' | 'history' | 'schema';

    setActiveDbId: (id: number | null) => void;
    toggleSidebar: () => void;
    setActivePanel: (panel: 'chat' | 'history' | 'schema') => void;
}

export const useWorkspaceStore = create<WorkspaceState>((set) => ({
    activeDbId: null,
    isSidebarOpen: true,
    activePanel: 'chat',

    setActiveDbId: (id) => set({ activeDbId: id }),
    toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
    setActivePanel: (panel) => set({ activePanel: panel }),
}));
