import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ✅ STATIC DOSYA AYARLARI
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]  # Statik dosyaların bulunduğu dizin
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')  # Django'nun topladığı statik dosyaların kaydedildiği dizin


SECRET_KEY = 'django-insecure-sy)$lg)q)s71#(-!me*f25(u-e-8yqmsl=i!a1d(lcjp0(3rkq'

DEBUG = True  # Test ortamı için True, Production'da False yap

ALLOWED_HOSTS = ["*"]  # Docker için açık bırakıyoruz

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',  # 🔥 Django REST Framework
    'core',  # Ana uygulama
]


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'core.validators.CustomPasswordValidator',  # 🚀 Sadece özel şifre doğrulayıcıyı kullan
    },
]



MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',  # ✅ Hata mesajında eklenmesi istenmiş
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # ✅ Hata mesajında eklenmesi istenmiş
    'django.contrib.messages.middleware.MessageMiddleware',  # ✅ Hata mesajında eklenmesi istenmiş
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# 📌 **TEMPLATE AYARLARI**
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # ✅ Güncellendi!
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# 📌 **DATABASE (MySQL)**
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pocket_db',
        'USER': 'pocket_user',
        'PASSWORD': 'pocket_password',
        'HOST': 'db',
        'PORT': '3306',
    }
}

# 📌 **DİĞER AYARLAR**
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Berlin'  # Almanya zaman dilimi
USE_I18N = True
USE_TZ = True

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

ROOT_URLCONF = 'backend.urls'  # Eğer backend klasörün ana URL'leri içeriyorsa

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

