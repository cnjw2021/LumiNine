'use client';

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/auth/AuthContext';

interface PermissionGuardProps {
  permissionCode: string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
  requireSuperuser?: boolean;
}

/**
 * 特定の権限を持つユーザーにのみコンテンツを表示するコンポーネント
 * @param permissionCode 必要な権限コード
 * @param children 権限がある場合に表示するコンテンツ
 * @param fallback 権限がない場合に表示する代替コンテンツ（省略可）
 * @param requireSuperuser スーパーユーザーのみアクセス可能にするかどうか（省略可）
 */
export function PermissionGuard({ permissionCode, children, fallback = null, requireSuperuser = false }: PermissionGuardProps) {
  const { checkPermission, isAdmin, isSuperuser } = useAuth();
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);

  // スーパーユーザーは常に全ての権限を持つ
  useEffect(() => {
    if (requireSuperuser && !isSuperuser) {
      setHasPermission(false);
      return;
    }

    if (isSuperuser) {
      setHasPermission(true);
      return;
    }

    // 管理者の基本権限の場合は、isAdminフラグで即時判断
    if (isAdmin && ['user_view', 'user_create', 'user_edit', 'user_delete'].includes(permissionCode)) {
      setHasPermission(true);
      return;
    }

    // それ以外の権限は非同期でチェック
    let isMounted = true;
    checkPermission(permissionCode).then(result => {
      if (isMounted) {
        setHasPermission(result);
      }
    });

    return () => {
      isMounted = false;
    };
  }, [permissionCode, checkPermission, isAdmin, isSuperuser, requireSuperuser]);

  // 権限チェック中は何も表示しない（ローディング表示なし）
  if (hasPermission === null) {
    return null;
  }

  return hasPermission ? <>{children}</> : <>{fallback}</>;
} 