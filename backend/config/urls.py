from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static

def health_check(request):
    return JsonResponse({"status": "ok"})

# Custom Django Admin configuration for Finovo
admin.site.site_header = "Finovo Administration"
admin.site.site_title = "Finovo Admin Portal"
admin.site.index_title = "Welcome to Finovo Admin Portal"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health_check'),

    # API v1
    path('api/v1/', include([
        path('auth/',        include('apps.accounts.urls',     namespace='accounts')),
        path('dashboard/',   include('apps.core.urls')),
        path('wallet/',      include('apps.wallet.urls')),
        path('investments/', include('apps.investments.urls')),
        path('',             include('apps.transactions.urls')),   # /deposits/ + /withdrawals/
        path('referrals/',   include('apps.referrals.urls')),
        path('support/',     include('apps.support.urls')),
        path('admin-panel/', include('apps.core.admin_urls',   namespace='admin_panel')),
    ])),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
