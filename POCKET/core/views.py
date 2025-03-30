from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets
from .models import Mitarbeiter, Projekt, Abrechnung, Reisebericht, Schulungskosten, Abordnung, ProjektMitarbeiter
from .serializers import MitarbeiterSerializer, ProjektSerializer, AbrechnungSerializer, ReiseberichtSerializer, SchulungskostenSerializer, AbordnungSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.views import ObtainAuthToken
from django.utils.decorators import method_decorator
from .forms import BenutzerForm, BenutzerProfilForm
from django.contrib import messages
from simple_history.utils import update_change_reason
from core.models import BenutzerProfil
from django.db.models import Count
from django.core.paginator import Paginator
from django.http import HttpResponse
from collections import defaultdict
import calendar
import csv

@method_decorator(csrf_exempt, name='dispatch')
class CustomObtainAuthToken(ObtainAuthToken):
    pass

# ✅ API ViewSets (Bunları Değiştirmiyoruz)
class MitarbeiterViewSet(viewsets.ModelViewSet):
    queryset = Mitarbeiter.objects.all()
    serializer_class = MitarbeiterSerializer

class ProjektViewSet(viewsets.ModelViewSet):
    queryset = Projekt.objects.all()
    serializer_class = ProjektSerializer

class AbrechnungViewSet(viewsets.ModelViewSet):
    queryset = Abrechnung.objects.all()
    serializer_class = AbrechnungSerializer

class ReiseberichtViewSet(viewsets.ModelViewSet):
    queryset = Reisebericht.objects.all()
    serializer_class = ReiseberichtSerializer

class SchulungskostenViewSet(viewsets.ModelViewSet):
    queryset = Schulungskosten.objects.all()
    serializer_class = SchulungskostenSerializer

class AbordnungViewSet(viewsets.ModelViewSet):
    queryset = Abordnung.objects.all()
    serializer_class = AbordnungSerializer

# ✅ Giriş Ekranı (Django Template ile Login)
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            if user.is_superuser:  # 🚀 Eğer admin ise admin dashboard'a yönlendir
                return redirect("admin_dashboard")
            elif user.groups.filter(name="Manager").exists():
                return redirect("manager_dashboard")
            elif user.groups.filter(name="Mitarbeiter").exists():
                return redirect("mitarbeiter_dashboard")
            else:
                return render(request, "login.html", {"error": "Sie haben keine Berechtigung für den Zugriff."})
        else:
            return render(request, "login.html", {"error": "Benutzername oder Passwort ist falsch."})

    return render(request, "login.html")


from django.db.models import Sum, Q

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard_view(request):
    # 🔢 Genel toplamlar
    total_projekte = Projekt.objects.count()
    total_mitarbeiter = Mitarbeiter.objects.count()
    total_abordnungen = Abordnung.objects.count()
    total_reisen = Reisebericht.objects.count()
    total_schulungen = Schulungskosten.objects.count()
    total_abrechnungen = Abrechnung.objects.count()

    # 💸 Maliyet hesapları
    total_abrechnung = Abrechnung.objects.aggregate(s=Sum("brutto_summe"))["s"] or 0
    total_reise = Reisebericht.objects.aggregate(s=Sum("kosten_fahrt"))["s"] or 0
    total_hotel = Reisebericht.objects.aggregate(s=Sum("kosten_übernachtung"))["s"] or 0
    total_schulung = Schulungskosten.objects.aggregate(s=Sum("kosten"))["s"] or 0

    total_kosten = total_abrechnung + total_reise + total_hotel + total_schulung

    projekt_kosten = (
        (Abrechnung.objects.filter(projekt__isnull=False).aggregate(s=Sum("brutto_summe"))["s"] or 0)
        + (Reisebericht.objects.filter(projekt__isnull=False).aggregate(s=Sum("kosten_fahrt"))["s"] or 0)
        + (Reisebericht.objects.filter(projekt__isnull=False).aggregate(s=Sum("kosten_übernachtung"))["s"] or 0)
    )
    allgemeine_kosten = total_kosten - projekt_kosten

    # 🎨 Grafik 1: Kategori bazlı dağılım (Doughnut)
    category_data = {
        "Abrechnung": float(total_abrechnung),
        "Reise": float(total_reise + total_hotel),
        "Schulung": float(total_schulung),
    }

    # 🎨 Grafik 2: Projekt vs Allgemein (Doughnut)
    projekt_vs_allgemein_data = {
        "Projektgebunden": float(projekt_kosten),
        "Allgemein": float(allgemeine_kosten),
    }

    context = {
        "total_projekte": total_projekte,
        "total_mitarbeiter": total_mitarbeiter,
        "total_abordnungen": total_abordnungen,
        "total_reisen": total_reisen,
        "total_schulungen": total_schulungen,
        "total_abrechnungen": total_abrechnungen,
        "total_kosten": total_kosten,
        "projektgebundene_kosten": projekt_kosten,
        "allgemeine_kosten": allgemeine_kosten,
        "category_data": category_data,
        "projekt_vs_allgemein_data": projekt_vs_allgemein_data,
    }

    return render(request, "admin_pages/admin_dashboard.html", context)

