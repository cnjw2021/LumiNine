'use client';

import React, { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import api from '@/utils/api';
import { AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios';

// ── 상수 ────────────────────────────────────────────

const PUBLIC_PATHS = ['/', '/login', '/register', '/forgot-password'];
const PUBLIC_PATH_PREFIXES = ['/about/'];

/** 管理者に自動付与される基本権限（DRY: checkPermission / checkPermissions 共有） */
export const ADMIN_BASIC_PERMISSIONS = ['user_view', 'user_create', 'user_edit', 'user_delete'];

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
  logout: () => Promise<void>;
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
  const permissionCacheRef = useRef<Record<string, boolean>>({});
  const cacheGenerationRef = useRef(0);

  // ref キャッシュを更新するヘルパー（generation チェックで stale write を防止）
  const updatePermissionCache = useCallback((entries: Record<string, boolean>, generation: number) => {
    // リクエスト開始時の generation と現在が一致する場合のみ書き込み
    if (generation === cacheGenerationRef.current) {
      permissionCacheRef.current = { ...permissionCacheRef.current, ...entries };
    }
  }, []);

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
    permissionCacheRef.current = {};
    cacheGenerationRef.current += 1;
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
    // token をスナップショットしてから状態をクリア（API側のログアウト処理を確実に実行）
    const currentToken = localStorage.getItem('token');
    try {
      if (currentToken) {
        await api.post('/auth/logout', {}, {
          headers: { Authorization: `Bearer ${currentToken}` }
        }).catch(() => { });
      }
    } finally {
      clearAuthState();
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
      clearPermissionCache();
    }
  }, [isAdmin, isSuperuser, clearPermissionCache]);

  // ── Permission Check ──────────────────────────────

  // 個別の権限チェックAPIを呼び出すヘルパー（エラーは throw → 呼び出し側で判別）
  const checkPermissionApi = useCallback(async (permissionCode: string): Promise<{ code: string; hasPermission: boolean }> => {
    const response = await api.post('/permissions/check', {
      permission_code: permissionCode
    });
    return { code: permissionCode, hasPermission: response.data.has_permission === true };
  }, []);

  const checkPermissions = useCallback(async (permissionCodes: string[]): Promise<Record<string, boolean>> => {
    try {
      // 未認証の場合は全て false
      if (!localStorage.getItem('token')) {
        const denied: Record<string, boolean> = {};
        permissionCodes.forEach(code => { denied[code] = false; });
        return denied;
      }

      // スーパーユーザーは全ての権限を持つ
      const gen = cacheGenerationRef.current;
      if (isSuperuser) {
        const allGranted: Record<string, boolean> = {};
        permissionCodes.forEach(code => { allGranted[code] = true; });
        updatePermissionCache(allGranted, gen);
        return allGranted;
      }

      // 重複コードを除去
      const uniqueCodes = [...new Set(permissionCodes)];

      // 全コードを false で初期化（rejected でも undefined にしない）
      const results: Record<string, boolean> = {};
      uniqueCodes.forEach(code => { results[code] = false; });

      // キャッシュ済みコードを short-circuit
      const cache = permissionCacheRef.current;
      const codesToCheck = uniqueCodes.filter(code => {
        // 管理者の基本権限は自動付与
        if (isAdmin && ADMIN_BASIC_PERMISSIONS.includes(code)) {
          results[code] = true;
          return false;
        }
        // キャッシュにあればAPIスキップ
        if (cache[code] !== undefined) {
          results[code] = cache[code];
          return false;
        }
        return true;
      });

      // 未キャッシュのコードのみAPIで確認
      if (codesToCheck.length > 0) {
        const apiResults = await Promise.allSettled(
          codesToCheck.map(code => checkPermissionApi(code))
        );

        // 成功した結果のみキャッシュに書き込む（失敗はfalse初期値のまま、キャッシュしない）
        const toCache: Record<string, boolean> = {};
        apiResults.forEach(result => {
          if (result.status === 'fulfilled') {
            results[result.value.code] = result.value.hasPermission;
            toCache[result.value.code] = result.value.hasPermission;
          }
        });

        if (Object.keys(toCache).length > 0) {
          updatePermissionCache(toCache, gen);
        }
      }

      return results;
    } catch {
      const fallback: Record<string, boolean> = {};
      permissionCodes.forEach(code => { fallback[code] = false; });
      return fallback;
    }
  }, [isSuperuser, isAdmin, checkPermissionApi, updatePermissionCache]);

  const checkPermission = useCallback(async (permissionCode: string): Promise<boolean> => {
    try {
      // 未認証の場合は即 false（ログアウト後のキャッシュ漏れ防止）
      if (!localStorage.getItem('token')) {
        return false;
      }

      const gen = cacheGenerationRef.current;

      if (isSuperuser) return true;

      if (isAdmin && ADMIN_BASIC_PERMISSIONS.includes(permissionCode)) {
        return true;
      }

      // useRefで最新のキャッシュを参照（依存配列に含めない → コールバック安定化）
      const cachedValue = permissionCacheRef.current[permissionCode];
      if (cachedValue !== undefined) {
        return cachedValue;
      }

      // checkPermissionApi を再利用して API 呼び出しを一元化
      const { hasPermission } = await checkPermissionApi(permissionCode);
      // 権限キャッシュ（ref）のみを更新
      updatePermissionCache({ [permissionCode]: hasPermission }, gen);

      return hasPermission;
    } catch {
      return false;
    }
  }, [isAdmin, isSuperuser, checkPermissionApi, updatePermissionCache]);

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