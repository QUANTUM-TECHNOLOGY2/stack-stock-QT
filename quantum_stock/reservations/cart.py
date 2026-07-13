from catalog.models import Materiel

CLE_SESSION = "panier_reservation"


class Panier:
    """Panier de réservation stocké dans la session (avant validation, aucun compte requis pour consulter,
    mais l'authentification est obligatoire pour ajouter un article ou valider - voir vues)."""

    def __init__(self, request):
        self.session = request.session
        self.contenu = self.session.setdefault(CLE_SESSION, {})

    def ajouter(self, materiel_id, quantite=1):
        cle = str(materiel_id)
        self.contenu[cle] = self.contenu.get(cle, 0) + quantite
        self._sauvegarder()

    def definir_quantite(self, materiel_id, quantite):
        cle = str(materiel_id)
        if quantite <= 0:
            self.contenu.pop(cle, None)
        else:
            self.contenu[cle] = quantite
        self._sauvegarder()

    def retirer(self, materiel_id):
        self.contenu.pop(str(materiel_id), None)
        self._sauvegarder()

    def vider(self):
        self.session[CLE_SESSION] = {}
        self._sauvegarder()

    def _sauvegarder(self):
        self.session[CLE_SESSION] = self.contenu
        self.session.modified = True

    def __len__(self):
        return sum(self.contenu.values())

    def lignes(self):
        materiels = Materiel.objects.filter(id__in=self.contenu.keys())
        for materiel in materiels:
            quantite = self.contenu[str(materiel.id)]
            yield {
                "materiel": materiel,
                "quantite": quantite,
                "sous_total": materiel.valeur * quantite if materiel.valeur else None,
            }
