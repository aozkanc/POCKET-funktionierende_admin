from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login, logout
from rest_framework import viewsets
from .models import Mitarbeiter, Projekt, Abrechnung, Reisebericht, Schulungskosten, Abordnung, ProjektMitarbeiter, Einnahme
from .serializers import MitarbeiterSerializer, ProjektSerializer, AbrechnungSerializer, ReiseberichtSerializer, SchulungskostenSerializer, AbordnungSerializer, EinnahmeSerializer
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.views import ObtainAuthToken
from django.utils.decorators import method_decorator
from .forms import BenutzerForm, BenutzerProfilForm
from django.contrib import messages
from simple_history.utils import update_change_reason
from core.models import BenutzerProfil
from django.db.models import Count, Q
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

class EinnahmeViewSet(viewsets.ModelViewSet):
    queryset = Einnahme.objects.all()
    serializer_class = EinnahmeSerializer

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
    # 🔢 Genel toplam sayılar (sadece projeye bağlı olanlar)
    total_projekte = Projekt.objects.count()
    total_mitarbeiter = Mitarbeiter.objects.count()
    total_abordnungen = Abordnung.objects.count()
    total_reisen = Reisebericht.objects.filter(projekt__isnull=False).count()
    total_schulungen = Schulungskosten.objects.filter(projekt__isnull=False).count()
    total_abrechnungen = Abrechnung.objects.filter(projekt__isnull=False).count()

    # 💸 Gider hesapları (SADECE proje bağlantılı veriler)
    total_abrechnung = Abrechnung.objects.filter(projekt__isnull=False).aggregate(s=Sum("brutto_summe"))["s"] or 0
    total_reise = Reisebericht.objects.filter(projekt__isnull=False).aggregate(s=Sum("kosten_fahrt"))["s"] or 0
    total_hotel = Reisebericht.objects.filter(projekt__isnull=False).aggregate(s=Sum("kosten_übernachtung"))["s"] or 0
    total_schulung = Schulungskosten.objects.filter(projekt__isnull=False).aggregate(s=Sum("kosten"))["s"] or 0

    total_kosten = total_abrechnung + total_reise + total_hotel + total_schulung

    # 💰 Gelir (zaten proje bağlı)
    total_einnahmen = Einnahme.objects.aggregate(s=Sum("betrag"))["s"] or 0
    total_einnahmen_count = Einnahme.objects.count()

    # 💹 Kar
    nettogewinn = total_einnahmen - total_kosten

    # 📊 Grafik: Einnahmen vs Kosten
    einnahme_vs_kosten_data = {
        "Einnahmen": float(total_einnahmen),
        "Kosten": float(total_kosten),
    }

    # 📊 Grafik: Gider Kategorileri
    category_data = {
        "Abrechnung": float(total_abrechnung),
        "Reise": float(total_reise + total_hotel),
        "Schulung": float(total_schulung),
    }

    # 🔁 Artık "allgemeine_kosten" yok!
    # "projekt_vs_allgemein_data" gibi grafiklere gerek yok

    # 📦 Template'e gönderilecek context
    context = {
        "total_projekte": total_projekte,
        "total_mitarbeiter": total_mitarbeiter,
        "total_abordnungen": total_abordnungen,
        "total_reisen": total_reisen,
        "total_schulungen": total_schulungen,
        "total_abrechnungen": total_abrechnungen,
        "total_einnahmen_count": total_einnahmen_count,
        "total_einnahmen": total_einnahmen,
        "total_kosten": total_kosten,
        "nettogewinn": nettogewinn,
        "einnahme_vs_kosten_data": einnahme_vs_kosten_data,
        "category_data": category_data,
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

    # 🔢 Verileri getir
    abrechnung = Abrechnung.objects.all()
    reisen = Reisebericht.objects.all()
    schulungen = Schulungskosten.objects.all()
    einnahmen_qs = Einnahme.objects.all()

    # 💸 Giderler
    total_abrechnung = abrechnung.aggregate(s=Sum('brutto_summe'))['s'] or 0
    total_reise = reisen.aggregate(s=Sum('kosten_fahrt'))['s'] or 0
    total_hotel = reisen.aggregate(s=Sum('kosten_übernachtung'))['s'] or 0
    total_schulung = schulungen.aggregate(s=Sum('kosten'))['s'] or 0
    total_kosten = total_abrechnung + total_reise + total_hotel + total_schulung

    # 💰 Gelir
    total_einnahmen = einnahmen_qs.aggregate(s=Sum('betrag'))['s'] or 0

    # 📈 Net kar
    nettogewinn = total_einnahmen - total_kosten

    # 📤 CSV satırları
    writer.writerow(['Abrechnung', f"{total_abrechnung:.2f}"])
    writer.writerow(['Reise (Fahrt + Hotel)', f"{(total_reise + total_hotel):.2f}"])
    writer.writerow(['Schulung', f"{total_schulung:.2f}"])
    writer.writerow(['Einnahmen', f"{total_einnahmen:.2f}"])
    writer.writerow(['Gesamtkosten', f"{total_kosten:.2f}"])
    writer.writerow(['Nettogewinn', f"{nettogewinn:.2f}"])

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
                    beschreibung=beschreibung,
                    erstellt_von=request.user  # 👈 eksikti!
                )
                messages.success(request, "✅ Projekt erfolgreich gespeichert.")
        else:
            messages.warning(request, "⚠️ Bitte alle Pflichtfelder ausfüllen.")

        return redirect("admin_projekte")

    # ✅ GET (Listeleme ve Filtreleme)
    projekte = Projekt.objects.all()

    # 🔍 Filtreleme
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
    response.write('\ufeff')  # Excel uyumu için BOM karakteri

    writer = csv.writer(response)
    writer.writerow([
        'Projektname', 'Kunde 1', 'Startdatum', 'Enddatum', 'Budget',
        'Einnahmen (€)', 'Ausgaben (€)', 'Gewinn (€)', 'Status'
    ])

    projekte = Projekt.objects.all()

    # 🔍 Filtreler (isteğe bağlı)
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

    # 📤 Verileri yaz
    for p in projekte:
        writer.writerow([
            p.projektname,
            p.kunde_1,
            p.startdatum.strftime("%d.%m.%Y"),
            p.enddatum.strftime("%d.%m.%Y"),
            float(p.budget),
            float(p.get_total_einnahmen()),
            float(p.get_total_ausgaben()),
            float(p.get_gewinn()),
            p.status
        ])

    return response


