from catalog.models import Materiel

CLE_SESSION = "panier_commande"


class PanierCommande:
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
            prix = materiel.prix_achat or 0
            yield {
                "materiel": materiel,
                "quantite": quantite,
                "prix_unitaire": prix,
                "sous_total": prix * quantite,
            }
