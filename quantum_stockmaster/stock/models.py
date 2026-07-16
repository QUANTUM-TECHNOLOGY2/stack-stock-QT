from django.db import models

class Equipement(models.Model):
    CATEGORIES = [
        ('Ordinateurs', 'Ordinateurs'),
        ('Serveurs', 'Serveurs'),
        ('Réseau', 'Réseau'),
        ('Switch', 'Switch'),
        ('Routeur', 'Routeur'),
        ('Firewall', 'Firewall'),
        ('Cybersécurité', 'Cybersécurité'),
        ('Logiciels', 'Logiciels'),
        ('Licences', 'Licences'),
        ('Mobilier', 'Mobilier'),
        ('Téléphonie', 'Téléphonie'),
        ('Caméras', 'Caméras'),
        ('Onduleurs', 'Onduleurs'),
        ('Stockage', 'Stockage'),
        ('Fibre Optique', 'Fibre Optique'),
        ('Câblage', 'Câblage'),
        ('Consommables', 'Consommables'),
        ('Outillage', 'Outillage'),
        ('Électricité', 'Électricité'),
        ('Audiovisuel', 'Audiovisuel'),
    ]

    nom = models.CharField(max_length=150)
    categorie = models.CharField(max_length=50, choices=CATEGORIES)
    marque = models.CharField(max_length=100, blank=True, null=True)
    modele = models.CharField(max_length=100, blank=True, null=True)
    numero_serie = models.CharField(max_length=100, blank=True, null=True, unique=True)
    reference = models.CharField(max_length=100, blank=True, null=True)
    fournisseur = models.CharField(max_length=150, blank=True, null=True)
    
    quantite_dispo = models.PositiveIntegerField(default=0)
    seuil_alerte = models.PositiveIntegerField(default=5)
    quantite_reservee = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.nom} - {self.marque or 'Générique'}"

class HistoriqueFlux(models.Model):
    TYPES = [
        ('Création', 'Création'),
        ('Modification', 'Modification'),
        ('Entrée', 'Entrée'),
        ('Sortie', 'Sortie'),
        ('Réservation', 'Réservation'),
        ('Libération', 'Libération'),
        ('Suppression', 'Suppression'),
    ]
    type_action = models.CharField(max_length=20, choices=TYPES)
    message = models.TextField()
    date_action = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.type_action}] - {self.date_action.strftime('%d/%m/%Y %H:%M')}"