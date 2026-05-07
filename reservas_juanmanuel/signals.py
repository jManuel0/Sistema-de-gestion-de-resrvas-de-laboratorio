from django.apps import apps
from django.db.models.signals import post_migrate
from django.dispatch import receiver


@receiver(post_migrate)
def crear_roles_basicos(**kwargs):
    Group = apps.get_model('auth', 'Group')
    if Group is None:
        return

    for nombre in ['Docente', 'Administrador', 'Estudiante']:
        Group.objects.get_or_create(name=nombre)

