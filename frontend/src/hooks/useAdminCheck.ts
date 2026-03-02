import { useState, useEffect } from 'react';
import api from '../utils/api';

export const useAdminCheck = () => {
  const [isAdmin, setIsAdmin] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const checkAdminStatus = async () => {
      try {
        const response = await api.get('/auth/admin-status');
        setIsAdmin(response.data.is_admin || response.data.is_superuser);
      } catch (error) {
        console.error('管理者権限チェックエラー:', error);
        setIsAdmin(false);
      } finally {
        setIsLoading(false);
      }
    };

    checkAdminStatus();
  }, []);

  return { isAdmin, isLoading };
}; 