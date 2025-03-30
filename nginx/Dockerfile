# ✅ Hafif Nginx sürümünü kullanıyoruz
FROM nginx:alpine

# ✅ Konfigürasyon dosyasını container içine kopyalayalım
COPY nginx.conf /etc/nginx/nginx.conf

# ✅ Nginx başlat
CMD ["nginx", "-g", "daemon off;"]
