# 運用環境用Dockerfile
FROM nginx:alpine

# デフォルトの設定をクリア
RUN rm -f /etc/nginx/conf.d/default.conf

# メイン設定とサーバーブロック設定をそれぞれコピー
COPY ./nginx.conf /etc/nginx/nginx.conf
COPY ./conf.d/default.conf /etc/nginx/conf.d/default.conf

# コンテナ起動時に他のSSL関連設定ファイルをクリア
# CMD rm -f /etc/nginx/conf.d/ssl.conf && nginx -g 'daemon off;' 
CMD ["nginx", "-g", "daemon off;"]