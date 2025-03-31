from django.urls import path, include
from rest_framework.routers import DefaultRouter
from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from .views import profil_view
from .views import (
    MitarbeiterViewSet, ProjektViewSet, AbrechnungViewSet, ReiseberichtViewSet,
    SchulungskostenViewSet, AbordnungViewSet, EinnahmeViewSet
)

router = DefaultRouter()
router.register(r'mitarbeiter', MitarbeiterViewSet)
router.register(r'projekte', ProjektViewSet)
router.register(r'abrechnung', AbrechnungViewSet)
router.register(r'reisebericht', ReiseberichtViewSet)
router.register(r'schulungskosten', SchulungskostenViewSet)
router.register(r'abordnung', AbordnungViewSet)
router.register(r'einnahmen', EinnahmeViewSet)


urlpatterns = [
    path('', include(router.urls)),  # API Router'ı ekli
]

from django.contrib.auth.views import (
    PasswordChangeView, PasswordChangeDoneView,
    PasswordResetView, PasswordResetDoneView,
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.urls import path

urlpatterns = [
    # Şifre değiştirme
    path('password_change/', PasswordChangeView.as_view(template_name='auth/password_change.html'), name='password_change'),
    path('password_change_done/', PasswordChangeDoneView.as_view(template_name='auth/password_change_done.html'), name='password_change_done'),


    path('profil/', profil_view, name="profil"),  # Profil sayfası
]

