from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin
from .models import BenutzerProfil, Abrechnung, Mitarbeiter, Projekt, Reisebericht, Schulungskosten, Abordnung

# 📌 BenutzerProfil için geçmişi admin panelinde göster
@admin.register(BenutzerProfil)
class BenutzerProfilAdmin(SimpleHistoryAdmin):
    list_display = ("benutzer", "profil_bild")  # ✅ Sadece profil bilgisi kaldı
    search_fields = ("benutzer__username",)


@admin.register(Mitarbeiter)
class MitarbeiterAdmin(admin.ModelAdmin):
    exclude = ("user", "password_plain")
    list_display = ('vorname', 'nachname', 'standort', 'erste_taetigkeitsstaette', 'abteilung', 'status', 'rolle')
    search_fields = ('vorname', 'nachname', 'standort', 'abteilung')
    list_filter = ('standort', 'rolle', 'abteilung', 'status')

@admin.register(Projekt)
class ProjektAdmin(admin.ModelAdmin):
    list_display = ('projektname', 'startdatum', 'enddatum', 'budget', 'kunde_1', 'kunde_2', 'projekttyp', 'status')
    search_fields = ('projektname', 'kunde_1', 'kunde_2')
    list_filter = ('status', 'projekttyp')

@admin.register(Abrechnung)
class AbrechnungAdmin(admin.ModelAdmin):
    list_display = ('mitarbeiter', 'projekt', 'monat', 'stunden', 'stundensatz', 'netto_summe', 'brutto_summe', 'rechnung_status', 'zahlungseingang')
    search_fields = ('mitarbeiter__vorname', 'mitarbeiter__nachname', 'projekt__projektname')
    list_filter = ('projekt', 'mitarbeiter', 'rechnung_status', 'monat')

@admin.register(Reisebericht)
class ReiseberichtAdmin(admin.ModelAdmin):
    list_display = ('mitarbeiter', 'projekt', 'datum', 'zielort', 'zweck', 'verkehrsmittel', 'distanz_km', 'kosten_fahrt', 'hotel_name', 'kosten_übernachtung', 'gesamtkosten', 'rechnung_vorhanden')
    search_fields = ('mitarbeiter__vorname', 'mitarbeiter__nachname', 'projekt__projektname', 'zielort')
    list_filter = ('verkehrsmittel', 'rechnung_vorhanden')

@admin.register(Schulungskosten)
class SchulungskostenAdmin(admin.ModelAdmin):
    list_display = ('mitarbeiter', 'projekt', 'schulungstyp', 'datum_start', 'datum_ende', 'dauer', 'kosten', 'anbieter', 'teilgenommen')
    search_fields = ('mitarbeiter__vorname', 'mitarbeiter__nachname', 'schulungstyp', 'anbieter')
    list_filter = ('teilgenommen',)

@admin.register(Abordnung)
class AbordnungAdmin(admin.ModelAdmin):
    list_display = ('mitarbeiter', 'projekt', 'zeitraum_start', 'zeitraum_ende')
    search_fields = ('mitarbeiter__vorname', 'mitarbeiter__nachname', 'projekt__projektname')
    list_filter = ('projekt',)
