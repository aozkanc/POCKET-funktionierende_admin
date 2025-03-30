from datetime import datetime
from django.contrib.auth.models import User, Group
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from simple_history.models import HistoricalRecords


@receiver(post_save, sender=User)
def benutzerprofil_erstellen(sender, instance, created, **kwargs):
    if created:  # Yeni bir kullanıcı oluşturulduğunda çalışır
        from core.models import BenutzerProfil  # ✅ Modeli burada import et
        BenutzerProfil.objects.create(benutzer=instance)


# Create your models here.

class Mitarbeiter(models.Model):
    STATUS_CHOICES = [
        ('-', 'Bitte wählen'),
        ('intern', 'Intern'),
        ('freelancer', 'Freelancer'),
    ]

    ROLLE_CHOICES = [
        ('-', 'Bitte wählen'),
        ('Manager', 'Manager'),
        ('Mitarbeiter', 'Mitarbeiter'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # Opsiyonel User bağlantısı
    vorname = models.CharField(max_length=50)
    nachname = models.CharField(max_length=50)
    standort = models.CharField(max_length=100)
    erste_taetigkeitsstaette = models.CharField(max_length=150)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='-', blank=True)
    abteilung = models.CharField(max_length=100)
    rolle = models.CharField(max_length=20, choices=ROLLE_CHOICES, default='-', blank=True)

    class Meta:
        verbose_name_plural = "Mitarbeiter"
        ordering = ["nachname", "vorname"]  # Listeleme sırası için

    def __str__(self):
        return f"{self.vorname} {self.nachname} ({self.rolle})"


class Projekt(models.Model):
    STATUS_CHOICES = [
        ('-', 'Bitte wählen'),
        ('geplant', 'Geplant'),
        ('laufend', 'Laufend'),
        ('abgeschlossen', 'Abgeschlossen'),
    ]

    projektname = models.CharField(max_length=100)
    startdatum = models.DateField()
    enddatum = models.DateField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    kunde_1 = models.CharField(max_length=100)
    kunde_2 = models.CharField(max_length=100, blank=True, null=True)
    projekttyp = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='-')
    erstellt_von = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='erstellt_projekte')
    beschreibung = models.TextField()
    class Meta:
        verbose_name_plural = "Projekte"

    def __str__(self):
        return self.projektname


class Abrechnung(models.Model):
    RECHNUNG_STATUS_CHOICES = [
        ('-', 'Bitte wählen'),
        ('nicht erstellt', 'Nicht erstellt'),
        ('erstellt', 'Erstellt'),
        ('gesendet', 'Gesendet'),
        ('erhalten', 'Erhalten'),
        ('storniert', 'Storniert'),
    ]

    mitarbeiter = models.ForeignKey('Mitarbeiter', on_delete=models.CASCADE)
    projekt = models.ForeignKey('Projekt', on_delete=models.CASCADE)
    monat = models.CharField(max_length=7, help_text="Format: YYYY-MM (z.B. 2025-03)")
    stunden = models.IntegerField()
    stundensatz = models.DecimalField(max_digits=10, decimal_places=2)
    netto_summe = models.DecimalField(max_digits=10, decimal_places=2)
    brutto_summe = models.DecimalField(max_digits=10, decimal_places=2)
    rechnung_status = models.CharField(max_length=20, choices=RECHNUNG_STATUS_CHOICES, default='-')
    zahlungseingang = models.DateField(null=True, blank=True)
    leistungsnachweis = models.CharField(max_length=100, blank=True, null=True)
    bemerkung = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name_plural = "Abrechnungen"

    def __str__(self):
        return f"{self.mitarbeiter} - {self.projekt} ({self.monat})"


class Reisebericht(models.Model):
    RECHNUNG_VORHANDEN_CHOICES = [
        ('-', 'Bitte wählen'),
        ('Ja', 'Ja'),
        ('Nein', 'Nein'),
    ]

    mitarbeiter = models.ForeignKey('Mitarbeiter', on_delete=models.CASCADE)
    projekt = models.ForeignKey('Projekt', on_delete=models.CASCADE, null=True, blank=True)
    datum = models.DateField()
    zielort = models.CharField(max_length=100)
    zweck = models.TextField()
    verkehrsmittel = models.CharField(max_length=50)
    distanz_km = models.DecimalField(max_digits=10, decimal_places=2)
    kosten_fahrt = models.DecimalField(max_digits=10, decimal_places=2)
    hotel_name = models.CharField(max_length=100, blank=True, null=True)
    kosten_übernachtung = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    gesamtkosten = models.DecimalField(max_digits=10, decimal_places=2)
    rechnung_vorhanden = models.CharField(max_length=10, choices=RECHNUNG_VORHANDEN_CHOICES, default='-')
    class Meta:
        verbose_name_plural = "Reiseberichte"

    def __str__(self):
        return f"{self.mitarbeiter} - {self.zielort} - ({self.datum})"


class Schulungskosten(models.Model):
    TEILGENOMMEN_CHOICES = [
        ('-', 'Bitte wählen'),
        ('Ja', 'Ja'),
        ('Nein', 'Nein'),
    ]

    mitarbeiter = models.ForeignKey('Mitarbeiter', on_delete=models.CASCADE)
    projekt = models.ForeignKey('Projekt', on_delete=models.CASCADE, null=True, blank=True)
    schulungstyp = models.CharField(max_length=100)
    datum_start = models.DateField()
    datum_ende = models.DateField()
    dauer = models.IntegerField()
    kosten = models.DecimalField(max_digits=10, decimal_places=2)
    anbieter = models.CharField(max_length=150)
    teilgenommen = models.CharField(max_length=10, choices=TEILGENOMMEN_CHOICES, default='-')
    beschreibung = models.TextField(blank=True, null=True)
    class Meta:
        verbose_name_plural = "Schulungskosten"

    def __str__(self):
        return f"{self.mitarbeiter} - {self.schulungstyp} ({self.datum_start})"


class Abordnung(models.Model):
    mitarbeiter = models.ForeignKey('Mitarbeiter', on_delete=models.CASCADE)
    projekt = models.ForeignKey('Projekt', on_delete=models.CASCADE)
    zeitraum_start = models.DateField()
    zeitraum_ende = models.DateField()
    class Meta:
        verbose_name_plural = "Abordnungen"

    def __str__(self):
        return f"{self.mitarbeiter} → {self.projekt} ({self.zeitraum_start} - {self.zeitraum_ende})"


class ProjektMitarbeiter(models.Model):
    projekt = models.ForeignKey('Projekt', on_delete=models.CASCADE)
    mitarbeiter = models.ForeignKey('Mitarbeiter', on_delete=models.CASCADE)
    class Meta:
        verbose_name_plural = "ProjektMitarbeiter"

    def __str__(self):
        return f"{self.mitarbeiter} → {self.projekt}"


class BenutzerProfil(models.Model):
    benutzer = models.OneToOneField(User, on_delete=models.CASCADE)
    profil_bild = models.ImageField(upload_to='profil_bilder/', blank=True, null=True)

    history = HistoricalRecords()

    def __str__(self):
        return self.benutzer.username