import * as React from "react";

// シンプルなトースト通知のための型定義
export type ToastProps = {
  id: string;
  title?: React.ReactNode;
  description?: React.ReactNode;
  action?: React.ReactNode;
  open?: boolean;
  onOpenChange?: (open: boolean) => void;
  variant?: "default" | "destructive";
};

export type ToastActionElement = React.ReactElement;

// シンプルなトースト管理のためのカスタムフック
export function useToast() {
  const [toasts, setToasts] = React.useState<ToastProps[]>([]);

  const toast = React.useCallback(
    (props: Omit<ToastProps, "id">) => {
      const id = Math.random().toString(36).substring(2, 9);
      setToasts((prevToasts) => [...prevToasts, { id, ...props }]);
      return {
        id,
        dismiss: () => setToasts((prevToasts) => prevToasts.filter((t) => t.id !== id)),
        update: (props: Partial<ToastProps>) =>
          setToasts((prevToasts) =>
            prevToasts.map((t) => (t.id === id ? { ...t, ...props } : t))
          ),
      };
    },
    []
  );

  const dismiss = React.useCallback((id?: string) => {
    setToasts((prevToasts) =>
      id ? prevToasts.filter((t) => t.id !== id) : []
    );
  }, []);

  return {
    toasts,
    toast,
    dismiss,
  };
}
