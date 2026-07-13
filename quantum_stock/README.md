# QUANTUM TECHNOLOGY — Application de gestion de stock

Application Django professionnelle de gestion de stock informatique : catalogue de matériels,
réservations et commandes avec circuit de validation hiérarchique, mouvements de stock,
notifications (interne + email), journal d'activité complet, tableau de bord et alertes intelligentes.

## 1. Ce qui est livré (fonctionnel et testé)

- **Comptes & rôles** : Super Administrateur, Administrateur, Responsable hiérarchique, Magasinier,
  Employé, Client interne, Client externe. Inscription avec vérification d'email obligatoire,
  connexion, réinitialisation de mot de passe.
- **Catalogue** : agences, magasins, fournisseurs, hiérarchie de catégories (catégorie → sous-catégorie
  → famille → sous-famille → type → classe), fiche matériel complète (référence auto-générée, QR code
  auto-généré, code-barres, quantités disponible/réservée/commandée/min/max/critique, photos, documents).
- **Stock** : entrées, sorties, transferts entre magasins, ajustements, historique complet et
  atomique (transactions verrouillées pour éviter les incohérences de quantités).
- **Panier & réservations / commandes** : ajout au panier (session), soumission, suivi, annulation,
  téléchargement du bon de commande en PDF.
- **Workflow de validation** : Employé/Client → Responsable → Magasinier → Administrateur → Validation
  finale, avec Accepter / Refuser / Demander une modification à chaque étape, historique horodaté.
- **Notifications** : notification interne + email automatique à chaque étape clé (nouvelle demande,
  validation, refus, stock faible, garantie expirée...).
- **Journal des activités (audit)** : toutes les créations/modifications/suppressions des matériels,
  réservations, commandes et mouvements de stock sont tracées automatiquement (utilisateur, IP,
  navigateur, ancienne/nouvelle valeur), ainsi que les connexions/déconnexions.
- **Tableau de bord** : KPIs, alertes de stock faible/rupture/garantie expirée, matériels les plus
  demandés, dernières activités.
- **Tâches périodiques Celery** : vérification quotidienne des stocks faibles et des garanties expirées.
- **Sécurité** : CSRF, protection XSS (échappement automatique des templates Django), ORM (donc pas
  d'injection SQL), permissions par rôle sur les vues sensibles, journalisation de sécurité.

Ce socle a été testé de bout en bout (migrations, création d'utilisateurs/matériels, cycle complet
réservation → 4 validations → mise à jour du stock → notifications, serveur de développement).

## 2. Ce qu'il reste à enrichir (le cahier des charges est très large)

Le cahier des charges couvre un périmètre de niveau "ERP" complet. Cette première livraison pose une
architecture propre et un cœur fonctionnel réel ; les points suivants sont prévus dans la structure
mais restent à compléter selon vos priorités :
- Rapports Excel/CSV export avancés (le PDF du bon de commande est déjà fonctionnel)
- Signature électronique, lecture de QR code depuis l'interface (scanner caméra)
- Mode sombre, tableau de bord personnalisable, multi-langue
- Interface d'inventaire physique (l'écran de saisie des comptages)
- API REST

Dites-moi lesquels traiter en priorité et je les implémente dans le même style.

## 3. Installation

```bash
# 1. Environnement virtuel
python3 -m venv venv
source venv/bin/activate   # Windows : venv\Scripts\activate

# 2. Dépendances
pip install -r requirements.txt

# 3. Variables d'environnement
cp .env.example .env
# Éditez .env :
#  - DATABASE_URL : récupérez la vraie chaîne de connexion PostgreSQL dans
#    Supabase > Project Settings > Database > Connection string (URI).
#    ATTENTION : ce n'est PAS la clé "sb_publishable_...", qui est une clé API,
#    pas un mot de passe de base de données.
#  - EMAIL_* : vos identifiants SMTP pour l'envoi réel des emails
#    (sans EMAIL_HOST renseigné, les emails s'affichent simplement dans la console).
#  - REDIS_URL : nécessaire pour Celery et le cache (Redis local ou managé).

# 4. Base de données
python manage.py migrate

# 5. Compte administrateur
python manage.py createsuperuser

# 6. Lancer le serveur
python manage.py runserver
```

Ouvrez ensuite http://127.0.0.1:8000/comptes/connexion/ pour l'application, et
http://127.0.0.1:8000/admin/ pour l'administration Django.

### Lancer Celery (tâches planifiées : alertes stock/garantie)

```bash
celery -A quantum_stock worker -l info
celery -A quantum_stock beat -l info
```

## 4. Structure du projet

```
quantum_stock/
├── quantum_stock/     # configuration Django (settings, urls, celery)
├── accounts/          # utilisateurs, rôles, authentification, vérification email
├── catalog/           # agences, magasins, fournisseurs, catégories, matériels
├── stock/             # entrées / sorties / transferts / ajustements / inventaires
├── reservations/       # panier + réservations
├── commandes/          # panier + commandes + bon PDF
├── workflow/           # moteur générique de circuit de validation
├── notifications/      # notifications internes + emails
├── audit/              # journal des activités (middleware + signaux automatiques)
├── dashboard/           # tableau de bord et KPIs
└── templates/           # gabarits HTML (Tailwind CSS, charte QUANTUM TECHNOLOGY)
```

## 5. Charte graphique appliquée

- Rouge principal : `#D61C4E`
- Bleu principal : `#293462`
- Blanc : `#FFFFFF`
- Interface responsive (Tailwind CSS), sidebar bleue, actions en rouge, mode clair.
