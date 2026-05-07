from django.contrib import admin
from django import forms
from django_json_widget.widgets import JSONEditorWidget

from apps.products.models import Product


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product

        fields = (
            "id",
            "title",
            "is_active",
            "type",
            "price",
            "data",
        )
        widgets = {"data": JSONEditorWidget}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = (
        "id",
        "title",
        "is_active",
        "price",
    )
    fields = (
        "id",
        "title",
        "is_active",
        "priority",
        "type",
        "price",
        "data",
        "created_at",
        "updated_at",
    )
    list_display_links = (
        "id",
        "title",
    )
    readonly_fields = (
        "id",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "is_active",
    )
    search_fields = (
        "title",
    )
