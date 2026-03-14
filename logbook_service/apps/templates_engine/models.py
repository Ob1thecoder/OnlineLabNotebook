from django.conf import settings
from django.db import models


class EntryTemplate(models.Model):
    """
    Built-in and custom templates that pre-structure entries.
    """

    DISCIPLINE_GENERAL = "general"
    DISCIPLINE_ELECTRICAL = "electrical"
    DISCIPLINE_MATERIALS = "materials"
    DISCIPLINE_FLUIDS = "fluids"
    DISCIPLINE_STRUCTURAL = "structural"
    DISCIPLINE_SOFTWARE = "software"
    DISCIPLINE_FIELD_OBS = "field_observation"

    DISCIPLINE_CHOICES = [
        (DISCIPLINE_GENERAL, "General"),
        (DISCIPLINE_ELECTRICAL, "Electrical / Circuits"),
        (DISCIPLINE_MATERIALS, "Materials"),
        (DISCIPLINE_FLUIDS, "Fluid Mechanics"),
        (DISCIPLINE_STRUCTURAL, "Structural"),
        (DISCIPLINE_SOFTWARE, "Software"),
        (DISCIPLINE_FIELD_OBS, "Field Observation"),
    ]

    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    discipline = models.CharField(
        max_length=50, choices=DISCIPLINE_CHOICES, default=DISCIPLINE_GENERAL
    )

    is_builtin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    # Null for built-in templates; set for instructor/admin-created templates.
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_templates",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "templates_entrytemplate"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class TemplateSection(models.Model):
    """
    Individual sections within a template (e.g. Objective, Hypothesis).
    """

    template = models.ForeignKey(
        EntryTemplate,
        on_delete=models.CASCADE,
        related_name="sections",
    )
    title = models.CharField(max_length=200)
    prompt = models.TextField(blank=True)
    is_required = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "templates_templatesection"
        ordering = ["template", "order"]
        unique_together = ("template", "order")

    def __str__(self) -> str:
        return self.title
