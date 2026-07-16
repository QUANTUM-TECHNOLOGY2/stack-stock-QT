import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Equipement, HistoriqueFlux

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if User.objects.filter(username=email).exists():
            messages.error(request, "Cette adresse email est déjà enregistrée.")
        else:
            # Création de l'utilisateur Django standard
            user = User.objects.create_user(
                username=email, email=email, password=password,
                first_name=prenom, last_name=nom
            )
            messages.success(request, "Inscription réussie ! Veuillez vous connecter.")
            return redirect('login')
    return render(request, 'stock/register.html')

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Adresse email ou mot de passe incorrect.")
    return render(request, 'stock/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def dashboard_view(request):
    equipements = Equipement.objects.all()
    categories_list = [c[0] for c in Equipement.CATEGORIES]
    logs = HistoriqueFlux.objects.all().order_by('-date_action')[:50]
    
    search_cat = request.GET.get('category', '')
    search_query = request.GET.get('search', '')
    
    if search_cat and search_cat != 'All':
        equipements = equipements.filter(categorie=search_cat)
    if search_query:
        equipements = equipements.filter(nom__icontains=search_query)

    # Calcul des indicateurs clés (KPI)
    kpi_total = equipements.count()
    # Utilisation de F() pour comparer les champs de manière sûre au niveau base de données
    from django.db.models import F
    kpi_alert = equipements.filter(quantite_dispo__lte=F('seuil_alerte'), quantite_dispo__gt=0).count()
    kpi_empty = equipements.filter(quantite_dispo=0).count()
    kpi_reserved = sum(item.quantite_reservee for item in equipements)

    # Préparation des données du graphique en anneau
    chart_data = {cat: 0 for cat in categories_list}
    for item in Equipement.objects.all():
        if item.categorie in chart_data:
            chart_data[item.categorie] += item.quantite_dispo

    context = {
        'equipements': equipements,
        'categories': categories_list,
        'selected_cat': search_cat,
        'search_query': search_query,
        'logs': logs,
        'kpi_total': kpi_total,
        'kpi_alert': kpi_alert,
        'kpi_empty': kpi_empty,
        'kpi_reserved': kpi_reserved,
        'chart_labels': list(chart_data.keys()),
        'chart_values': list(chart_data.values()),
    }
    return render(request, 'stock/dashboard.html', context)

@login_required
def add_or_edit_item(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        nom = request.POST.get('nom')
        categorie = request.POST.get('categorie')
        marque = request.POST.get('marque')
        modele = request.POST.get('modele')
        numero_serie = request.POST.get('numero_serie')
        reference = request.POST.get('reference')
        fournisseur = request.POST.get('fournisseur')
        quantite = int(request.POST.get('quantite', 0))
        seuil = int(request.POST.get('seuil', 5))

        if item_id:
            # Mode mise à jour
            item = get_object_or_404(Equipement, id=item_id)
            item.nom, item.categorie, item.marque, item.modele = nom, categorie, marque, modele
            item.numero_serie, item.reference, item.fournisseur = numero_serie, reference, fournisseur
            item.quantite_dispo, item.seuil_alerte = quantite, seuil
            item.save()
            HistoriqueFlux.objects.create(type_action='Modification', message=f"Équipement modifié : {nom}")
            messages.success(request, f"Équipement {nom} mis à jour.")
        else:
            # Mode création
            Equipement.objects.create(
                nom=nom, categorie=categorie, marque=marque, modele=modele,
                numero_serie=numero_serie, reference=reference, fournisseur=fournisseur,
                quantite_dispo=quantite, seuil_alerte=seuil
            )
            HistoriqueFlux.objects.create(type_action='Création', message=f"Équipement ajouté : {nom} ({quantite} unités)")
            messages.success(request, f"L'équipement {nom} a été créé.")
            
    return redirect('dashboard')

@login_required
def delete_item(request, pk):
    item = get_object_or_404(Equipement, pk=pk)
    name = item.nom
    item.delete()
    HistoriqueFlux.objects.create(type_action='Suppression', message=f"Équipement supprimé : {name}")
    messages.success(request, f"L'équipement {name} a été retiré de l'inventaire.")
    return redirect('dashboard')

@login_required
def update_stock(request, pk, action):
    item = get_object_or_404(Equipement, pk=pk)
    # Récupération de la quantité souhaitée depuis le paramètre d'URL fourni par l'interface
    try:
        qty = int(request.GET.get('qty', 1))
    except ValueError:
        qty = 1

    if qty <= 0:
        messages.error(request, "La quantité spécifiée doit être supérieure à zéro.")
        return redirect('dashboard')

    now_str = timezone.now().strftime('%d/%m/%Y à %H:%M')

    if action == 'in':
        item.quantite_dispo += qty
        item.save()
        HistoriqueFlux.objects.create(type_action='Entrée', message=f"Entrée en stock : +{qty} unités de {item.nom}")
        messages.success(request, f"Stock de {item.nom} augmenté de +{qty} unités.")
        
    elif action == 'out':
        if item.quantite_dispo >= qty:
            item.quantite_dispo -= qty
            item.save()
            HistoriqueFlux.objects.create(type_action='Sortie', message=f"Sortie de stock : -{qty} unités de {item.nom}")
            messages.success(request, f"Stock de {item.nom} diminué de -{qty} unités.")
        else:
            messages.error(request, "Le stock disponible est insuffisant pour valider cette sortie.")
            
    elif action == 'reserve':
        if item.quantite_dispo >= qty:
            item.quantite_dispo -= qty
            item.quantite_reservee += qty
            item.save()
            
            # Enregistrement du flux de transaction
            HistoriqueFlux.objects.create(
                type_action='Réservation', 
                message=f"Réservation de {qty}x {item.nom} par {request.user.first_name} {request.user.last_name}"
            )
            
            # 📨 Alerte e-mail pour le propriétaire de l'entreprise
            sujet_email = "⚠️ Réservation de matériel - Quantum Technology"
            corps_email = (
                f"Bonjour,\n\n"
                f"Une réservation d'équipement informatique vient d'être effectuée par un membre du personnel.\n\n"
                f"👤 Collaborateur : {request.user.first_name} {request.user.last_name} ({request.user.email})\n"
                f"📦 Équipement : {item.nom} ({item.marque or 'N/A'} - {item.modele or 'N/A'})\n"
                f"🔢 Quantité : {qty} unité(s)\n"
                f"⏰ Date et heure : {now_str}\n\n"
                f"Le système de gestion StockMaster"
            )
            try:
                send_mail(
                    sujet_email,
                    corps_email,
                    settings.DEFAULT_FROM_EMAIL,
                    [settings.COMPANY_OWNER_EMAIL],
                    fail_silently=False
                )
                messages.success(request, f"Réservation de {qty} unités enregistrée ! Un e-mail d'alerte a été envoyé.")
            except Exception:
                # Permet de continuer à faire tourner l'appli sur Kali même si aucun SMTP n'est actif
                messages.warning(request, f"Réservation de {qty} unités enregistrée localement (alerte e-mail visible dans la console du terminal).")
        else:
            messages.error(request, f"Le stock disponible de {item.nom} est insuffisant pour en réserver {qty} unités.")
            
    elif action == 'unreserve':
        if item.quantite_reservee >= qty:
            item.quantite_reservee -= qty
            item.quantite_dispo += qty
            item.save()
            HistoriqueFlux.objects.create(type_action='Libération', message=f"Retour au stock disponible : {qty}x {item.nom}")
            messages.success(request, f"Réservation annulée : {qty} unités de {item.nom} libérées.")
        else:
            messages.error(request, "La quantité réservée disponible est insuffisante.")
            
    return redirect('dashboard')

@login_required
def clear_history(request):
    HistoriqueFlux.objects.all().delete()
    messages.success(request, "L'historique des flux a été entièrement réinitialisé.")
    return redirect('dashboard')

@login_required
def export_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="quantum_inventory.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Nom', 'Categorie', 'Marque', 'Modele', 'Numero Serie', 'Reference', 'Fournisseur', 'Quantite Dispo', 'Seuil Alerte', 'Reserve'])
    for item in Equipement.objects.all():
        writer.writerow([
            item.id, item.nom, item.categorie, item.marque, item.modele,
            item.numero_serie, item.reference, item.fournisseur,
            item.quantite_dispo, item.seuil_alerte, item.quantite_reservee
        ])
    return response

@login_required
def import_csv(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = request.FILES['csv_file']
        decoded_file = csv_file.read().decode('utf-8').splitlines()
        reader = csv.reader(decoded_file)
        next(reader)  # Saut de l'en-tête
        count = 0
        for row in reader:
            if len(row) >= 10:
                _, created = Equipement.objects.update_or_create(
                    numero_serie=row[5],
                    defaults={
                        'nom': row[1],
                        'categorie': row[2],
                        'marque': row[3],
                        'modele': row[4],
                        'reference': row[6],
                        'fournisseur': row[7],
                        'quantite_dispo': int(row[8]),
                        'seuil_alerte': int(row[9]),
                        'quantite_reservee': int(row[10]) if len(row) > 10 else 0
                    }
                )
                count += 1
        HistoriqueFlux.objects.create(type_action='Modification', message=f"Synchronisation de base : {count} équipements importés par CSV.")
        messages.success(request, f"{count} équipements synchronisés avec succès.")
    return redirect('dashboard')