@login_required
@user_passes_test(lambda u: u.is_superuser)
def export_finanzuebersicht(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="finanzuebersicht.csv"'
    response.write('\ufeff')  # UTF-8 BOM

    writer = csv.writer(response)
    writer.writerow(['Kategorie', 'Betrag (€)'])

    abrechnung = Abrechnung.objects.all()
    reisen = Reisebericht.objects.all()
    schulungen = Schulungskosten.objects.all()

    total_abrechnung = abrechnung.aggregate(s=Sum('brutto_summe'))['s'] or 0
    total_reise = reisen.aggregate(s=Sum('kosten_fahrt'))['s'] or 0
    total_hotel = reisen.aggregate(s=Sum('kosten_übernachtung'))['s'] or 0
    total_schulung = schulungen.aggregate(s=Sum('kosten'))['s'] or 0

    writer.writerow(['Abrechnung', f"{total_abrechnung:.2f}"])
    writer.writerow(['Reise (Fahrt + Hotel)', f"{(total_reise + total_hotel):.2f}"])
    writer.writerow(['Schulung', f"{total_schulung:.2f}"])

    total = total_abrechnung + total_reise + total_hotel + total_schulung
    writer.writerow(['Gesamtkosten', f"{total:.2f}"])

    return response

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_projekte_view(request):
    if request.method == "POST":
        edit_id = request.POST.get("edit_id")
        projektname = request.POST.get("projektname")
        startdatum = request.POST.get("startdatum")
        enddatum = request.POST.get("enddatum")
        budget = request.POST.get("budget")
        kunde_1 = request.POST.get("kunde_1")
        kunde_2 = request.POST.get("kunde_2")
        projekttyp = request.POST.get("projekttyp")
        status = request.POST.get("status")
        beschreibung = request.POST.get("beschreibung")

        if projektname and startdatum and enddatum and budget and kunde_1 and projekttyp and status:
            if edit_id:
                # 🔄 Güncelleme
                projekt = get_object_or_404(Projekt, id=edit_id)
                projekt.projektname = projektname
                projekt.startdatum = startdatum
                projekt.enddatum = enddatum
                projekt.budget = budget
                projekt.kunde_1 = kunde_1
                projekt.kunde_2 = kunde_2
                projekt.projekttyp = projekttyp
                projekt.status = status
                projekt.beschreibung = beschreibung
                projekt.save()
                messages.success(request, "✅ Projekt wurde aktualisiert.")
            else:
                # ➕ Yeni Kayıt
                Projekt.objects.create(
                    projektname=projektname,
                    startdatum=startdatum,
                    enddatum=enddatum,
                    budget=budget,
                    kunde_1=kunde_1,
                    kunde_2=kunde_2,
                    projekttyp=projekttyp,
                    status=status,
                    beschreibung=beschreibung
                )
                messages.success(request, "✅ Projekt erfolgreich gespeichert.")
        else:
            messages.warning(request, "⚠️ Bitte alle Pflichtfelder ausfüllen.")

        return redirect("admin_projekte")

    # ✅ GET (Listeleme ve Filtreleme)
    projekte = Projekt.objects.all()

    projektname = request.GET.get("projektname")
    kunde_1 = request.GET.get("kunde")
    startdatum = request.GET.get("start")
    enddatum = request.GET.get("end")
    status = request.GET.get("status")

    if projektname:
        projekte = projekte.filter(projektname__icontains=projektname)
    if kunde_1:
        projekte = projekte.filter(kunde_1__icontains=kunde_1)
    if startdatum:
        projekte = projekte.filter(startdatum__gte=startdatum)
    if enddatum:
        projekte = projekte.filter(enddatum__lte=enddatum)
    if status:
        projekte = projekte.filter(status__icontains=status)

    # Sayfalama
    paginator = Paginator(projekte, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "admin_pages/admin_projekte.html", {
        "projekte": page_obj,
    })


# ✅ Projekt Silme
@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_projekt_delete(request, id):
    projekt = get_object_or_404(Projekt, id=id)
    projekt.delete()
    messages.success(request, "🗑️ Projekt wurde gelöscht.")
    return redirect("admin_projekte")


# ✅ Projekt Export
@login_required
@user_passes_test(lambda u: u.is_superuser)
def export_projekte(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="projekte.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(['Projektname', 'Kunde 1', 'Startdatum', 'Enddatum', 'Budget', 'Status'])

    projekte = Projekt.objects.all()

    # Filtreleme
    projektname = request.GET.get("projektname")
    kunde_1 = request.GET.get("kunde")
    startdatum = request.GET.get("start")
    enddatum = request.GET.get("end")
    status = request.GET.get("status")

    if projektname:
        projekte = projekte.filter(projektname__icontains=projektname)
    if kunde_1:
        projekte = projekte.filter(kunde_1__icontains=kunde_1)
    if startdatum:
        projekte = projekte.filter(startdatum__gte=startdatum)
    if enddatum:
        projekte = projekte.filter(enddatum__lte=enddatum)
    if status:
        projekte = projekte.filter(status__icontains=status)

    for p in projekte:
        writer.writerow([
            p.projektname,
            p.kunde_1,
            p.startdatum.strftime("%d.%m.%Y"),
            p.enddatum.strftime("%d.%m.%Y"),
            p.budget,
            p.status
        ])

    return response


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_mitarbeiter_view(request):
    if request.method == "POST":
        edit_id = request.POST.get("edit_id")
        vorname = request.POST.get("vorname")
        nachname = request.POST.get("nachname")
        standort = request.POST.get("standort")
        erste_taetigkeitsstaette = request.POST.get("erste_taetigkeitsstaette")
        abteilung = request.POST.get("abteilung")
        status = request.POST.get("status")
        rolle = request.POST.get("rolle")

        if vorname and nachname and standort and erste_taetigkeitsstaette and abteilung and status and rolle:
            if edit_id:
                # 🔄 Güncelleme
                m = get_object_or_404(Mitarbeiter, id=edit_id)
                m.vorname = vorname
                m.nachname = nachname
                m.standort = standort
                m.erste_taetigkeitsstaette = erste_taetigkeitsstaette
                m.abteilung = abteilung
                m.status = status
                m.rolle = rolle
                m.save()
                messages.success(request, "✅ Mitarbeiter wurde aktualisiert.")
            else:
                # ➕ Yeni kayıt
                Mitarbeiter.objects.create(
                    vorname=vorname,
                    nachname=nachname,
                    standort=standort,
                    erste_taetigkeitsstaette=erste_taetigkeitsstaette,
                    abteilung=abteilung,
                    status=status,
                    rolle=rolle
                )
                messages.success(request, "✅ Mitarbeiter erfolgreich gespeichert.")
        else:
            messages.warning(request, "⚠️ Bitte alle Felder ausfüllen.")

        return redirect("admin_mitarbeiter")

    # ✅ GET: Listeleme + filtre
    mitarbeiter = Mitarbeiter.objects.all()
    vorname = request.GET.get("vorname")
    nachname = request.GET.get("nachname")
    rolle = request.GET.get("rolle")
    abteilung = request.GET.get("abteilung")
    status = request.GET.get("status")

    if vorname:
        mitarbeiter = mitarbeiter.filter(vorname__icontains=vorname)
    if nachname:
        mitarbeiter = mitarbeiter.filter(nachname__icontains=nachname)
    if rolle:
        mitarbeiter = mitarbeiter.filter(rolle__icontains=rolle)
    if abteilung:
        mitarbeiter = mitarbeiter.filter(abteilung__icontains=abteilung)
    if status:
        mitarbeiter = mitarbeiter.filter(status__icontains=status)

    paginator = Paginator(mitarbeiter, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "admin_pages/admin_mitarbeiter.html", {
        "mitarbeiter": page_obj
    })


# ✅ Silme
@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_mitarbeiter_delete(request, id):
    mitarbeiter = get_object_or_404(Mitarbeiter, id=id)
    mitarbeiter.delete()
    messages.success(request, "🗑️ Mitarbeiter wurde gelöscht.")
    return redirect("admin_mitarbeiter")


# ✅ CSV Export (filtreli)
@login_required
@user_passes_test(lambda u: u.is_superuser)
def export_mitarbeiter(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="mitarbeiter.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(['Vorname', 'Nachname', 'Standort', '1. Tätigkeitsstätte', 'Abteilung', 'Status', 'Rolle'])

    mitarbeiter = Mitarbeiter.objects.all()

    # Filtreler
    vorname = request.GET.get("vorname")
    nachname = request.GET.get("nachname")
    rolle = request.GET.get("rolle")
    abteilung = request.GET.get("abteilung")
    status = request.GET.get("status")

    if vorname:
        mitarbeiter = mitarbeiter.filter(vorname__icontains=vorname)
    if nachname:
        mitarbeiter = mitarbeiter.filter(nachname__icontains=nachname)
    if rolle:
        mitarbeiter = mitarbeiter.filter(rolle__icontains=rolle)
    if abteilung:
        mitarbeiter = mitarbeiter.filter(abteilung__icontains=abteilung)
    if status:
        mitarbeiter = mitarbeiter.filter(status__icontains=status)

    for m in mitarbeiter:
        writer.writerow([
            m.vorname,
            m.nachname,
            m.standort,
            m.erste_taetigkeitsstaette,
            m.abteilung,
            m.status,
            m.rolle
        ])

    return response


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_projektmitarbeiter_view(request):
    zuordnungen = ProjektMitarbeiter.objects.select_related("projekt", "mitarbeiter")
    projekt_filter_id = request.GET.get("projekt_id")
    if projekt_filter_id:
        zuordnungen = zuordnungen.filter(projekt_id=projekt_filter_id)

    projekte = Projekt.objects.all()
    mitarbeiter = Mitarbeiter.objects.all()

    if request.method == "POST":
        projekt_id = request.POST.get("projekt_id")
        mitarbeiter_id = request.POST.get("mitarbeiter_id")

        if projekt_id and mitarbeiter_id:
            obj, created = ProjektMitarbeiter.objects.get_or_create(
                projekt_id=projekt_id,
                mitarbeiter_id=mitarbeiter_id
            )
            if created:
                messages.success(request, "✅ Zuordnung erfolgreich gespeichert.")
            else:
                messages.warning(request, "⚠️ Diese Zuordnung existiert bereits.")

        return redirect("admin_projektmitarbeiter")

    return render(request, "admin_pages/admin_projektmitarbeiter.html", {
        "zuordnungen": zuordnungen,
        "projekte": projekte,
        "mitarbeiter": mitarbeiter,
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_projektmitarbeiter_delete(request, id):
    eintrag = get_object_or_404(ProjektMitarbeiter, id=id)
    eintrag.delete()
    return redirect("admin_projektmitarbeiter")



# Abordnung Yönetimi
@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_abordnung_view(request):
    projekte = Projekt.objects.all()
    mitarbeiter = Mitarbeiter.objects.all()
    abordnungen = filter_abordnungen(request)

    # Sayfalama
    paginator = Paginator(abordnungen, 10)  # Sayfa başına 10 öğe
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.method == "POST":
        edit_id = request.POST.get("edit_id")
        projekt_id = request.POST.get("projekt_id")
        mitarbeiter_id = request.POST.get("mitarbeiter_id")
        zeitraum_start = request.POST.get("zeitraum_start")
        zeitraum_ende = request.POST.get("zeitraum_ende")

        if projekt_id and mitarbeiter_id and zeitraum_start and zeitraum_ende:
            if edit_id:
                # 🔄 GÜNCELLEME MODU
                eintrag = get_object_or_404(Abordnung, id=edit_id)
                eintrag.projekt_id = projekt_id
                eintrag.mitarbeiter_id = mitarbeiter_id
                eintrag.zeitraum_start = zeitraum_start
                eintrag.zeitraum_ende = zeitraum_ende
                eintrag.save()
                messages.success(request, "✅ Abordnung wurde aktualisiert.")
            else:
                # ➕ YENİ EKLEME MODU
                overlap_exists = Abordnung.objects.filter(
                    projekt_id=projekt_id,
                    mitarbeiter_id=mitarbeiter_id,
                    zeitraum_start__lte=zeitraum_ende,
                    zeitraum_ende__gte=zeitraum_start
                ).exists()

                if overlap_exists:
                    messages.warning(request, "⚠️ Es existiert bereits eine Abordnung für diesen Zeitraum.")
                else:
                    Abordnung.objects.create(
                        projekt_id=projekt_id,
                        mitarbeiter_id=mitarbeiter_id,
                        zeitraum_start=zeitraum_start,
                        zeitraum_ende=zeitraum_ende
                    )
                    messages.success(request, "✅ Abordnung erfolgreich gespeichert.")
        else:
            messages.warning(request, "⚠️ Bitte alle Felder ausfüllen.")

        return redirect("admin_abordnung")

    return render(request, "admin_pages/admin_abordnung.html", {
        "abordnungen": page_obj,
        "projekte": projekte,
        "mitarbeiter": mitarbeiter,
    })

# Abordnung Silme
@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_abordnung_delete(request, id):
    abordnung = get_object_or_404(Abordnung, id=id)
    abordnung.delete()
    messages.success(request, "🗑️ Abordnung wurde gelöscht.")
    return redirect("admin_abordnung")

# Filtreleme fonksiyonu
def filter_abordnungen(request):
    queryset = Abordnung.objects.select_related("projekt", "mitarbeiter")
    projekt_id = request.GET.get("projekt_id")
    mitarbeiter_id = request.GET.get("mitarbeiter_id")
    start = request.GET.get("start")
    end = request.GET.get("end")

    if projekt_id:
        queryset = queryset.filter(projekt_id=projekt_id)
    if mitarbeiter_id:
        queryset = queryset.filter(mitarbeiter_id=mitarbeiter_id)
    if start:
        queryset = queryset.filter(zeitraum_start__gte=start)
    if end:
        queryset = queryset.filter(zeitraum_ende__lte=end)

    return queryset

# Export Fonksiyonu
def export_abordnung(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="abordnungen.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(['Projekt', 'Mitarbeiter', 'Startdatum', 'Enddatum'])

    queryset = Abordnung.objects.select_related('projekt', 'mitarbeiter')

    # Filtreleri uygula
    projekt_id = request.GET.get("projekt_id")
    mitarbeiter_id = request.GET.get("mitarbeiter_id")
    start = request.GET.get("start")
    end = request.GET.get("end")

    if projekt_id:
        queryset = queryset.filter(projekt_id=projekt_id)
    if mitarbeiter_id:
        queryset = queryset.filter(mitarbeiter_id=mitarbeiter_id)
    if start:
        queryset = queryset.filter(zeitraum_start__gte=start)
    if end:
        queryset = queryset.filter(zeitraum_ende__lte=end)

    # CSV yazma
    for ab in queryset:
        writer.writerow([
            ab.projekt.projektname,
            f"{ab.mitarbeiter.vorname} {ab.mitarbeiter.nachname}",
            ab.zeitraum_start.strftime("%d.%m.%Y"),
            ab.zeitraum_ende.strftime("%d.%m.%Y")
        ])

    return response


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_reisebericht_view(request):
    projekte = Projekt.objects.all()
    mitarbeiter = Mitarbeiter.objects.all()
    reiseberichte = filter_reiseberichte(request)

    paginator = Paginator(reiseberichte, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    if request.method == "POST":
        edit_id = request.POST.get("edit_id")
        data = request.POST

        if edit_id:
            rb = get_object_or_404(Reisebericht, id=edit_id)
        else:
            rb = Reisebericht()

        rb.mitarbeiter_id = data.get("mitarbeiter_id")
        rb.projekt_id = data.get("projekt_id") or None
        rb.datum = data.get("datum")
        rb.zielort = data.get("zielort")
        rb.zweck = data.get("zweck")
        rb.verkehrsmittel = data.get("verkehrsmittel")
        rb.distanz_km = data.get("distanz_km") or 0
        rb.kosten_fahrt = to_float_or_zero(data.get("kosten_fahrt"))
        rb.hotel_name = data.get("hotel_name") or ""
        rb.kosten_übernachtung = to_float_or_zero(data.get("kosten_übernachtung"))
        rb.gesamtkosten = rb.kosten_fahrt + rb.kosten_übernachtung
        rb.rechnung_vorhanden = data.get("rechnung_vorhanden")
        rb.save()

        if edit_id:
            messages.success(request, "✅ Reisebericht aktualisiert.")
        else:
            messages.success(request, "✅ Reisebericht hinzugefügt.")

        return redirect("admin_reisebericht")

    return render(request, "admin_pages/admin_reisebericht.html", {
        "reiseberichte": page_obj,
        "mitarbeiter": mitarbeiter,
        "projekte": projekte,
    })

def to_float_or_zero(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0

def filter_reiseberichte(request):
    queryset = Reisebericht.objects.select_related("mitarbeiter", "projekt")
    mitarbeiter_id = request.GET.get("mitarbeiter_id")
    projekt_id = request.GET.get("projekt_id")
    start = request.GET.get("start")
    end = request.GET.get("end")
    nur_mit_hotel = request.GET.get("nur_mit_hotel")

    if mitarbeiter_id:
        queryset = queryset.filter(mitarbeiter_id=mitarbeiter_id)
    if projekt_id:
        queryset = queryset.filter(projekt_id=projekt_id)
    if start:
        queryset = queryset.filter(datum__gte=start)
    if end:
        queryset = queryset.filter(datum__lte=end)
    if nur_mit_hotel == "1":
        queryset = queryset.exclude(kosten_übernachtung=0)

    return queryset.order_by("-datum")

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_reisebericht_delete(request, id):
    rb = get_object_or_404(Reisebericht, id=id)
    rb.delete()
    messages.success(request, "🗑️ Reisebericht wurde gelöscht.")
    return redirect("admin_reisebericht")

@login_required
@user_passes_test(lambda u: u.is_superuser)
def export_reisebericht(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="reiseberichte.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow([
        "Mitarbeiter", "Projekt", "Datum", "Zielort", "Zweck",
        "Verkehrsmittel", "Distanz (km)", "Kosten Fahrt", "Hotel", "Kosten Hotel", "Gesamtkosten", "Rechnung"
    ])

    queryset = filter_reiseberichte(request)

    for r in queryset:
        writer.writerow([
            f"{r.mitarbeiter.vorname} {r.mitarbeiter.nachname}",
            r.projekt.projektname if r.projekt else "-",
            r.datum.strftime("%d.%m.%Y"),
            r.zielort,
            r.zweck,
            r.verkehrsmittel,
            r.distanz_km,
            r.kosten_fahrt,
            r.hotel_name or "-",
            r.kosten_übernachtung,
            r.gesamtkosten,
            r.rechnung_vorhanden
        ])

    return response



@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_schulungskosten_view(request):
    mitarbeiter = Mitarbeiter.objects.all()
    projekte = Projekt.objects.all()

    # 🔎 Filtreleme
    schulungen = Schulungskosten.objects.select_related("mitarbeiter", "projekt").all()
    mitarbeiter_id = request.GET.get("mitarbeiter_id")
    teilgenommen = request.GET.get("teilgenommen")
    start = request.GET.get("start")
    end = request.GET.get("end")

    if mitarbeiter_id:
        schulungen = schulungen.filter(mitarbeiter_id=mitarbeiter_id)
    if teilgenommen:
        schulungen = schulungen.filter(teilgenommen=teilgenommen)
    if start:
        schulungen = schulungen.filter(datum_start__gte=start)
    if end:
        schulungen = schulungen.filter(datum_ende__lte=end)

    # 📄 Sayfalama
    paginator = Paginator(schulungen.order_by("-datum_start"), 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # ➕ / ✏️ Ekleme veya Güncelleme
    if request.method == "POST":
        data = request.POST
        edit_id = data.get("edit_id")

        schulung = Schulungskosten.objects.get(id=edit_id) if edit_id else Schulungskosten()

        schulung.schulungstyp = data.get("schulungstyp")
        schulung.datum_start = data.get("datum_start")
        schulung.datum_ende = data.get("datum_ende")
        schulung.dauer = data.get("dauer") or 0
        schulung.kosten = data.get("kosten") or 0
        schulung.anbieter = data.get("anbieter")
        schulung.teilgenommen = data.get("teilgenommen") or "-"
        schulung.beschreibung = data.get("beschreibung") or ""
        schulung.mitarbeiter_id = data.get("mitarbeiter_id")
        schulung.projekt_id = data.get("projekt_id") or None

        schulung.save()

        messages.success(request, "✅ Schulung gespeichert.")
        return redirect("admin_schulungskosten")

    return render(request, "admin_pages/admin_schulungskosten.html", {
        "schulungen": page_obj,
        "mitarbeiter": mitarbeiter,
        "projekte": projekte,
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_schulung_delete(request, id):
    eintrag = get_object_or_404(Schulungskosten, id=id)
    eintrag.delete()
    messages.success(request, "🗑️ Eintrag gelöscht.")
    return redirect("admin_schulungskosten")

def export_schulungskosten(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="schulungskosten.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(['Datum', 'Mitarbeiter', 'Typ', 'Kosten', 'Dauer', 'Teilgenommen'])

    queryset = Schulungskosten.objects.select_related('mitarbeiter')

    # Filtre uygula
    mitarbeiter_id = request.GET.get("mitarbeiter_id")
    teilgenommen = request.GET.get("teilgenommen")
    start = request.GET.get("start")
    end = request.GET.get("end")

    if mitarbeiter_id:
        queryset = queryset.filter(mitarbeiter_id=mitarbeiter_id)
    if teilgenommen:
        queryset = queryset.filter(teilgenommen=teilgenommen)
    if start:
        queryset = queryset.filter(datum_start__gte=start)
    if end:
        queryset = queryset.filter(datum_ende__lte=end)

    for eintrag in queryset:
        writer.writerow([
            eintrag.datum_start.strftime("%d.%m.%Y"),
            f"{eintrag.mitarbeiter.vorname} {eintrag.mitarbeiter.nachname}",
            eintrag.schulungstyp,
            eintrag.kosten,
            eintrag.dauer,
            eintrag.teilgenommen,
        ])

    return response



@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_abrechnung_view(request):
    projekte = Projekt.objects.all()
    mitarbeiter = Mitarbeiter.objects.all()
    abrechnungen = Abrechnung.objects.select_related("mitarbeiter", "projekt").all()

    # 🔍 Filtreleme
    monat = request.GET.get("monat")
    mitarbeiter_id = request.GET.get("mitarbeiter_id")
    projekt_id = request.GET.get("projekt_id")
    status = request.GET.get("status")

    if monat:
        abrechnungen = abrechnungen.filter(monat=monat)
    if mitarbeiter_id:
        abrechnungen = abrechnungen.filter(mitarbeiter_id=mitarbeiter_id)
    if projekt_id:
        abrechnungen = abrechnungen.filter(projekt_id=projekt_id)
    if status:
        abrechnungen = abrechnungen.filter(rechnung_status=status)

    # Sayfalama
    paginator = Paginator(abrechnungen, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # 🔁 POST: Ekleme veya Güncelleme
    if request.method == "POST":
        edit_id = request.POST.get("edit_id")
        monat = request.POST.get("monat")
        mitarbeiter_id = request.POST.get("mitarbeiter_id")
        projekt_id = request.POST.get("projekt_id") or None
        stunden = request.POST.get("stunden")
        stundensatz = request.POST.get("stundensatz")
        netto_summe = request.POST.get("netto_summe") or None
        brutto_summe = request.POST.get("brutto_summe") or None
        rechnung_status = request.POST.get("rechnung_status")
        zahlungseingang = request.POST.get("zahlungseingang") or None
        leistungsnachweis = request.POST.get("leistungsnachweis")
        bemerkung = request.POST.get("bemerkung")

        if not netto_summe and stunden and stundensatz:
            try:
                netto_summe = float(stunden) * float(stundensatz)
            except:
                netto_summe = 0

        if not brutto_summe:
            messages.warning(request, "⚠️ Bitte geben Sie die Brutto-Summe ein.")
            return redirect("admin_abrechnung")

        if monat and mitarbeiter_id and stunden and stundensatz:
            if edit_id:
                # GÜNCELLEME
                abrechnung = get_object_or_404(Abrechnung, id=edit_id)
                abrechnung.monat = monat
                abrechnung.mitarbeiter_id = mitarbeiter_id
                abrechnung.projekt_id = projekt_id
                abrechnung.stunden = stunden
                abrechnung.stundensatz = stundensatz
                abrechnung.netto_summe = netto_summe
                abrechnung.brutto_summe = brutto_summe
                abrechnung.rechnung_status = rechnung_status
                abrechnung.zahlungseingang = zahlungseingang
                abrechnung.leistungsnachweis = leistungsnachweis
                abrechnung.bemerkung = bemerkung
                abrechnung.save()
                messages.success(request, "✅ Abrechnung wurde aktualisiert.")
            else:
                # EKLEME
                Abrechnung.objects.create(
                    monat=monat,
                    mitarbeiter_id=mitarbeiter_id,
                    projekt_id=projekt_id,
                    stunden=stunden,
                    stundensatz=stundensatz,
                    netto_summe=netto_summe,
                    brutto_summe=brutto_summe,
                    rechnung_status=rechnung_status,
                    zahlungseingang=zahlungseingang,
                    leistungsnachweis=leistungsnachweis,
                    bemerkung=bemerkung
                )
                messages.success(request, "✅ Abrechnung erfolgreich gespeichert.")
        else:
            messages.warning(request, "⚠️ Bitte alle Pflichtfelder ausfüllen.")

        return redirect("admin_abrechnung")

    return render(request, "admin_pages/admin_abrechnung.html", {
        "abrechnungen": page_obj,
        "mitarbeiter": mitarbeiter,
        "projekte": projekte,
    })


# 🗑️ Silme
@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_abrechnung_delete(request, id):
    eintrag = get_object_or_404(Abrechnung, id=id)
    eintrag.delete()
    messages.success(request, "🗑️ Abrechnung wurde gelöscht.")
    return redirect("admin_abrechnung")


# 📤 Export CSV
@login_required
@user_passes_test(lambda u: u.is_superuser)
def export_abrechnung(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="abrechnungen.csv"'
    response.write('\ufeff')  # UTF-8 BOM for Excel

    writer = csv.writer(response)
    writer.writerow([
        'Monat', 'Mitarbeiter', 'Projekt', 'Stunden', 'Stundensatz', 'Netto', 'Brutto',
        'Rechnungsstatus', 'Zahlungseingang', 'Leistungsnachweis', 'Bemerkung'
    ])

    eintraege = Abrechnung.objects.select_related("mitarbeiter", "projekt")

    # Filtreler
    if request.GET.get("monat"):
        eintraege = eintraege.filter(monat=request.GET.get("monat"))
    if request.GET.get("mitarbeiter_id"):
        eintraege = eintraege.filter(mitarbeiter_id=request.GET.get("mitarbeiter_id"))
    if request.GET.get("projekt_id"):
        eintraege = eintraege.filter(projekt_id=request.GET.get("projekt_id"))
    if request.GET.get("status"):
        eintraege = eintraege.filter(rechnung_status=request.GET.get("status"))

    for a in eintraege:
        writer.writerow([
            a.monat,
            f"{a.mitarbeiter.vorname} {a.mitarbeiter.nachname}",
            a.projekt.projektname if a.projekt else "-",
            a.stunden,
            a.stundensatz,
            a.netto_summe,
            a.brutto_summe,
            a.rechnung_status,
            a.zahlungseingang.strftime("%d.%m.%Y") if a.zahlungseingang else "",
            a.leistungsnachweis,
            a.bemerkung or ""
        ])

    return response


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_reports_view(request):
    return render(request, "admin_pages/admin_reports.html")




@login_required
@user_passes_test(lambda u: u.groups.filter(name="Manager").exists())
def manager_dashboard_view(request):
    manager = request.user

    # 🔹 Sadece bu manager tarafından oluşturulan projeler
    eigene_projekte = Projekt.objects.filter(erstellt_von=manager)

    # 🔸 Proje sayısı
    total_projekte = eigene_projekte.count()

    # 🔸 Bu manager'ın oluşturduğu projelere atanan toplam çalışan sayısı
    total_mitarbeiter = ProjektMitarbeiter.objects.filter(projekt__in=eigene_projekte).values("mitarbeiter").distinct().count()

    return render(request, "manager_pages/manager_dashboard.html", {
        "total_projekte": total_projekte,
        "total_mitarbeiter": total_mitarbeiter,
        "projekte": eigene_projekte,
    })


@login_required
@user_passes_test(lambda u: u.groups.filter(name="Mitarbeiter").exists())
def mitarbeiter_dashboard_view(request):
    user = request.user

    # Mitarbeiter objesini bul
    try:
        mitarbeiter = Mitarbeiter.objects.get(user=user)
    except Mitarbeiter.DoesNotExist:
        return render(request, "mitarbeiter_pages/mitarbeiter_dashboard.html", {
            "error": "Mitarbeiterprofil nicht gefunden."
        })

    # Sadece kullanıcının dahil olduğu projeleri al
    eigene_projekte = Projekt.objects.filter(projektmitarbeiter__mitarbeiter=mitarbeiter).distinct()

    # Kendi Reiseberichte, Schulungskosten ve Abrechnungen kayıtları
    eigene_reisen = Reisebericht.objects.filter(mitarbeiter=mitarbeiter)
    eigene_schulungen = Schulungskosten.objects.filter(mitarbeiter=mitarbeiter)
    eigene_abrechnungen = Abrechnung.objects.filter(mitarbeiter=mitarbeiter)

    return render(request, "mitarbeiter_pages/mitarbeiter_dashboard.html", {
        "projekte": eigene_projekte,
        "reisen": eigene_reisen,
        "schulungen": eigene_schulungen,
        "abrechnungen": eigene_abrechnungen,
    })


def custom_404(request, exception):
    return render(request, 'error_pages/404.html', status=404)

def custom_500(request):
    return render(request, 'error_pages/500.html', status=500)

def custom_403(request, exception):
    return render(request, 'error_pages/403.html', status=403)


@login_required
def profil_view(request):
    benutzerprofil, created = BenutzerProfil.objects.get_or_create(benutzer=request.user)

    if request.method == "POST":
        benutzer_form = BenutzerForm(request.POST, instance=request.user)
        profil_form = BenutzerProfilForm(request.POST, request.FILES, instance=benutzerprofil)

        if benutzer_form.is_valid() and profil_form.is_valid():
            benutzer_form.save()
            profil_form.save()

            # 📌 Yapılan değişiklikleri geçmişte kaydet
            update_change_reason(benutzerprofil, "Profil wurde aktualisiert.")
            benutzerprofil.save()

            # 📌 Kullanıcıya başarı mesajı göster
            messages.success(request, "Ihr Profil wurde erfolgreich aktualisiert!")

            # ✅ Kullanıcının rolüne göre yönlendirme yap
            if request.user.is_superuser:
                return redirect('/admin-dashboard/')
            elif request.user.groups.filter(name="Manager").exists():
                return redirect('/manager/')
            else:
                return redirect('/mitarbeiter/')

    else:
        benutzer_form = BenutzerForm(instance=request.user)
        profil_form = BenutzerProfilForm(instance=benutzerprofil)

    return render(request, "profil.html", {
        "benutzer_form": benutzer_form,
        "profil_form": profil_form
    })


@login_required
def projekt_team_view(request, projekt_id):
    projekt = Projekt.objects.get(id=projekt_id)
    mitarbeiter_liste = Mitarbeiter.objects.filter(projekt=projekt)  # 📌 Bu projedeki çalışanları getir

    return render(request, "projekt_team.html", {
        "projekt": projekt,
        "mitarbeiter_liste": mitarbeiter_liste
    })


def custom_logout_view(request):
    """🚀 Logout işlemi, tüm kullanıcıları login sayfasına yönlendirir."""
    logout(request)
    return redirect('/login/')


def export_finanzbericht(request):
    """ 📤 Finanzübersicht verilerini CSV olarak indir """
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="finanzbericht.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(['Projekt', 'Mitarbeiter', 'Kosten', 'Datum'])

    for eintrag in Reisebericht.objects.all():
        writer.writerow([eintrag.projekt.projektname, 
                         f"{eintrag.mitarbeiter.vorname} {eintrag.mitarbeiter.nachname}", 
                         eintrag.gesamtkosten, 
                         eintrag.datum])

    return response

    
def export_projektbericht(request):
    """ 📤 Proje verilerini CSV olarak indir """
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="projektbericht.csv"'
    response.write('\ufeff')

    writer = csv.writer(response)
    writer.writerow(['Projektname', 'Kunde', 'Startdatum', 'Enddatum', 'Status'])

    for projekt in Projekt.objects.all():
        writer.writerow([projekt.projektname, 
                         projekt.kunde_1, 
                         projekt.startdatum, 
                         projekt.enddatum, 
                         projekt.status])

    return response