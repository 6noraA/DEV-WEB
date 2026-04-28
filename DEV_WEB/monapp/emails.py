import secrets
from django.core.mail import send_mail
from django.conf import settings

FROM = getattr(settings, 'DEFAULT_FROM_EMAIL', 'MaVille <admin@ville.com>')


def _envoyer(sujet, corps, destinataire):
    if not destinataire:
        return
    try:
        send_mail(
            subject=sujet,
            message=corps,
            from_email=FROM,
            recipient_list=[destinataire],
            fail_silently=False,
        )
    except Exception:
        pass


def generer_token():
    return secrets.token_urlsafe(32)


def email_confirmation_inscription(user, token, request):
    lien = request.build_absolute_uri('/confirmer-email/' + token + '/')
    corps = (
        "Bonjour " + user.username + ",\n\n"
        "Merci de vous etre inscrit sur Barbz !\n\n"
        "Pour activer votre compte, cliquez sur le lien ci-dessous :\n\n"
        + lien + "\n\n"
        "Ce lien est valable 24h.\n"
        "Si vous n'avez pas cree de compte, ignorez ce message.\n\n"
        "-- La municipalité de Barbz"
    )
    _envoyer("Confirmez votre adresse email - Barbz", corps, user.email)


def email_bienvenue(user):
    corps = (
        "Bonjour " + user.username + ",\n\n"
        "Votre adresse email a ete confirmee. Votre compte est maintenant actif.\n\n"
        "Vous pouvez des maintenant utiliser Barbz.\n\n"
        "-- La municipalité de Barbz"
    )
    _envoyer("Votre compte Barbz est active !", corps, user.email)


def email_bannissement(user, raison="Violation des regles de la plateforme."):
    corps = (
        "Bonjour " + user.username + ",\n\n"
        "Votre compte a ete suspendu suite a une decision de moderation.\n\n"
        "Raison : " + raison + "\n\n"
        "Si vous pensez qu'il s'agit d'une erreur, contactez la municipalité de Barbz.\n\n"
        "-- La municipalité de Barbz"
    )
    _envoyer("Votre compte Barbz a ete suspendu", corps, user.email)


def email_reactivation(user):
    corps = (
        "Bonjour " + user.username + ",\n\n"
        "Bonne nouvelle - votre compte a ete reactive.\n"
        "Vous pouvez a nouveau vous connecter sur Barbz.\n\n"
        "-- La municipalité de Barbz"
    )
    _envoyer("Votre compte Barbz a ete reactive", corps, user.email)


def email_demande_promotion_envoyee(user):
    corps = (
        "Bonjour " + user.username + ",\n\n"
        "Votre demande pour devenir Administrateur sur Barbz a bien ete recue.\n"
        "Un administrateur va l'examiner prochainement.\n\n"
        "Vous serez notifie par email des qu'une decision sera prise.\n\n"
        "-- La municipalité de Barbz"
    )
    _envoyer("Votre demande de promotion a ete envoyee", corps, user.email)


def email_promotion_admin_acceptee(user):
    corps = (
        "Bonjour " + user.username + ",\n\n"
        "Votre demande de promotion a ete acceptee.\n"
        "Vous etes maintenant Administrateur sur Barbz.\n\n"
        "Vous avez acces au tableau de bord d'administration,\n"
        "a la gestion des utilisateurs et aux demandes de promotion.\n\n"
        "Utilisez ces droits avec responsabilite !\n\n"
        "-- La municipalité de Barbz"
    )
    _envoyer("Vous etes maintenant Administrateur sur Barbz !", corps, user.email)


def email_promotion_admin_refusee(user):
    corps = (
        "Bonjour " + user.username + ",\n\n"
        "Votre demande pour devenir Administrateur sur Barbz a ete examinee\n"
        "et n'a pas ete retenue pour le moment.\n\n"
        "Continuez a contribuer a la plateforme.\n\n"
        "-- La municipalité de Barbz"
    )
    _envoyer("Votre demande de promotion a ete refusee", corps, user.email)


def email_suppression(username, email_destinataire, raison="Décision administrative."):
    corps = (
        "Bonjour " + username + ",\n\n"
        "Votre compte a ete definitivement supprime.\n\n"
        "Raison : " + raison + "\n\n"
        "Si vous pensez qu'il s'agit d'une erreur, contactez la municipalite de Barbz.\n\n"
        "-- La municipalite de Barbz"
    )
    _envoyer("Votre compte Barbz a ete supprime", corps, email_destinataire)


def email_signalement_pris_en_charge(user, signalement):
    corps = (
        "Bonjour " + user.username + ",\n\n"
        "Votre signalement \"" + signalement.nom + "\" a ete pris en charge\n"
        "par les services de la ville.\n\n"
        "Merci pour votre contribution !\n\n"
        "-- La municipalité de Barbz"
    )
    _envoyer("Votre signalement a ete pris en charge", corps, user.email)