# ✅ Python 3.12 kullanıyoruz
FROM python:3.12

# ✅ Çalışma dizinini belirleyelim
WORKDIR /app

# ✅ Gerekli bağımlılıkları yükleyelim
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Tüm backend dosyalarını container içine kopyalayalım
COPY . .

# ✅ Django uygulamasını çalıştırmadan önce migration ve statik dosya toplama işlemleri yapılacak
CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]
