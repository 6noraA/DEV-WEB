from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from .models import (
    Personne, Produit, Lieu,
    Information_locale, Signalement,
    DemandePromotion,
)


# ── Site admin custom ─────────────────────────────────────────────
class MaVilleAdminSite(AdminSite):
    site_header = "MaVille — Administration"
    site_title  = "MaVille Admin"
    index_title = "Tableau de bord"

    def has_permission(self, request):
        if not request.user.is_active:
            return False
        if request.user.is_superuser:
            return True
        try:
            return request.user.personne.type_membre == 'administrateur'
        except Exception:
            return False

admin_site = MaVilleAdminSite(name='maville_admin')


# ── Inline Personne dans User ─────────────────────────────────────
class PersonneInline(admin.StackedInline):
    model = Personne
    can_delete = False
    verbose_name_plural = 'Profil'
    fields = ['age', 'sexe', 'date_naissance', 'type_membre', 'niveau',
              'points', 'nb_connexions', 'nb_actions', 'photo']
    extra = 0


# ── User ──────────────────────────────────────────────────────────
class UserAdmin(BaseUserAdmin):
    inlines = [PersonneInline]
    list_display  = ['username', 'email', 'get_niveau', 'get_type_membre', 'is_active', 'is_superuser']
    list_filter   = ['is_active', 'is_superuser', 'personne__niveau', 'personne__type_membre']
    search_fields = ['username', 'email']
    actions       = ['bannir_utilisateurs', 'reactiver_utilisateurs', 'passer_expert', 'passer_admin']

    @admin.display(description='Niveau')
    def get_niveau(self, obj):
        couleurs = {
            'debutant':      '#94a3b8',
            'intermediaire': '#3b82f6',
            'avance':        '#8b5cf6',
            'expert':        '#f59e0b',
        }
        try:
            n = obj.personne.niveau
            c = couleurs.get(n, '#64748b')
            return format_html('<span style="color:{};font-weight:700;">{}</span>', c, n.capitalize())
        except Exception:
            return '—'

    @admin.display(description='Type')
    def get_type_membre(self, obj):
        try:
            t = obj.personne.type_membre
            if t == 'administrateur':
                return format_html('<span style="color:#ef4444;font-weight:700;">Administrateur</span>')
            return t.capitalize()
        except Exception:
            return '—'

    @admin.action(description='Bannir les utilisateurs sélectionnés')
    def bannir_utilisateurs(self, request, queryset):
        proteges = queryset.filter(is_superuser=True) | queryset.filter(personne__type_membre='administrateur')
        if proteges.exclude(pk=request.user.pk).exists():
            self.message_user(request, "Impossible de bannir un administrateur.", level='error')
            return
        count = queryset.exclude(pk=request.user.pk).update(is_active=False)
        self.message_user(request, f"{count} utilisateur(s) bannis.")

    @admin.action(description='Réactiver les utilisateurs sélectionnés')
    def reactiver_utilisateurs(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count} utilisateur(s) réactivés.")

    @admin.action(description='Passer au niveau Expert')
    def passer_expert(self, request, queryset):
        count = 0
        for user in queryset:
            try:
                p = user.personne
                p.niveau = 'expert'
                p.points = max(p.points, 7)
                p.save()
                count += 1
            except Exception:
                pass
        self.message_user(request, f"{count} utilisateur(s) passés Expert.")

    @admin.action(description='Promouvoir Administrateur')
    def passer_admin(self, request, queryset):
        count = 0
        for user in queryset:
            try:
                p = user.personne
                p.type_membre = 'administrateur'
                p.niveau = 'expert'
                p.points = max(p.points, 7)
                p.save()
                count += 1
            except Exception:
                pass
        self.message_user(request, f"{count} utilisateur(s) promus Administrateur.")


# ── PersonneAdmin ─────────────────────────────────────────────────
class PersonneAdmin(admin.ModelAdmin):
    list_display  = ['user', 'niveau', 'type_membre', 'points', 'nb_connexions', 'nb_actions']
    list_filter   = ['niveau', 'type_membre', 'sexe']
    search_fields = ['user__username', 'user__email']
    list_editable = ['niveau', 'type_membre']
    ordering      = ['-points']


# ── ProduitAdmin ──────────────────────────────────────────────────
class ProduitAdmin(admin.ModelAdmin):
    list_display  = ['ID', 'Nom', 'marque', 'etat', 'mode', 'Bactterie', 'Adresse_IP']
    list_filter   = ['etat', 'mode', 'marque']
    search_fields = ['ID', 'Nom', 'marque', 'Adresse_IP']
    list_editable = ['etat', 'mode']


# ── LieuAdmin ─────────────────────────────────────────────────────
class LieuAdmin(admin.ModelAdmin):
    list_display      = ['Nom', 'Adresse', 'latitude', 'longitude']
    search_fields     = ['Nom', 'Adresse']
    filter_horizontal = ['liste_produits']


# ── SignalementAdmin ──────────────────────────────────────────────
class SignalementAdmin(admin.ModelAdmin):
    list_display  = ['nom', 'type_signalement', 'auteur', 'lieu', 'produit', 'date']
    list_filter   = ['type_signalement', 'date']
    search_fields = ['nom', 'auteur', 'description']
    ordering      = ['-date']


# ── InformationLocaleAdmin ────────────────────────────────────────
class InformationLocaleAdmin(admin.ModelAdmin):
    list_display  = ['nom', 'auteur', 'date']
    search_fields = ['nom', 'auteur']
    ordering      = ['-date']


# ── DemandePromotionAdmin ─────────────────────────────────────────
class DemandePromotionAdmin(admin.ModelAdmin):
    list_display    = ['demandeur', 'statut', 'date', 'traitee_par']
    list_filter     = ['statut']
    search_fields   = ['demandeur__user__username']
    ordering        = ['-date']
    readonly_fields = ['demandeur', 'message', 'date']
    actions         = ['accepter_demandes', 'refuser_demandes']

    @admin.action(description='Accepter les demandes sélectionnées')
    def accepter_demandes(self, request, queryset):
        count = 0
        for demande in queryset.filter(statut='en_attente'):
            demande.demandeur.type_membre = 'administrateur'
            demande.demandeur.save()
            demande.statut = 'acceptee'
            try:
                demande.traitee_par = request.user.personne
            except Exception:
                pass
            demande.save()
            count += 1
        self.message_user(request, f"{count} demande(s) acceptée(s).")

    @admin.action(description='Refuser les demandes sélectionnées')
    def refuser_demandes(self, request, queryset):
        count = queryset.filter(statut='en_attente').count()
        queryset.filter(statut='en_attente').update(statut='refusee')
        self.message_user(request, f"{count} demande(s) refusée(s).")


# ── Enregistrement dans les deux sites ───────────────────────────
# Site Django original (superuser)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(Personne, PersonneAdmin)
admin.site.register(Produit, ProduitAdmin)
admin.site.register(Lieu, LieuAdmin)
admin.site.register(Signalement, SignalementAdmin)
admin.site.register(Information_locale, InformationLocaleAdmin)
admin.site.register(DemandePromotion, DemandePromotionAdmin)

# Site custom MaVille (administrateurs)
admin_site.register(User, UserAdmin)
admin_site.register(Personne, PersonneAdmin)
admin_site.register(Produit, ProduitAdmin)
admin_site.register(Lieu, LieuAdmin)
admin_site.register(Signalement, SignalementAdmin)
admin_site.register(Information_locale, InformationLocaleAdmin)
admin_site.register(DemandePromotion, DemandePromotionAdmin)