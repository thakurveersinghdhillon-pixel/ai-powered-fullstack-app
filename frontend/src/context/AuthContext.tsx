"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import { User } from "@/lib/types";
import { api } from "@/lib/api";

interface AuthContextType {
  user: User | null;
  accessToken: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [accessToken, setAccessToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // Restore session on app load using HttpOnly refresh cookie
  useEffect(() => {
    let isMounted = true;
    const restoreSession = async () => {
      try {
        const tokenData = await api.refreshToken();
        if (tokenData && tokenData.access_token) {
          if (isMounted) setAccessToken(tokenData.access_token);
          const userData = await api.getMe(tokenData.access_token);
          if (isMounted) setUser(userData);
        }
      } catch (err) {
        if (isMounted) {
          setUser(null);
          setAccessToken(null);
        }
      } finally {
        if (isMounted) setIsLoading(false);
      }
    };
    restoreSession();

    return () => {
      isMounted = false;
    };
  }, []);

  const login = async (email: string, password: string) => {
    const tokenData = await api.login(email, password);
    setAccessToken(tokenData.access_token);
    const userData = await api.getMe(tokenData.access_token);
    setUser(userData);
  };

  const register = async (email: string, password: string) => {
    await api.register(email, password);
    await login(email, password);
  };

  const logout = async () => {
    try {
      await api.logout();
    } catch (err) {
      // Ignore logout errors
    } finally {
      setUser(null);
      setAccessToken(null);
    }
  };

  return (
    <AuthContext.Provider value={{ user, accessToken, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
