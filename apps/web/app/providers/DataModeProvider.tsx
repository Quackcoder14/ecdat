'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

export type DataMode = 'simulation' | 'demo';

interface DataModeContextType {
  mode: DataMode;
  setMode: (mode: DataMode) => void;
}

const DataModeContext = createContext<DataModeContextType | undefined>(undefined);

export function DataModeProvider({ children }: { children: ReactNode }) {
  const [mode, setMode] = useState<DataMode>('simulation');

  useEffect(() => {
    // Load from localStorage on client side
    const stored = localStorage.getItem('ecdat-data-mode');
    if (stored === 'simulation' || stored === 'demo') {
      setMode(stored);
    }
  }, []);

  const setModeWithPersistence = (newMode: DataMode) => {
    setMode(newMode);
    localStorage.setItem('ecdat-data-mode', newMode);
  };

  return (
    <DataModeContext.Provider value={{ mode, setMode: setModeWithPersistence }}>
      {children}
    </DataModeContext.Provider>
  );
}

export function useDataMode() {
  const context = useContext(DataModeContext);
  if (!context) {
    throw new Error('useDataMode must be used within a DataModeProvider');
  }
  return context;
}