// src/components/providers/Providers.tsx
"use client";

import { ReactNode } from 'react';
import { AmplifyProvider } from './AmplifyProvider';
import { AuthProvider } from './AuthProvider';

interface ProvidersProps {
  children: ReactNode;
}

export function Providers({ children }: ProvidersProps) {
  return (
    <AmplifyProvider>
      <AuthProvider>
        {children}
      </AuthProvider>
    </AmplifyProvider>
  );
}