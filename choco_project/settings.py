import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    'SECRET_KEY',
    'django-insecure-ammas-chocolate-pos-system-key-secret'
)

DEBUG = os.environ.get('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '*').split(',')

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pos_core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 👈 WhiteNoise එක Security එකට පල්ලෙහායින්
    'django.contrib.sessions.middleware.SessionMiddleware',  # 👈 මේක අනිවාර්යයෙන්ම දෙවැනි හෝ තුන්වැනි තැනට තියෙන්න ඕනේ
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # 👈 Session එකට පල්ලෙහායින් තියෙන්න ඕනේ
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'choco_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # ✨ FEATURE ADDED: දවසේ සාරාංශ බැනර් එක ලෝඩ් වෙන්න pos_core templates පාත් එක විතරක් එකතු කළා
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'pos_core', 'templates'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'choco_project.wsgi.application'

# DATABASES = {
#     'default': dj_database_url.config(
#         # ✨ FEATURE ADDED: SQLite වෙනුවට ඔයාගේ Supabase Cloud Database ලින්ක් එක විතරක් default එකට දැම්මා
#         # ⚠️ settings.py එකේ DATABASES කෑල්ල මේ විදිහට විතරක් වෙනස් කරන්න
# 🔗 Supabase Cloud Database Connection (Direct Object Format)
# 🔗 Supabase Cloud Database Connection (Pure Django Standard)
# 🔗 Supabase Cloud Live Database Connection (Direct Mumbai Route)
# 🔗 Supabase Cloud Live Database Connection (Mumbai Pooler Route)
# 🔗 Supabase Cloud Live Database Connection (Tenant Embedded Format)
# 🔗 Supabase Cloud Live Database Connection (Direct Production Connection String)
# 🔗 Supabase Cloud Live Database Connection (Direct Connection String for Django)
# 🔗 Supabase Cloud Live Database Connection (Direct Mumbai Pooler Route)
# 🔗 Supabase Cloud Live Database Connection (Direct Route - 100% Stable)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'postgres.gvucbxvqyhirsvhpqrtt',
        'PASSWORD': 'Nima@2001044022',
        # 🇮🇳 ඔයාගේ මුම්බායි සර්වර් එකේ සජීවී නිල හොස්ට් එක
        'HOST': 'aws-1-ap-south-1.pooler.supabase.com', 
        # ⚡ කිසිම ටෙනන්ට් බග් එකක් නැති ඍජු පෝට් එක
        'PORT': '6543', 
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Colombo'  # 🇱🇰 ලංකාවේ වෙලාව ලස්සනට වැඩ කරන්න
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880

CSRF_TRUSTED_ORIGINS = os.environ.get(
    'CSRF_TRUSTED_ORIGINS',
    'http://localhost,http://127.0.0.1'
).split(',')

if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'