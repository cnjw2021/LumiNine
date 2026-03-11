'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import api from '@/utils/api';
import { AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios';

// ── 상수 ────────────────────────────────────────────

const PUBLIC_PATHS = ['/', '/login', '/register', '/forgot-password'];
const PUBLIC_PATH_PREFIXES = ['/about/'];

/** 管理者に自動付与される基本権限（DRY: checkPermission / checkPermissions 共有） */
const ADMIN_BASIC_PERMISSIONS = ['user_view', 'user_create', 'user_edit', 'user_delete'];

// ── 型定義 ──────────────────────────────────────────

interface AuthContextType {
  isLoggedIn: boolean;
  isAdmin: boolean;
  isSuperuser: boolean;
  isLoading: boolean;
  token: string | null;
  userName: string | null;
  setIsLoading: (status: boolean) => void;
  setLoginStatus: (status: boolean, newToken?: string, refreshToken?: string) => void;
  setIsLoggedIn: (status: boolean) => void;
  logout: () => void;
  checkAdminStatus: () => Promise<void>;
  checkPermission: (permissionCode: string) => Promise<boolean>;
  checkPermissions: (permissionCodes: string[]) => Promise<Record<string, boolean>>;
  clearPermissionCache: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// ── Provider ────────────────────────────────────────

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const [isAdmin, setIsAdmin] = useState<boolean>(false);
  const [isSuperuser, setIsSuperuser] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [token, setToken] = useState<string | null>(null);
  const [userName, setUserName] = useState<string | null>(null);
  const [permissionCache, setPermissionCache] = useState<Record<string, boolean>>({});

  // ── Interceptors (useEffect 内で登録 → cleanup で解除) ──

  useEffect(() => {
    const reqInterceptor = api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
      config.headers = config.headers || {};
      config.headers['Cache-Control'] = 'no-cache';
      config.headers['Pragma'] = 'no-cache';
      config.headers['Expires'] = '0';
      return config;
    });

    return () => {
      api.interceptors.request.eject(reqInterceptor);
    };
  }, []);

  useEffect(() => {
    const resInterceptor = api.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error: AxiosError) => {
        if (error.response?.status === 403) {
          router.replace('/');
          return Promise.reject(error);
        }
        return Promise.reject(error);
      }
    );

    return () => {
      api.interceptors.response.eject(resInterceptor);
    };
  }, [router]);

  // ── Auth State ────────────────────────────────────

  const clearPermissionCache = useCallback(() => {
    setPermissionCache({});
  }, []);

  const clearAuthState = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    setToken(null);
    setIsLoggedIn(false);
    setIsAdmin(false);
    setIsSuperuser(false);
    setUserName(null);
    clearPermissionCache();
  }, [clearPermissionCache]);

  const logout = useCallback(async () => {
    try {
      clearAuthState();
      await api.post('/auth/logout').catch(() => { });
    } finally {
      window.location.href = '/login';
    }
  }, [clearAuthState]);

  const setLoginStatus = (status: boolean, newToken?: string, refreshToken?: string) => {
    setIsLoggedIn(status);

    if (status && newToken) {
      localStorage.setItem('token', newToken);
      setToken(newToken);

      if (refreshToken) {
        localStorage.setItem('refresh_token', refreshToken);
      }

      clearPermissionCache();
    } else {
      clearAuthState();
    }
  };

  // ── Admin Status ──────────────────────────────────

  const checkAdminStatus = useCallback(async () => {
    try {
      const storedToken = localStorage.getItem('token');

      if (!storedToken) {
        setIsAdmin(false);
        setIsSuperuser(false);
        return;
      }

      const response = await api.get('/auth/admin-status', {
        headers: { Authorization: `Bearer ${storedToken}` }
      });
      setIsAdmin(response.data.is_admin);
      setIsSuperuser(response.data.is_superuser);

      if (isAdmin !== response.data.is_admin || isSuperuser !== response.data.is_superuser) {
        clearPermissionCache();
      }
    } catch (error) {
      console.error('Error checking admin status:', error);
      setIsAdmin(false);
      setIsSuperuser(false);
    }
  }, [isAdmin, isSuperuser, clearPermissionCache]);

  // ── Permission Check ──────────────────────────────

  const checkPermissions = useCallback(async (permissionCodes: string[]): Promise<Record<string, boolean>> => {
    try {
      // スーパーユーザーは全ての権限を持つ
      if (isSuperuser) {
        const result: Record<string, boolean> = {};
        permissionCodes.forEach(code => {
          result[code] = true;
          setPermissionCache(prev => ({ ...prev, [code]: true }));
        });
        return result;
      }

      // 管理者の場合、基本権限を自動付与
      if (isAdmin) {
        const results: Record<string, boolean> = {};

        try {
          const response = await api.post('/auth/permissions/check-multiple', {
            permission_codes: permissionCodes
          });

          if (response.data && response.data.permissions) {
            permissionCodes.forEach(code => {
              results[code] = ADMIN_BASIC_PERMISSIONS.includes(code) || !!response.data.permissions[code];
              setPermissionCache(prev => ({ ...prev, [code]: results[code] }));
            });
          }
        } catch {
          permissionCodes.forEach(code => {
            results[code] = ADMIN_BASIC_PERMISSIONS.includes(code);
            setPermissionCache(prev => ({ ...prev, [code]: results[code] }));
          });
        }

        return results;
      }

      // 一般ユーザーの場合はAPIで確認
      const response = await api.post('/auth/permissions/check-multiple', {
        permission_codes: permissionCodes
      });

      if (response.data && response.data.permissions) {
        const permissions = response.data.permissions;
        Object.entries(permissions).forEach(([code, hasPermission]) => {
          setPermissionCache(prev => ({ ...prev, [code]: !!hasPermission }));
        });
        return permissions;
      }

      return {};
    } catch {
      return {};
    }
  }, [isSuperuser, isAdmin, setPermissionCache]);

  const checkPermission = useCallback(async (permissionCode: string): Promise<boolean> => {
    try {
      if (isSuperuser) return true;

      if (isAdmin && ADMIN_BASIC_PERMISSIONS.includes(permissionCode)) {
        return true;
      }

      if (permissionCache[permissionCode] !== undefined) {
        return permissionCache[permissionCode];
      }

      const response = await api.post('/permissions/check', {
        permission_code: permissionCode
      });

      const hasPermission = response.data.has_permission === true;
      setPermissionCache(prev => ({ ...prev, [permissionCode]: hasPermission }));

      return hasPermission;
    } catch {
      return false;
    }
  }, [isAdmin, isSuperuser, permissionCache]);

  // ── Effects ───────────────────────────────────────

  // ログイン状態が変わったらパーミッションキャッシュをクリア
  useEffect(() => {
    if (isLoggedIn) {
      clearPermissionCache();
    }
  }, [isLoggedIn, clearPermissionCache]);

  // 初期化
  useEffect(() => {
    const initialize = async () => {
      try {
        const token = localStorage.getItem('token');
        if (token) {
          setToken(token);
          const response = await api.get('/auth/me');
          if (response.data) {
            setIsLoggedIn(true);
            setIsAdmin(response.data.is_admin);
            setIsSuperuser(response.data.is_superuser);
            const name = response.data.full_name || response.data.name || response.data.email || null;
            setUserName(name);
          }
        }
      } catch (error) {
        console.error('Error initializing auth:', error);
        clearAuthState();
      } finally {
        setIsLoading(false);
      }
    };

    initialize();
  }, [clearAuthState]);

  // 非公開ページへのアクセス制御
  useEffect(() => {
    if (!isLoading && !isLoggedIn && pathname && !PUBLIC_PATHS.includes(pathname) && !PUBLIC_PATH_PREFIXES.some(prefix => pathname.startsWith(prefix))) {
      router.replace('/login');
    }
  }, [isLoading, isLoggedIn, pathname, router]);

  // ── Render ────────────────────────────────────────

  return (
    <AuthContext.Provider value={{
      isLoggedIn,
      isAdmin,
      isSuperuser,
      isLoading,
      token,
      userName,
      setIsLoading,
      setLoginStatus,
      setIsLoggedIn,
      logout,
      checkAdminStatus,
      checkPermission,
      checkPermissions,
      clearPermissionCache,
    }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}