@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_einnahmen_view(request):
    einnahmen = Einnahme.objects.select_related("projekt").all()
    projekte = Projekt.objects.all()

    # 🔍 Filtreleme
    projekt_id = request.GET.get("projekt_id")
    start = request.GET.get("start")
    end = request.GET.get("end")
    status = request.GET.get("status")

    if projekt_id:
        einnahmen = einnahmen.filter(projekt_id=projekt_id)
    if start:
        einnahmen = einnahmen.filter(zahlungseingang__gte=start)
    if end:
        einnahmen = einnahmen.filter(zahlungseingang__lte=end)
    if status:
        einnahmen = einnahmen.filter(status=status)

    # 📄 Sayfalama
    paginator = Paginator(einnahmen.order_by("-zahlungseingang"), 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # ➕ / ✏️ Ekleme veya Güncelleme
    if request.method == "POST":
        data = request.POST
        edit_id = data.get("edit_id")

        einnahme = Einnahme.objects.get(id=edit_id) if edit_id else Einnahme()
        einnahme.projekt_id = data.get("projekt_id")
        einnahme.betrag = data.get("betrag")
        einnahme.zahlungseingang = data.get("zahlungseingang") or None
        einnahme.zahlungsart = data.get("zahlungsart")
        einnahme.rechnungsnummer = data.get("rechnungsnummer")
        einnahme.status = data.get("status")
        einnahme.erstellt_von = request.user

        einnahme.save()

        if edit_id:
            messages.success(request, "✅ Einnahme wurde aktualisiert.")
        else:
            messages.success(request, "✅ Einnahme wurde erfolgreich gespeichert.")

        return redirect("admin_einnahmen")

    return render(request, "admin_pages/admin_einnahmen.html", {
        "einnahmen": page_obj,
        "projekte": projekte,
    })

@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_einnahme_delete(request, id):
    einnahme = get_object_or_404(Einnahme, id=id)
    einnahme.delete()
    messages.success(request, "🗑️ Einnahme wurde gelöscht.")
    return redirect("admin_einnahmen")

@login_required
@user_passes_test(lambda u: u.is_superuser)
def export_einnahmen(request):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="einnahmen.csv"'
    response.write('\ufeff')  # UTF-8 BOM

    writer = csv.writer(response)
    writer.writerow(['Projekt', 'Betrag (€)', 'Zahlungseingang', 'Zahlungsart', 'Rechnungsnummer', 'Status'])

    einnahmen = Einnahme.objects.select_related("projekt").all()

    # 🔍 Filtre uygulama
    projekt_id = request.GET.get("projekt_id")
    start = request.GET.get("start")
    end = request.GET.get("end")
    status = request.GET.get("status")

    if projekt_id:
        einnahmen = einnahmen.filter(projekt_id=projekt_id)
    if start:
        einnahmen = einnahmen.filter(zahlungseingang__gte=start)
    if end:
        einnahmen = einnahmen.filter(zahlungseingang__lte=end)
    if status:
        einnahmen = einnahmen.filter(status=status)

    for e in einnahmen:
        writer.writerow([
            e.projekt.projektname,
            f"{e.betrag:.2f}",
            e.zahlungseingang.strftime("%d.%m.%Y") if e.zahlungseingang else "-",
            e.zahlungsart,
            e.rechnungsnummer or "-",
            e.status,
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

        # ❗ Zorunlu alan ve geçerli seçim kontrolleri
        if not all([vorname, nachname, standort, erste_taetigkeitsstaette, abteilung, status, rolle]):
            messages.warning(request, "⚠️ Bitte alle Felder ausfüllen.")
            return redirect("admin_mitarbeiter")

        if rolle == "-" or status == "-":
            messages.warning(request, "⚠️ Bitte wählen Sie eine gültige Rolle und einen gültigen Status aus.")
            return redirect("admin_mitarbeiter")

        if edit_id:
            # 🔄 GÜNCELLEME
            mitarbeiter = get_object_or_404(Mitarbeiter, id=edit_id)
            mitarbeiter.vorname = vorname
            mitarbeiter.nachname = nachname
            mitarbeiter.standort = standort
            mitarbeiter.erste_taetigkeitsstaette = erste_taetigkeitsstaette
            mitarbeiter.abteilung = abteilung
            mitarbeiter.status = status
            mitarbeiter.rolle = rolle
            mitarbeiter.save()
            messages.success(request, "✅ Mitarbeiter wurde aktualisiert.")
        else:
            # ➕ YENİ KAYIT
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

        return redirect("admin_mitarbeiter")

    # ✅ GET: Listeleme + Filtre
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
        mitarbeiter = mitarbeiter.filter(rolle=rolle)
    if abteilung:
        mitarbeiter = mitarbeiter.filter(abteilung__icontains=abteilung)
    if status:
        mitarbeiter = mitarbeiter.filter(status=status)

    paginator = Paginator(mitarbeiter, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(request, "admin_pages/admin_mitarbeiter.html", {
        "mitarbeiter": page_obj,
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




# Manager kontrolü
def is_manager(user):
    return user.groups.filter(name="Manager").exists()

@login_required
@user_passes_test(is_manager)
def manager_dashboard_view(request):
    user = request.user
    
    # Projeyi oluşturan manager ve atanmış manager'lar
    eigene_projekte = Projekt.objects.filter(erstellt_von=user)  # Yalnızca manager tarafından oluşturulan projeler
    zugewiesene_projekte = Projekt.objects.filter(manager=user)  # Manager'ın atandığı projeler

    # Her iki projeyi birleştir
    projekte = eigene_projekte | zugewiesene_projekte
    
    # İlgili proje ID'leri
    projekte_ids = projekte.values_list('id', flat=True)

    # 📊 Sayılar
    total_projekte = projekte.count()
    total_abrechnungen = Abrechnung.objects.filter(projekt__in=projekte_ids).count()
    total_reisen = Reisebericht.objects.filter(projekt__in=projekte_ids).count()
    total_schulungen = Schulungskosten.objects.filter(projekt__in=projekte_ids).count()
    total_einnahmen = Einnahme.objects.filter(projekt__in=projekte_ids).aggregate(s=Sum("betrag"))["s"] or 0
    total_abordnungen = Abordnung.objects.filter(projekt__in=projekte_ids).count()

    # Gider hesapları
    total_abrechnung = Abrechnung.objects.filter(projekt__in=projekte_ids).aggregate(s=Sum("brutto_summe"))["s"] or 0
    total_reise = Reisebericht.objects.filter(projekt__in=projekte_ids).aggregate(s=Sum("kosten_fahrt"))["s"] or 0
    total_hotel = Reisebericht.objects.filter(projekt__in=projekte_ids).aggregate(s=Sum("kosten_übernachtung"))["s"] or 0
    total_schulung = Schulungskosten.objects.filter(projekt__in=projekte_ids).aggregate(s=Sum("kosten"))["s"] or 0

    total_kosten = total_abrechnung + total_reise + total_hotel + total_schulung
    nettogewinn = total_einnahmen - total_kosten

    # Grafik verileri
    category_data = {
        "Abrechnung": float(total_abrechnung),
        "Reise": float(total_reise + total_hotel),
        "Schulung": float(total_schulung),
    }

    einnahme_vs_kosten_data = {
        "Einnahmen": float(total_einnahmen),
        "Kosten": float(total_kosten),
    }

    context = {
        "total_projekte": total_projekte,
        "total_abrechnungen": total_abrechnungen,
        "total_reisen": total_reisen,
        "total_schulungen": total_schulungen,
        "total_abordnungen": total_abordnungen,
        "total_einnahmen": total_einnahmen,
        "total_kosten": total_kosten,
        "nettogewinn": nettogewinn,
        "category_data": category_data,
        "einnahme_vs_kosten_data": einnahme_vs_kosten_data,
    }

    return render(request, "manager_pages/manager_dashboard.html", context)


# @login_required
# @user_passes_test(is_manager)
# def manager_projekte_view(request):
#     user = request.user
    
#     # Kullanıcının yönetiminde olan projeler: hem kendi oluşturduğu hem de atanmış olduğu projeler
#     projekte = Projekt.objects.filter(Q(erstellt_von=user) | Q(manager=user))

#         # Eğer "meine_projekte" seçeneği işaretliyse, sadece manager'ın oluşturduğu projeleri göster
#     if request.GET.get('meine_projekte'):
#         projekte = projekte.filter(erstellt_von=user)

#     # 🔍 Filtreleme
#     projektname = request.GET.get("projektname")
#     kunde_1 = request.GET.get("kunde")
#     startdatum = request.GET.get("start")
#     enddatum = request.GET.get("end")
#     status = request.GET.get("status")

#     if projektname:
#         projekte = projekte.filter(projektname__icontains=projektname)
#     if kunde_1:
#         projekte = projekte.filter(kunde_1__icontains=kunde_1)
#     if startdatum:
#         projekte = projekte.filter(startdatum__gte=startdatum)
#     if enddatum:
#         projekte = projekte.filter(enddatum__lte=enddatum)
#     if status:
#         projekte = projekte.filter(status__icontains=status)

#     # Sayfalama
#     paginator = Paginator(projekte, 10)
#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)

#     # POST işlemi (Güncelleme / Ekleme)
#     if request.method == "POST":
#         edit_id = request.POST.get("edit_id")
#         projektname = request.POST.get("projektname")
#         startdatum = request.POST.get("startdatum")
#         enddatum = request.POST.get("enddatum")
#         budget = request.POST.get("budget")
#         kunde_1 = request.POST.get("kunde_1")
#         kunde_2 = request.POST.get("kunde_2")
#         projekttyp = request.POST.get("projekttyp")
#         status = request.POST.get("status")
#         beschreibung = request.POST.get("beschreibung")

#         if projektname and startdatum and enddatum and budget and kunde_1 and projekttyp and status:
#             if edit_id:
#                 # 🔄 Güncelleme
#                 projekt = get_object_or_404(Projekt, id=edit_id, erstellt_von=user)
#                 projekt.projektname = projektname
#                 projekt.startdatum = startdatum
#                 projekt.enddatum = enddatum
#                 projekt.budget = budget
#                 projekt.kunde_1 = kunde_1
#                 projekt.kunde_2 = kunde_2
#                 projekt.projekttyp = projekttyp
#                 projekt.status = status
#                 projekt.beschreibung = beschreibung
#                 projekt.save()
#                 messages.success(request, "✅ Projekt wurde aktualisiert.")
#             else:
#                 # ➕ Yeni Kayıt
#                 projekt = Projekt.objects.create(
#                     projektname=projektname,
#                     startdatum=startdatum,
#                     enddatum=enddatum,
#                     budget=budget,
#                     kunde_1=kunde_1,
#                     kunde_2=kunde_2,
#                     projekttyp=projekttyp,
#                     status=status,
#                     beschreibung=beschreibung,
#                     erstellt_von=user
#                 )
#                 # Manager olarak projeyi kendisine atama
#                 projekt.manager.add(user)
#                 messages.success(request, "✅ Projekt erfolgreich gespeichert.")
#         else:
#             messages.warning(request, "⚠️ Bitte alle Pflichtfelder ausfüllen.")

#         return redirect("manager_projekte")

#     return render(request, "manager_pages/manager_projekte.html", {
#         "projekte": page_obj,
#     })


# @login_required
# @user_passes_test(is_manager)
# def manager_projekte_delete(request, id):
#     # Projeyi bul
#     projekt = get_object_or_404(Projekt, id=id)

#     # Projeyi sadece onu oluşturan kullanıcı silebilir
#     if projekt.erstellt_von != request.user:
#         messages.error(request, "❗ Sie können nur Ihre eigenen Projekte löschen!")
#         return redirect("manager_projekte")

#     # Projeyi sil
#     projekt.delete()
#     messages.success(request, "🗑️ Projekt wurde erfolgreich gelöscht.")
#     return redirect("manager_projekte")

# @login_required
# @user_passes_test(is_manager)
# def manager_projekte_export(request):
#     user = request.user

#     # Kullanıcının oluşturduğu ve atanmış olduğu projeler
#     projekte = Projekt.objects.filter(Q(erstellt_von=user) | Q(manager=user))

#     # CSV formatında bir response oluşturuyoruz
#     response = HttpResponse(content_type='text/csv; charset=utf-8')
#     response['Content-Disposition'] = 'attachment; filename="projekte.csv"'
#     response.write('\ufeff')  # UTF-8 BOM karakteri ekliyoruz

#     writer = csv.writer(response)
#     writer.writerow(['Projektname', 'Kunde 1', 'Startdatum', 'Enddatum', 'Budget', 'Status', 'Beschreibung'])

#     # Projeleri yazıyoruz
#     for projekt in projekte:
#         writer.writerow([projekt.projektname, projekt.kunde_1, projekt.startdatum.strftime('%d.%m.%Y'),
#                          projekt.enddatum.strftime('%d.%m.%Y'), projekt.budget, projekt.status, projekt.beschreibung])

#     return response


# @login_required
# @user_passes_test(is_manager)
# def manager_abordnungen_view(request):
#     user = request.user

#     # Manager'ın oluşturduğu projeleri alıyoruz
#     eigene_projekte = Projekt.objects.filter(erstellt_von=user)

#     # Manager'ın atanmış olduğu projeleri alıyoruz
#     zugewiesene_projekte = Projekt.objects.filter(manager=user)

#     # Kendi oluşturduğu ve atanmış olduğu projeleri birleştiriyoruz
#     projekte = Projekt.objects.filter(Q(erstellt_von=user) | Q(manager=user))

#     # Sayfalama için Abordnungen
#     aborderungen = Abordnung.objects.filter(projekt__in=projekte)

#     # 🔍 Filtreleme
#     mitarbeiter_id = request.GET.get('mitarbeiter_id')
#     projekt_id = request.GET.get('projekt_id')
#     start = request.GET.get('start')
#     end = request.GET.get('end')

#     if mitarbeiter_id:
#         aborderungen = aborderungen.filter(mitarbeiter_id=mitarbeiter_id)
#     if projekt_id:
#         aborderungen = aborderungen.filter(projekt_id=projekt_id)
#     if start:
#         aborderungen = aborderungen.filter(zeitraum_start__gte=start)
#     if end:
#         aborderungen = aborderungen.filter(zeitraum_ende__lte=end)

#     # Sayfalama
#     paginator = Paginator(aborderungen, 10)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

#     # POST işlemi (Ekleme / Güncelleme)
#     if request.method == 'POST':
#         mitarbeiter = request.POST.get('mitarbeiter')
#         projekt_id = request.POST.get('projekt')
#         zeitraum_start = request.POST.get('zeitraum_start')
#         zeitraum_ende = request.POST.get('zeitraum_ende')
#         edit_id = request.POST.get('edit_id')

#         # Yalnızca kendi oluşturduğu projelere Abordnung yapılabilir
#         if not Projekt.objects.filter(id=projekt_id, erstellt_von=user).exists():
#             messages.error(request, "❌ Sie können nur Abordnungen zu Ihren eigenen Projekten erstellen/bearbeiten.")
#             return redirect("manager_abordnungen")

#         if edit_id:
#             abordnung = get_object_or_404(Abordnung, id=edit_id)

#             if abordnung.projekt.erstellt_von != user:
#                 messages.error(request, "❌ Sie können nur Ihre eigenen Abordnungen bearbeiten.")
#                 return redirect("manager_abordnungen")

#             abordnung.mitarbeiter_id = mitarbeiter
#             abordnung.projekt_id = projekt_id
#             abordnung.zeitraum_start = zeitraum_start
#             abordnung.zeitraum_ende = zeitraum_ende
#             abordnung.save()
#             messages.success(request, "✅ Abordnung erfolgreich aktualisiert.")
#         else:
#             Abordnung.objects.create(
#                 mitarbeiter_id=mitarbeiter,
#                 projekt_id=projekt_id,
#                 zeitraum_start=zeitraum_start,
#                 zeitraum_ende=zeitraum_ende
#             )
#             messages.success(request, "✅ Abordnung erfolgreich gespeichert.")

#         return redirect('manager_abordnungen')

#     return render(request, 'manager_pages/manager_abordnungen.html', {
#         'aborderungen': page_obj,
#         'projekte': projekte,
#         'mitarbeiter_list': Mitarbeiter.objects.all(),  # Tüm çalışanlar
#     })

# @login_required
# @user_passes_test(is_manager)
# def manager_abordnungen_delete(request, id):
#     user = request.user
#     abordnung = get_object_or_404(Abordnung, id=id)

#     if abordnung.projekt.erstellt_von != user:
#         messages.error(request, "❌ Sie können nur Ihre eigenen Abordnungen löschen.")
#         return redirect("manager_abordnungen")

#     abordnung.delete()
#     messages.success(request, "🗑️ Abordnung wurde gelöscht.")
#     return redirect("manager_abordnungen")

# @login_required
# @user_passes_test(is_manager)
# def manager_abordnungen_export(request):
#     user = request.user

#     # Sadece erişilebilir projeler için export
#     projekte_ids = Projekt.objects.filter(Q(erstellt_von=user) | Q(manager=user)).values_list('id', flat=True)
#     aborderungen = Abordnung.objects.filter(projekt__in=projekte_ids)

#     response = HttpResponse(content_type='text/csv; charset=utf-8')
#     response['Content-Disposition'] = 'attachment; filename="abordnungen.csv"'
#     response.write('\ufeff')  # UTF-8 BOM

#     writer = csv.writer(response)
#     writer.writerow(['Mitarbeiter', 'Projekt', 'Zeitraum Start', 'Zeitraum Ende'])

#     for abordnung in aborderungen:
#         writer.writerow([
#             str(abordnung.mitarbeiter),
#             str(abordnung.projekt),
#             abordnung.zeitraum_start.strftime('%d.%m.%Y'),
#             abordnung.zeitraum_ende.strftime('%d.%m.%Y')
#         ])

#     return response



# @login_required
# @user_passes_test(is_manager)
# def manager_schulungskosten_view(request):
#     user = request.user

#     # Kullanıcının oluşturduğu veya atandığı projelere ait Schulungskosten
#     projekte = Projekt.objects.filter(Q(erstellt_von=user) | Q(manager=user))
#     projekte_ids = projekte.values_list("id", flat=True)

#     schulungskosten = Schulungskosten.objects.filter(projekt__in=projekte_ids)

#     # 🔍 Filtreleme
#     projektname = request.GET.get("projektname")
#     mitarbeiter = request.GET.get("mitarbeiter")
#     start = request.GET.get("start")
#     end = request.GET.get("end")

#     if projektname:
#         schulungskosten = schulungskosten.filter(projekt__projektname__icontains=projektname)
#     if mitarbeiter:
#         schulungskosten = schulungskosten.filter(
#             Q(mitarbeiter__vorname__icontains=mitarbeiter) |
#             Q(mitarbeiter__nachname__icontains=mitarbeiter)
#         )
#     if start:
#         schulungskosten = schulungskosten.filter(datum_start__gte=start)
#     if end:
#         schulungskosten = schulungskosten.filter(datum_ende__lte=end)

#     # ➕ / ✏️ POST işlemleri
#     if request.method == "POST":
#         edit_id = request.POST.get("edit_id")

#         mitarbeiter_id = request.POST.get("mitarbeiter")
#         projekt_id = request.POST.get("projekt")
#         schulungstyp = request.POST.get("schulungstyp")
#         datum_start = request.POST.get("datum_start")
#         datum_ende = request.POST.get("datum_ende")
#         dauer = request.POST.get("dauer")
#         kosten = request.POST.get("kosten")
#         anbieter = request.POST.get("anbieter")
#         teilgenommen = request.POST.get("teilgenommen")
#         beschreibung = request.POST.get("beschreibung")

#         # 🛡️ Yetki kontrolü: sadece kendi oluşturduğu projelere kayıt yapılabilir
#         if not Projekt.objects.filter(id=projekt_id, erstellt_von=user).exists():
#             messages.error(request, "❌ Nur eigene Projekte können bearbeitet oder ergänzt werden.")
#             return redirect("manager_schulungskosten")

#         if edit_id:
#             # ✏️ Güncelleme
#             eintrag = get_object_or_404(Schulungskosten, id=edit_id, projekt__erstellt_von=user)
#             eintrag.mitarbeiter_id = mitarbeiter_id
#             eintrag.projekt_id = projekt_id
#             eintrag.schulungstyp = schulungstyp
#             eintrag.datum_start = datum_start
#             eintrag.datum_ende = datum_ende
#             eintrag.dauer = dauer
#             eintrag.kosten = kosten
#             eintrag.anbieter = anbieter
#             eintrag.teilgenommen = teilgenommen
#             eintrag.beschreibung = beschreibung
#             eintrag.save()
#             messages.success(request, "✅ Schulungskosten wurden aktualisiert.")
#         else:
#             # ➕ Yeni kayıt
#             Schulungskosten.objects.create(
#                 mitarbeiter_id=mitarbeiter_id,
#                 projekt_id=projekt_id,
#                 schulungstyp=schulungstyp,
#                 datum_start=datum_start,
#                 datum_ende=datum_ende,
#                 dauer=dauer,
#                 kosten=kosten,
#                 anbieter=anbieter,
#                 teilgenommen=teilgenommen,
#                 beschreibung=beschreibung
#             )
#             messages.success(request, "✅ Schulungskosten wurden erfolgreich gespeichert.")

#         return redirect("manager_schulungskosten")

#     # Sayfalama
#     paginator = Paginator(schulungskosten, 10)
#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)

#     return render(request, "manager_pages/manager_schulungskosten.html", {
#         "schulungskosten": page_obj,
#         "projekte": projekte  # dropdownlarda kullanılabilir
#     })


# @login_required
# @user_passes_test(is_manager)
# def manager_schulungskosten_delete(request, id):
#     user = request.user

#     # Silme yetkisi sadece kendi oluşturduğu projeye ait kayıtlarda geçerlidir
#     schulung = get_object_or_404(Schulungskosten, id=id)

#     if schulung.projekt.erstellt_von != user:
#         messages.error(request, "❌ Sie dürfen nur Schulungskosten Ihrer eigenen Projekte löschen.")
#         return redirect("manager_schulungskosten")

#     schulung.delete()
#     messages.success(request, "🗑️ Schulungskosten wurden erfolgreich gelöscht.")
#     return redirect("manager_schulungskosten")


# @login_required
# @user_passes_test(is_manager)
# def manager_schulungskosten_export(request):
#     user = request.user

#     # Manager'ın oluşturduğu ve atandığı projeler
#     projekte = Projekt.objects.filter(Q(erstellt_von=user) | Q(manager=user))
#     schulungskosten = Schulungskosten.objects.filter(projekt__in=projekte)

#     response = HttpResponse(content_type='text/csv; charset=utf-8')
#     response['Content-Disposition'] = 'attachment; filename="schulungskosten.csv"'
#     response.write('\ufeff')  # Excel uyumluluğu için BOM

#     writer = csv.writer(response)
#     writer.writerow([
#         "Projektname", "Mitarbeiter", "Schulungstyp", "Startdatum", "Enddatum",
#         "Dauer (Stunden)", "Kosten (€)", "Anbieter", "Teilgenommen", "Beschreibung"
#     ])

#     for s in schulungskosten:
#         writer.writerow([
#             s.projekt.projektname,
#             f"{s.mitarbeiter.vorname} {s.mitarbeiter.nachname}",
#             s.schulungstyp,
#             s.datum_start.strftime('%d.%m.%Y'),
#             s.datum_ende.strftime('%d.%m.%Y'),
#             s.dauer,
#             s.kosten,
#             s.anbieter,
#             s.teilgenommen,
#             s.beschreibung or ""
#         ])

#     return response


# @login_required
# @user_passes_test(is_manager)
# def manager_abrechnung_view(request):
#     user = request.user

#     # Manager'ın oluşturduğu projeler ve atandığı projeler
#     projekte = Projekt.objects.filter(Q(erstellt_von=user) | Q(manager=user))

#     # Tabloda gösterilecek Abrechnung'lar: hem kendi oluşturduğu projeler, hem de atandığı projelerdeki Abrechnung'lar
#     projekte_ids = projekte.values_list("id", flat=True)
#     abrechnungen = Abrechnung.objects.filter(projekt__in=projekte_ids)

#     # 🔍 Filtreleme işlemleri
#     mitarbeiter_id = request.GET.get("mitarbeiter_id")
#     projekt_id = request.GET.get("projekt_id")
#     monat = request.GET.get("monat")
#     stunden_min = request.GET.get("stunden_min")
#     netto_summe_min = request.GET.get("netto_summe_min")

#     if mitarbeiter_id:
#         abrechnungen = abrechnungen.filter(mitarbeiter_id=mitarbeiter_id)
#     if projekt_id:
#         abrechnungen = abrechnungen.filter(projekt_id=projekt_id)
#     if monat:
#         abrechnungen = abrechnungen.filter(monat__icontains=monat)
#     if stunden_min:
#         abrechnungen = abrechnungen.filter(stunden__gte=stunden_min)
#     if netto_summe_min:
#         abrechnungen = abrechnungen.filter(netto_summe__gte=netto_summe_min)

#     # Sayfalama
#     paginator = Paginator(abrechnungen, 10)
#     page_number = request.GET.get("page")
#     page_obj = paginator.get_page(page_number)

#     # POST işlemi (Ekleme ve Güncelleme)
#     if request.method == "POST":
#         mitarbeiter_id = request.POST.get("mitarbeiter")
#         projekt_id = request.POST.get("projekt")
#         monat = request.POST.get("monat")
#         stunden = request.POST.get("stunden")
#         stundensatz = request.POST.get("stundensatz")
#         rechnung_status = request.POST.get("rechnung_status")
#         zahlungseingang = request.POST.get("zahlungseingang")
#         leistungsnachweis = request.POST.get("leistungsnachweis")
#         bemerkung = request.POST.get("bemerkung")
#         edit_id = request.POST.get("edit_id")

#         # Yalnızca kendi projelerine Abrechnung eklenebilir
#         if not Projekt.objects.filter(id=projekt_id, erstellt_von=user).exists():
#             messages.error(request, "❌ Sie dürfen nur Abrechnungen zu Ihren eigenen Projekten hinzufügen oder bearbeiten.")
#             return redirect("manager_abrechnung")

#         # Gereklilikler
#         if mitarbeiter_id and monat and stunden and stundensatz:
#             try:
#                 stunden = float(stunden)
#                 stundensatz = float(stundensatz)
#                 netto_summe = stunden * stundensatz
#                 brutto_summe = round(netto_summe * 1.19, 2)  # varsayılan %19 KDV
#             except ValueError:
#                 messages.error(request, "❌ Ungültige Zahl für Stunden oder Stundensatz.")
#                 return redirect("manager_abrechnung")

#             if edit_id:
#                 # Güncelleme işlemi
#                 abrechnung = get_object_or_404(Abrechnung, id=edit_id, projekt__in=projekte)
#                 abrechnung.mitarbeiter_id = mitarbeiter_id
#                 abrechnung.projekt_id = projekt_id
#                 abrechnung.monat = monat
#                 abrechnung.stunden = stunden
#                 abrechnung.stundensatz = stundensatz
#                 abrechnung.netto_summe = netto_summe
#                 abrechnung.brutto_summe = brutto_summe
#                 abrechnung.rechnung_status = rechnung_status
#                 abrechnung.zahlungseingang = zahlungseingang or None
#                 abrechnung.leistungsnachweis = leistungsnachweis
#                 abrechnung.bemerkung = bemerkung
#                 abrechnung.save()
#                 messages.success(request, "✅ Abrechnung wurde erfolgreich aktualisiert.")
#             else:
#                 # Yeni Abrechnung oluşturma
#                 Abrechnung.objects.create(
#                     mitarbeiter_id=mitarbeiter_id,
#                     projekt_id=projekt_id,
#                     monat=monat,
#                     stunden=stunden,
#                     stundensatz=stundensatz,
#                     netto_summe=netto_summe,
#                     brutto_summe=brutto_summe,
#                     rechnung_status=rechnung_status,
#                     zahlungseingang=zahlungseingang or None,
#                     leistungsnachweis=leistungsnachweis,
#                     bemerkung=bemerkung
#                 )
#                 messages.success(request, "✅ Abrechnung wurde erfolgreich erstellt.")
#         else:
#             messages.error(request, "⚠️ Bitte füllen Sie alle Pflichtfelder aus.")

#         return redirect("manager_abrechnung")

#     # Tabloda sadece kendi projeleri ve atanmış projelere ait Abrechnung'ları gösteriyoruz
#     return render(request, "manager_pages/manager_abrechnung.html", {
#         "abrechnungen": page_obj,
#         "projekte": projekte  # sadece manager'ın oluşturduğu ve atandığı projeleri listeleyerek seçtirme
#     })


# @login_required
# @user_passes_test(is_manager)
# def manager_abrechnung_delete(request, id):
#     user = request.user

#     # İlgili Abrechnung kaydını getir
#     abrechnung = get_object_or_404(Abrechnung, id=id)

#     # Sadece kendi oluşturduğu projeye ait bir Abrechnung silinebilir
#     if abrechnung.projekt.erstellt_von != user:
#         messages.error(request, "❌ Sie dürfen nur Abrechnungen Ihrer eigenen Projekte löschen.")
#         return redirect("manager_abrechnung")

#     # Silme işlemi
#     abrechnung.delete()
#     messages.success(request, "🗑️ Abrechnung wurde erfolgreich gelöscht.")
#     return redirect("manager_abrechnung")

# @login_required
# @user_passes_test(is_manager)
# def manager_abrechnung_export(request):
#     user = request.user

#     # Manager'ın oluşturduğu veya atandığı projelerin ID'leri
#     projekte_ids = Projekt.objects.filter(Q(erstellt_von=user) | Q(manager=user)).values_list("id", flat=True)
#     abrechnungen = Abrechnung.objects.filter(projekt__in=projekte_ids)

#     # CSV export
#     response = HttpResponse(content_type='text/csv; charset=utf-8')
#     response['Content-Disposition'] = 'attachment; filename="abrechnungen.csv"'
#     response.write('\ufeff')  # BOM for Excel

#     writer = csv.writer(response)
#     writer.writerow([
#         'Projektname', 'Mitarbeiter', 'Monat', 'Stunden',
#         'Netto Summe', 'Brutto Summe', 'Rechnungsstatus',
#         'Zahlungseingang', 'Leistungsnachweis', 'Bemerkung'
#     ])

#     for abrechnung in abrechnungen:
#         writer.writerow([
#             abrechnung.projekt.projektname,
#             f"{abrechnung.mitarbeiter.vorname} {abrechnung.mitarbeiter.nachname}",
#             abrechnung.monat,
#             abrechnung.stunden,
#             abrechnung.netto_summe,
#             abrechnung.brutto_summe,
#             abrechnung.rechnung_status,
#             abrechnung.zahlungseingang,
#             abrechnung.leistungsnachweis,
#             abrechnung.bemerkung
#         ])

#     return response


# @login_required
# @user_passes_test(is_manager)
# def manager_reisebericht_view(request):
#     user = request.user

#     # Manager'ın oluşturduğu projeler ve atandığı projeler
#     eigene_projekte = Projekt.objects.filter(erstellt_von=user)
#     zugewiesene_projekte = Projekt.objects.filter(manager=user)
#     projekte = eigene_projekte | zugewiesene_projekte

#     # Tabloda gösterilecek Reisebericht'ler
#     projekte_ids = projekte.values_list("id", flat=True)
#     reiseberichte = Reisebericht.objects.filter(projekt__in=projekte_ids)

#     # 🔍 Filtreleme
#     zielort = request.GET.get('zielort')
#     startdatum = request.GET.get('startdatum')
#     enddatum = request.GET.get('enddatum')

#     if zielort:
#         reiseberichte = reiseberichte.filter(zielort__icontains=zielort)
#     if startdatum:
#         reiseberichte = reiseberichte.filter(datum__gte=startdatum)
#     if enddatum:
#         reiseberichte = reiseberichte.filter(datum__lte=enddatum)

#     # Sayfalama
#     paginator = Paginator(reiseberichte, 10)
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)

#     # POST işlemi (Ekleme ve Güncelleme)
#     if request.method == "POST":
#         mitarbeiter_id = request.POST.get("mitarbeiter")
#         projekt_id = request.POST.get("projekt")
#         datum = request.POST.get("datum")
#         zielort = request.POST.get("zielort")
#         verkehrsmittel = request.POST.get("verkehrsmittel")
#         distanz_km = request.POST.get("distanz_km")
#         kosten_fahrt = request.POST.get("kosten_fahrt")
#         hotel_name = request.POST.get("hotel_name")
#         kosten_übernachtung = request.POST.get("kosten_übernachtung")
#         rechnung_vorhanden = request.POST.get("rechnung_vorhanden")
#         gesamtkosten = 0
#         edit_id = request.POST.get("edit_id")

#         # 🛡️ Yetki kontrolü: sadece kendi projelerine kayıt yapılabilir
#         if not Projekt.objects.filter(id=projekt_id, erstellt_von=user).exists():
#             messages.error(request, "❌ Sie dürfen nur Reiseberichte zu Ihren eigenen Projekten hinzufügen oder bearbeiten.")
#             return redirect("manager_reisebericht")

#         try:
#             kosten_fahrt = float(kosten_fahrt)
#             kosten_übernachtung = float(kosten_übernachtung)
#             gesamtkosten = kosten_fahrt + kosten_übernachtung
#         except (ValueError, TypeError):
#             messages.error(request, "❌ Kosten müssen gültige Zahlen sein.")
#             return redirect("manager_reisebericht")

#         if mitarbeiter_id and projekt_id and datum and zielort and verkehrsmittel:
#             if edit_id:
#                 # ✏️ Güncelleme
#                 reisebericht = get_object_or_404(Reisebericht, id=edit_id, projekt__erstellt_von=user)
#                 reisebericht.mitarbeiter_id = mitarbeiter_id
#                 reisebericht.projekt_id = projekt_id
#                 reisebericht.datum = datum
#                 reisebericht.zielort = zielort
#                 reisebericht.verkehrsmittel = verkehrsmittel
#                 reisebericht.distanz_km = distanz_km or 0
#                 reisebericht.kosten_fahrt = kosten_fahrt
#                 reisebericht.hotel_name = hotel_name
#                 reisebericht.kosten_übernachtung = kosten_übernachtung
#                 reisebericht.gesamtkosten = gesamtkosten
#                 reisebericht.rechnung_vorhanden = rechnung_vorhanden
#                 reisebericht.save()
#                 messages.success(request, "✅ Reisebericht wurde erfolgreich aktualisiert.")
#             else:
#                 # ➕ Yeni Kayıt
#                 Reisebericht.objects.create(
#                     mitarbeiter_id=mitarbeiter_id,
#                     projekt_id=projekt_id,
#                     datum=datum,
#                     zielort=zielort,
#                     verkehrsmittel=verkehrsmittel,
#                     distanz_km=distanz_km or 0,
#                     kosten_fahrt=kosten_fahrt,
#                     hotel_name=hotel_name,
#                     kosten_übernachtung=kosten_übernachtung,
#                     gesamtkosten=gesamtkosten,
#                     rechnung_vorhanden=rechnung_vorhanden
#                 )
#                 messages.success(request, "✅ Reisebericht wurde erfolgreich erstellt.")
#         else:
#             messages.error(request, "⚠️ Bitte füllen Sie alle Pflichtfelder aus.")

#         return redirect("manager_reisebericht")

#     return render(request, 'manager_pages/manager_reisebericht.html', {
#         'reiseberichte': page_obj,
#         'projekte': projekte  # Manager sadece kendi projelerini görebilecek
#     })

# @login_required
# @user_passes_test(is_manager)
# def manager_reisebericht_delete(request, id):
#     user = request.user
#     reisebericht = get_object_or_404(Reisebericht, id=id)

#     if reisebericht.projekt.erstellt_von != user:
#         messages.error(request, "❌ Sie dürfen nur Reiseberichte Ihrer eigenen Projekte löschen.")
#         return redirect("manager_reisebericht")

#     reisebericht.delete()
#     messages.success(request, "🗑️ Reisebericht wurde erfolgreich gelöscht.")
#     return redirect("manager_reisebericht")


# @login_required
# @user_passes_test(is_manager)
# def manager_reisebericht_export(request):
#     user = request.user
    
#     # Manager'ın oluşturduğu projeler ve atanmış projeler
#     eigene_projekte = Projekt.objects.filter(erstellt_von=user)
#     zugewiesene_projekte = Projekt.objects.filter(manager=user)

#     # Tüm projelerin birleşimi
#     projekte = eigene_projekte | zugewiesene_projekte

#     # Reisebericht verilerini al
#     reiseberichte = Reisebericht.objects.filter(projekt__in=projekte)

#     # CSV formatında bir response oluştur
#     response = HttpResponse(content_type='text/csv')
#     response['Content-Disposition'] = 'attachment; filename="reiseberichte.csv"'

#     writer = csv.writer(response)
#     writer.writerow(['Mitarbeiter', 'Zielort', 'Datum', 'Verkehrsmittel', 'Distanz (km)', 'Kosten Fahrt', 'Hotel Name', 'Kosten Übernachtung', 'Gesamtkosten', 'Rechnung Vorhanden'])

#     for reisebericht in reiseberichte:
#         writer.writerow([reisebericht.mitarbeiter, 
#                          reisebericht.zielort, 
#                          reisebericht.datum.strftime("%d.%m.%Y"), 
#                          reisebericht.verkehrsmittel, 
#                          reisebericht.distanz_km, 
#                          reisebericht.kosten_fahrt, 
#                          reisebericht.hotel_name, 
#                          reisebericht.kosten_übernachtung, 
#                          reisebericht.gesamtkosten, 
#                          reisebericht.rechnung_vorhanden])

#     return response



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