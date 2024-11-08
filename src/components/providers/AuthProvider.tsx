// src/components/providers/AuthProvider.tsx
"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { fetchAuthSession, getCurrentUser, signIn, signOut } from 'aws-amplify/auth';

interface AuthContextType {
  isAuthenticated: boolean;
  isLoading: boolean;
  user: any;  // You can type this more specifically based on your needs
  error: Error | null;
}

const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
  isLoading: true,
  user: null,
  error: null
});

export function useAuth() {
  return useContext(AuthContext);
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    checkAuth();
  }, []);

  async function checkAuth() {
    try {
      const user = await getCurrentUser();
      setUser(user);
      setIsAuthenticated(true);
    } catch (err) {
      setError(err as Error);
      setIsAuthenticated(false);
    } finally {
      setIsLoading(false);
    }
  }

  const value = {
    isAuthenticated,
    isLoading,
    user,
    error
  };

  if (isLoading) {
    return null; // or a loading spinner
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}