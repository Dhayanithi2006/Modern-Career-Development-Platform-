"use client";

import { create } from "zustand";

type User = {
  id: number;
  email: string;
  full_name: string;
  role: string;
};

type AuthState = {
  accessToken: string | null;
  user: User | null;
  setAuth: (accessToken: string, user: User) => void;
  logout: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  accessToken: typeof window !== "undefined" ? localStorage.getItem("accessToken") : null,
  user: null,
  setAuth: (accessToken, user) => {
    localStorage.setItem("accessToken", accessToken);
    set({ accessToken, user });
  },
  logout: () => {
    localStorage.removeItem("accessToken");
    set({ accessToken: null, user: null });
  }
}));
