from django.db import models


class MediaAsset(models.Model):
    name = models.CharField(max_length=150)
    url = models.URLField()
    tag = models.SlugField(max_length=50, db_index=True)
    order = models.PositiveSmallIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Recurso multimedia'
        verbose_name_plural = 'Recursos multimedia'
        ordering = ['tag', 'order']

    def __str__(self):
        return f'[{self.tag}] {self.name}'
