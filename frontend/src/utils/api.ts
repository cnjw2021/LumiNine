import axios, { AxiosRequestConfig } from 'axios';

const api = axios.create({
    // 開発環境と本番環境で同じ設定を使用
    baseURL: '/api',
    timeout: 30000,
    withCredentials: true,
    headers: {
        'Content-Type': 'application/json; charset=utf-8',
        'Accept': 'application/json; charset=utf-8'
    }
});

// getUri関数の追加 - リクエストURIを構築するための関数
api.getUri = function(config?: AxiosRequestConfig): string {
    // 必要な設定のみを抽出して新しいconfigを作成
    const mergedConfig: AxiosRequestConfig = {
        baseURL: this.defaults.baseURL,
        url: config?.url
    };
    
    if (config) {
        if (config.params) mergedConfig.params = config.params;
        if (config.paramsSerializer) mergedConfig.paramsSerializer = config.paramsSerializer;
    }
    
    return axios.getUri(mergedConfig);
};

// リクエストインターセプター
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        // 요청 추적을 위한 Request ID 설정 (없으면 생성)
        if (!config.headers['X-Request-ID']) {
            const rid = `${Date.now()}-${Math.random().toString(36).slice(2, 10)}`;
            config.headers['X-Request-ID'] = rid;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

// レスポンスインターセプター
api.interceptors.response.use(
    (response) => {
        // 新しいトークンがレスポンスヘッダーにある場合は更新
        const newToken = response.headers['x-new-token'];
        if (newToken) {
            localStorage.setItem('token', newToken);
        }
        return response;
    },
    (error) => {
        // 401認証エラーの場合は静かに処理（コンソールログなし）
        if (error.response?.status === 401) {
            // トークンをクリア
            localStorage.removeItem('token');
            localStorage.removeItem('refresh_token');
            
            // ログイン画面へリダイレクト（現在のパスがログイン画面でない場合のみ）
            if (typeof window !== 'undefined' && !window.location.pathname.includes('/login')) {
                window.location.href = '/login';
            }
            
            // エラーオブジェクトを変更して返す（必要な情報のみ）
            return Promise.reject({
                response: {
                    status: 401,
                    data: error.response?.data || { message: 'メールアドレスまたはパスワードが正しくありません' }
                }
            });
        }
        
        // その他のエラーは詳細情報を取得
        const errorDetails: {
            status?: number;
            statusText?: string;
            data?: unknown;
            url?: string;
            method?: string;
            message?: string;
        } = {};
        
        // レスポンス関連の情報
        if (error.response) {
            errorDetails.status = error.response.status;
            errorDetails.statusText = error.response.statusText;
            errorDetails.data = error.response.data;
        }
        
        // リクエスト設定関連の情報
        if (error.config) {
            errorDetails.url = error.config.url;
            errorDetails.method = error.config.method;
        }
        
        // エラーメッセージ
        if (error.message) {
            errorDetails.message = error.message;
        }

        // エラーオブジェクトを返す
        return Promise.reject({
            ...error,
            details: errorDetails
        });
    }
);

export default api;
