from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import login_view, custom_logout_view, manager_dashboard_view, mitarbeiter_dashboard_view #manager_projekte_view, manager_projekte_delete, manager_projekte_export, manager_abordnungen_view, manager_abordnungen_delete, manager_abordnungen_export, manager_schulungskosten_view, manager_schulungskosten_delete, manager_schulungskosten_export, manager_abrechnung_view, manager_abrechnung_delete, manager_abrechnung_export, manager_reisebericht_view, manager_reisebericht_delete, manager_reisebericht_export, 
from core.views import admin_dashboard_view, export_finanzuebersicht, admin_projekte_view, admin_projekt_delete, export_projekte, admin_einnahmen_view, admin_einnahme_delete, export_einnahmen, admin_mitarbeiter_view, admin_mitarbeiter_delete, export_mitarbeiter, admin_abordnung_view, admin_abordnung_delete, export_abordnung, admin_reisebericht_view, admin_reisebericht_delete, export_reisebericht, admin_schulungskosten_view, admin_schulung_delete, export_schulungskosten, admin_abrechnung_view, admin_abrechnung_delete, export_abrechnung
from django.contrib.auth.views import LogoutView
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),  
    path('login/', login_view, name="login"),
    path('logout/', custom_logout_view, name='logout'),
    path('admin-dashboard/', admin_dashboard_view, name="admin_dashboard"),
    path("export-finanzuebersicht/", export_finanzuebersicht, name="export_finanzübersicht"),  
    path('admin-projekte/', admin_projekte_view, name="admin_projekte"),
    path('admin-projekte/delete/<int:id>/', admin_projekt_delete, name="admin_projekt_delete"),
    path("export-projekte/", export_projekte, name="export_projekte"),
    path("admin-einnahmen/", admin_einnahmen_view, name="admin_einnahmen"),
    path("admin-einnahme-delete/<int:id>/", admin_einnahme_delete, name="admin_einnahme_delete"),
    path("admin-einnahmen-export/", export_einnahmen, name="export_einnahmen"),
    path('admin-mitarbeiter/', admin_mitarbeiter_view, name="admin_mitarbeiter"),
    path('admin-mitarbeiter/delete/<int:id>/', admin_mitarbeiter_delete, name='admin_mitarbeiter_delete'),
    path("export-mitarbeiter/", export_mitarbeiter, name="export_mitarbeiter"),
    path("admin-abordnung/", admin_abordnung_view, name="admin_abordnung"),
    path("admin-abordnung/delete/<int:id>/", admin_abordnung_delete, name="admin_abordnung_delete"),
    path("export-abordnung/", export_abordnung, name="export_abordnung"),
    path("admin-reisebericht/", admin_reisebericht_view, name="admin_reisebericht"),
    path("admin-reisebericht/delete/<int:id>/", admin_reisebericht_delete, name="admin_reisebericht_delete"),
    path("export-reisebericht/", export_reisebericht, name="export_reisebericht"),
    path("admin-schulungskosten/", admin_schulungskosten_view, name="admin_schulungskosten"),
    path("admin-schulungskosten/delete/<int:id>/", admin_schulung_delete, name="admin_schulung_delete"),
    path("export-schulungskosten/", export_schulungskosten, name="export_schulungskosten"),
    path("admin-abrechnung/", admin_abrechnung_view, name="admin_abrechnung"),
    path("admin-abrechnung/delete/<int:id>/", admin_abrechnung_delete, name="admin_abrechnung_delete"),
    path("export-abrechnung/", export_abrechnung, name="export_abrechnung"),

    path("manager-dashboard/", manager_dashboard_view, name="manager_dashboard"),
    path("mitarbeiter-dashboard/", mitarbeiter_dashboard_view, name="mitarbeiter_dashboard"),
 

    # path("manager/projekte/", manager_projekte_view, name="manager_projekte"),
    # path("manager/projekte/delete/<int:projekt_id>/", manager_projekte_delete, name="manager_projekt_delete"),
    # path("manager/projekte/export/", manager_projekte_export, name="manager_projekte_export"),
    # path("manager/abordnungen/", manager_abordnungen_view, name="manager_abordnungen"),
    # path("manager/abordnungen/delete/<int:id>/", manager_abordnungen_delete, name="manager_abordnung_delete"),
    # path("manager/abordnungen/export/", manager_abordnungen_export, name="manager_abordnung_export"),
    # path('manager/schulungskosten/', manager_schulungskosten_view, name='manager_schulungskosten'),
    # path('manager/schulungskosten/delete/<int:id>/', manager_schulungskosten_delete, name='manager_schulungskosten_delete'),
    # path('manager/schulungskosten/export/', manager_schulungskosten_export, name='manager_schulungskosten_export'),
    # path("manager-abrechnung/", manager_abrechnung_view, name="manager_abrechnung"),
    # path("manager-abrechnung/delete/<int:id>/", manager_abrechnung_delete, name="manager_abrechnung_delete"),
    # path("manager-abrechnung/export/", manager_abrechnung_export, name="manager_abrechnung_export"),
    # path('manager/reisebericht/', manager_reisebericht_view, name='manager_reisebericht'), 
    # path('manager/reisebericht/delete/<int:id>/', manager_reisebericht_delete, name='manager_reisebericht_delete'),  
    # path('manager/reisebericht/export/', manager_reisebericht_export, name='manager_reisebericht_export'), 


    path('', include('core.urls')),
]

# ✅ Admin logout için özel yönlendirme
def admin_logout_redirect(request):
    return redirect('/admin/login/')

urlpatterns += [
    path('admin/logout/', admin_logout_redirect, name='admin_logout_redirect'),
]


# ✅ DEBUG MODUNDA STATİK DOSYALARI SUN
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


# ✅ HATA SAYFALARINI YÖNLENDİR
from django.conf.urls import handler404, handler500, handler403
from core import views  # core uygulamasındaki hata sayfası fonksiyonları için

handler404 = 'core.views.custom_404'
handler500 = 'core.views.custom_500'
handler403 = 'core.views.custom_403'