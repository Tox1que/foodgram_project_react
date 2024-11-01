from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from recipes.models import Recipe


@receiver(post_delete, sender=Recipe)
@receiver(post_save, sender=Recipe)
def recipes_count_changed(sender, instance, **kwargs):
    author = instance.author
    author.recipes_count = author.recipes.count()
    author.save()
