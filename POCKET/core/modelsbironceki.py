from django.db import models

class Abordnung(models.Model):
    abordnung_id = models.AutoField(primary_key=True)
    mitarbeiter = models.ForeignKey('Mitarbeiter', on_delete=models.CASCADE, db_column='mitarbeiter_id')
    projekt = models.ForeignKey('Projekt', on_delete=models.CASCADE, db_column='projekt_id')
    zeitraum_start = models.DateField()
    zeitraum_ende = models.DateField()

    class Meta:
        managed = False
        db_table = 'Abordnung'

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
    monat = models.DateField()
    stunden = models.IntegerField()
    stundensatz = models.DecimalField(max_digits=10, decimal_places=2)
    netto_summe = models.DecimalField(max_digits=10, decimal_places=2)
    brutto_summe = models.DecimalField(max_digits=10, decimal_places=2)
    rechnung_status = models.CharField(max_length=20, choices=RECHNUNG_STATUS_CHOICES, default='-')
    zahlungseingang = models.DateField(null=True, blank=True)
    leistungsnachweis = models.CharField(max_length=100, blank=True, null=True)
    bemerkung = models.TextField(blank=True, null=True)
        def save(self, *args, **kwargs):
        if self.monat:
            self.monat = self.monat.replace(day=1)
        super().save(*args, **kwargs)


    class Meta:
        managed = False
        db_table = 'Abrechnung'

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

    vorname = models.CharField(max_length=50)
    nachname = models.CharField(max_length=50)
    wohnort = models.CharField(max_length=100)
    erste_taetigkeitsstaette = models.CharField(max_length=150)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='-')
    abteilung = models.CharField(max_length=100)
    rolle = models.CharField(max_length=20, choices=ROLLE_CHOICES, default='-')

    class Meta:
        managed = False
        db_table = 'Mitarbeiter'

class ProjektMitarbeiter(models.Model):
    projekt = models.ForeignKey('Projekt', on_delete=models.CASCADE, db_column='projekt_id')
    mitarbeiter = models.ForeignKey('Mitarbeiter', on_delete=models.CASCADE, db_column='mitarbeiter_id')

    class Meta:
        managed = False
        db_table = 'ProjektMitarbeiter'
        unique_together = (('projekt', 'mitarbeiter'),)


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
    beschreibung = models.TextField()
    class Meta:
        managed = False
        db_table = 'Projekt'

class Reisekosten(models.Model):
    RECHNUNG_VORHANDEN_CHOICES = [
        ('-', 'Bitte wählen'),
        ('Ja', 'Ja'),
        ('Nein', 'Nein'),
    ]

    mitarbeiter = models.ForeignKey('Mitarbeiter', on_delete=models.CASCADE)
    projekt = models.ForeignKey('Projekt', on_delete=models.CASCADE)
    datum = models.DateField()
    zielort = models.CharField(max_length=100)
    zweck = models.TextField()
    verkehrsmittel = models.CharField(max_length=50)
    distanz_km = models.DecimalField(max_digits=10, decimal_places=2)
    kosten_fahrt = models.DecimalField(max_digits=10, decimal_places=2)
    hotel_name = models.CharField(max_length=100, blank=True, null=True)
    kosten_übernachtung = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    gesamtkosten = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    rechnung_vorhanden = models.CharField(max_length=10, choices=RECHNUNG_VORHANDEN_CHOICES, default='-')

    class Meta:
        managed = False
        db_table = 'Reisekosten'

class Schulungskosten(models.Model):
    TEILGENOMMEN_CHOICES = [
        ('-', 'Bitte wählen'),
        ('Ja', 'Ja'),
        ('Nein', 'Nein'),
    ]

    mitarbeiter = models.ForeignKey('Mitarbeiter', on_delete=models.CASCADE)
    projekt = models.ForeignKey('Projekt', on_delete=models.CASCADE)
    schulungstyp = models.CharField(max_length=100)
    datum_start = models.DateField()
    datum_ende = models.DateField()
    dauer = models.IntegerField()
    kosten = models.DecimalField(max_digits=10, decimal_places=2)
    anbieter = models.CharField(max_length=150)
    teilgenommen = models.CharField(max_length=10, choices=TEILGENOMMEN_CHOICES, default='-')
    beschreibung = models.TextField(blank=True, null=True)
    class Meta:
        managed = False
        db_table = 'Schulungskosten'
