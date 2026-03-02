'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import api from '@/utils/api';
import { AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios';

interface Permission {
  id: number;
  code: string;
  name: string;
  description: string | null;
  category: string;
}

interface AuthContextType {
  isLoggedIn: boolean;
  isAdmin: boolean;
  isSuperuser: boolean;
  isLoading: boolean;
  token: string | null;
  setIsLoading: (status: boolean) => void;
  setLoginStatus: (status: boolean, newToken?: string, refreshToken?: string) => void;
  setIsLoggedIn: (status: boolean) => void;
  logout: () => void;
  checkAdminStatus: () => Promise<void>;
  checkPermission: (permissionCode: string) => Promise<boolean>;
  checkPermissions: (permissionCodes: string[]) => Promise<Record<string, boolean>>;
  clearPermissionCache: () => void;
  allPermissions: Record<string, Permission[]>;
  userPermissions: Record<string, Permission[]>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const PUBLIC_PATHS = ['/login', '/register', '/forgot-password'];

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false);
  const [isAdmin, setIsAdmin] = useState<boolean>(false);
  const [isSuperuser, setIsSuperuser] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [token, setToken] = useState<string | null>(null);
  const [permissionCache, setPermissionCache] = useState<Record<string, boolean>>({});
  const [allPermissions, setAllPermissions] = useState<Record<string, Permission[]>>({});
  const [userPermissions, setUserPermissions] = useState<Record<string, Permission[]>>({});

  // キャッシュ制御のためのヘッダー設定
  api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
    config.headers = config.headers || {};
    config.headers['Cache-Control'] = 'no-cache';
    config.headers['Pragma'] = 'no-cache';
    config.headers['Expires'] = '0';
    return config;
  });

  // レスポンスインターセプターの設定
  useEffect(() => {
    const interceptor = api.interceptors.response.use(
      (response: AxiosResponse) => response,
      (error: AxiosError) => {
        // 403エラーの場合は新しい鑑定ページへリダイレクト
        if (error.response?.status === 403) {
          router.replace('/');
          return Promise.reject(error);
        }
        return Promise.reject(error);
      }
    );

    // クリーンアップ関数
    return () => {
      api.interceptors.response.eject(interceptor);
    };
  }, [router]);

  // 権限キャッシュをクリアする関数
  const clearPermissionCache = useCallback(() => {
    setPermissionCache({});
  }, []);

  // 認証状態をクリアする関数
  const clearAuthState = useCallback(() => {
    localStorage.removeItem('token');
    localStorage.removeItem('refresh_token');
    setToken(null);
    setIsLoggedIn(false);
    setIsAdmin(false);
    setIsSuperuser(false);
    clearPermissionCache();
  }, [clearPermissionCache]);

  const logout = useCallback(async () => {
    try {
      // ログアウトAPIを呼び出す前に状態をクリア
      clearAuthState();
      // APIエラーが発生してもログアウト処理は続行
      await api.post('/auth/logout').catch(() => {});
    } finally {
      // router.pushの代わりにwindow.location.hrefを使用して即時遷移
      window.location.href = '/login';
    }
  }, [clearAuthState]);

  // ログイン状態変更関数
  const setLoginStatus = (status: boolean, newToken?: string, refreshToken?: string) => {
    setIsLoggedIn(status);
    
    if (status && newToken) {
      localStorage.setItem('token', newToken);
      setToken(newToken);
      
      if (refreshToken) {
        localStorage.setItem('refresh_token', refreshToken);
      }
      
      // ログイン成功時に権限キャッシュをクリア
      clearPermissionCache();
    } else {
      clearAuthState();
    }
  };

  // 管理者ステータスチェック
  const checkAdminStatus = async () => {
    try {
      const storedToken = localStorage.getItem('token');
      
      if (!storedToken) {
        setIsAdmin(false);
        setIsSuperuser(false);
        return;
      }
      
      const response = await api.get('/auth/admin-status', {
        headers: {
          Authorization: `Bearer ${storedToken}`
        }
      });
      setIsAdmin(response.data.is_admin);
      setIsSuperuser(response.data.is_superuser);
      
      // 管理者ステータスが変更された場合、権限キャッシュをクリア
      if (isAdmin !== response.data.is_admin || isSuperuser !== response.data.is_superuser) {
        clearPermissionCache();
      }
    } catch (error) {
      console.error('Error checking admin status:', error);
      // エラー時は管理者権限なしとして扱う
      setIsAdmin(false);
      setIsSuperuser(false);
    }
  };

  // 権限定義とユーザー権限を取得
  const fetchPermissions = useCallback(async () => {
    try {
      // まずユーザー情報を取得
      const userResponse = await api.get('/auth/me');

      if (!userResponse?.data) {
        throw new Error('ユーザー情報の取得に失敗しました');
      }

      // ユーザーの権限を取得
      let hasPermissionManage = false;
      if (userResponse.data.id) {
        try {
          const userPermissionsResponse = await api.get(`/permissions/${userResponse.data.id}`);
          const permissions = userPermissionsResponse?.data?.permissions || {};
          setUserPermissions(permissions);
          
          // permission_manage権限を持っているか確認
          hasPermissionManage = Object.values(permissions as Record<string, Permission[]>).some(
            permissionList => permissionList.some(
              permission => permission.code === 'permission_manage'
            )
          );
        } catch (error) {
          if (error instanceof AxiosError && error.response?.status === 401) {
            throw error;
          }
          setUserPermissions({});
        }
      }

      // 権限定義を取得（スーパーユーザーまたはpermission_manage権限を持つ場合のみ）
      setAllPermissions({}); // デフォルトで空のオブジェクトを設定
      if (userResponse.data.is_superuser || hasPermissionManage) {
        try {
          const permissionsResponse = await api.get('/permissions');
          setAllPermissions(permissionsResponse?.data || {});
        } catch (error) {
          if (error instanceof AxiosError && error.response?.status === 401) {
            throw error;
          }
          // 403エラーなどその他のエラーは無視
        }
      }
    } catch (error: unknown) {
      if (error instanceof AxiosError && error.response?.status === 401) {
        clearAuthState();
        router.replace('/login');
        return;
      }
      throw error;
    }
  }, [clearAuthState, router]);

  // 複数の権限を一度にチェックする関数
  const checkPermissions = useCallback(async (permissionCodes: string[]): Promise<Record<string, boolean>> => {
    try {
      // スーパーユーザーは全ての権限を持つ
      if (isSuperuser) {
        const allPermissions: Record<string, boolean> = {};
        permissionCodes.forEach(code => {
          allPermissions[code] = true;
          setPermissionCache(prev => ({
            ...prev,
            [code]: true
          }));
        });
        return allPermissions;
      }
      
      // 管理者の場合、基本権限を自動付与
      if (isAdmin) {
        const adminBasicPermissions = ['user_view', 'user_create', 'user_edit', 'user_delete'];
        const results: Record<string, boolean> = {};
        
        try {
          // すべての権限をAPIで確認
          const response = await api.post('/auth/permissions/check-multiple', {
            permission_codes: permissionCodes
          });
          
          if (response.data && response.data.permissions) {
            // 各権限をチェック
            permissionCodes.forEach(code => {
              // 基本権限の場合は自動的にtrue
              if (adminBasicPermissions.includes(code)) {
                results[code] = true;
              } else {
                // その他の権限はAPIレスポンスの結果を使用
                results[code] = !!response.data.permissions[code];
              }
              // キャッシュを更新
              setPermissionCache(prev => ({
                ...prev,
                [code]: results[code]
              }));
            });
          }
        } catch {
          // エラー時は基本権限のみ設定し、その他はfalse
          permissionCodes.forEach(code => {
            results[code] = adminBasicPermissions.includes(code);
            setPermissionCache(prev => ({
              ...prev,
              [code]: results[code]
            }));
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
          setPermissionCache(prev => ({
            ...prev,
            [code]: !!hasPermission
          }));
        });
        return permissions;
      }
      
      return {};
    } catch {
      return {};
    }
  }, [isSuperuser, isAdmin, setPermissionCache]);

  // 単一の権限チェック
  const checkPermission = useCallback(async (permissionCode: string): Promise<boolean> => {
    try {
      if (isSuperuser) {
        return true;
      }
      
      if (isAdmin) {
        const adminBasicPermissions = ['user_view', 'user_create', 'user_edit', 'user_delete'];
        
        // 管理者の基本権限（ユーザー管理）のみを自動付与
        if (adminBasicPermissions.includes(permissionCode)) {
          return true;
        }
      }
      
      if (permissionCache[permissionCode] !== undefined) {
        return permissionCache[permissionCode];
      }
      
      const response = await api.post('/permissions/check', {
        permission_code: permissionCode
      });
      
      const hasPermission = response.data.has_permission === true;
      permissionCache[permissionCode] = hasPermission;
      
      return hasPermission;
    } catch {
      return false;
    }
  }, [isAdmin, isSuperuser, permissionCache]);

  // ログイン状態が変わったらパーミッションキャッシュをクリア
  useEffect(() => {
    if (isLoggedIn) {
      clearPermissionCache();
    }
  }, [isLoggedIn, clearPermissionCache]);

  // 初期化時に権限情報を取得
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
            await fetchPermissions();
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
  }, [fetchPermissions, clearAuthState]);

  // 非公開ページへのアクセス制御
  useEffect(() => {
    if (!isLoading && !isLoggedIn && pathname && !PUBLIC_PATHS.includes(pathname)) {
      router.replace('/login');
    }
  }, [isLoading, isLoggedIn, pathname, router]);

  return (
    <AuthContext.Provider value={{ 
      isLoggedIn,
      isAdmin,
      isSuperuser,
      isLoading,
      token,
      setIsLoading,
      setLoginStatus,
      setIsLoggedIn,
      logout,
      checkAdminStatus,
      checkPermission,
      checkPermissions,
      clearPermissionCache,
      allPermissions,
      userPermissions
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