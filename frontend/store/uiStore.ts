import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UIState {
    developerMode: boolean;
    toggleDeveloperMode: () => void;
    setDeveloperMode: (enabled: boolean) => void;
}

export const useUIStore = create<UIState>()(
    persist(
        (set) => ({
            developerMode: false,
            toggleDeveloperMode: () => set((state) => ({ developerMode: !state.developerMode })),
            setDeveloperMode: (enabled: boolean) => set({ developerMode: enabled }),
        }),
        {
            name: 'queryflow-ui-storage',
        }
    )
);
