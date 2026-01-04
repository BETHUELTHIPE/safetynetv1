"""
Performance optimizations for the Kings Park, Kwamhlanga CPF website.
Apply these settings in production for best performance.
"""

import os
from django.conf import settings

def apply_performance_settings(settings_dict):
    """
    Apply performance optimizations to the Django settings.
    
    These optimizations improve database queries, caching, template rendering,
    and overall responsiveness of the application.
    """
    
    # Database optimizations
    settings_dict['DATABASE_OPTIONS'] = {
        'CONN_MAX_AGE': 60,  # Persistent connections
        'ATOMIC_REQUESTS': True,  # Wrap each request in a transaction for consistency
    }
    
    # Additional caching settings
    settings_dict['CACHE_MIDDLEWARE_ALIAS'] = 'default'
    settings_dict['CACHE_MIDDLEWARE_SECONDS'] = 600  # 10 minutes
    settings_dict['CACHE_MIDDLEWARE_KEY_PREFIX'] = 'kingspark_cpf'
    
    # Template caching
    settings_dict['TEMPLATES'][0]['OPTIONS']['loaders'] = [
        ('django.template.loaders.cached.Loader', [
            'django.template.loaders.filesystem.Loader',
            'django.template.loaders.app_directories.Loader',
        ]),
    ]
    
    # Add cache middleware
    settings_dict['MIDDLEWARE'].insert(0, 'django.middleware.cache.UpdateCacheMiddleware')
    settings_dict['MIDDLEWARE'].append('django.middleware.cache.FetchFromCacheMiddleware')
    
    # Add compression middleware
    if 'django.middleware.gzip.GZipMiddleware' not in settings_dict['MIDDLEWARE']:
        settings_dict['MIDDLEWARE'].insert(0, 'django.middleware.gzip.GZipMiddleware')
    
    # Session optimization
    settings_dict['SESSION_ENGINE'] = 'django.contrib.sessions.backends.cached_db'
    
    # Static files serving with whitenoise for production
    if 'whitenoise.middleware.WhiteNoiseMiddleware' not in settings_dict['MIDDLEWARE']:
        # Insert after SecurityMiddleware
        security_index = settings_dict['MIDDLEWARE'].index('django.middleware.security.SecurityMiddleware')
        settings_dict['MIDDLEWARE'].insert(security_index + 1, 'whitenoise.middleware.WhiteNoiseMiddleware')
        
    # Whitenoise settings for static files compression
    settings_dict['STATICFILES_STORAGE'] = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
    
    # Optimize DB query execution - automatically select related objects
    settings_dict['INSTALLED_APPS'].append('django.contrib.postgres')
    
    # Media file performance settings
    settings_dict['MEDIA_ROOT'] = os.path.join(settings.BASE_DIR, 'media')
    settings_dict['MEDIA_URL'] = '/media/'
    
    # Content Security Policy settings
    settings_dict['CSP_DEFAULT_SRC'] = ("'self'", "https:")
    settings_dict['CSP_SCRIPT_SRC'] = ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com")
    settings_dict['CSP_STYLE_SRC'] = ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com")
    settings_dict['CSP_IMG_SRC'] = ("'self'", "data:", "https:")
    
    # Django Debug Toolbar - only in debug mode
    if settings_dict.get('DEBUG', False):
        settings_dict['INSTALLED_APPS'].append('debug_toolbar')
        settings_dict['MIDDLEWARE'].insert(0, 'debug_toolbar.middleware.DebugToolbarMiddleware')
        settings_dict['INTERNAL_IPS'] = ['127.0.0.1']
    
    # Logging configuration for performance monitoring
    settings_dict['LOGGING']['handlers']['performance'] = {
        'level': 'INFO',
        'class': 'logging.handlers.RotatingFileHandler',
        'filename': os.path.join(settings.BASE_DIR, 'logs', 'performance.log'),
        'maxBytes': 10 * 1024 * 1024,  # 10 MB
        'backupCount': 5,
        'formatter': 'verbose',
    }
    
    settings_dict['LOGGING']['loggers']['django.db.backends'] = {
        'handlers': ['console', 'performance'] if settings_dict.get('DEBUG', False) else ['performance'],
        'level': 'DEBUG' if settings_dict.get('DEBUG', False) else 'INFO',
        'propagate': False,
    }
    
    return settings_dict
