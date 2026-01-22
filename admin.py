from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Flower, Order


# ================= Flower Admin =================
@admin.register(Flower)
class FlowerAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'price', 'photo_preview')
    list_display_links = ('name',)
    search_fields = ('name',)
    list_filter = ('category',)
    ordering = ('id',)
    actions_selection_counter = True
    actions = ['delete_selected']

    def photo_preview(self, obj):
        if obj.image:
            edit_url = reverse('admin:shop_flower_change', args=[obj.id])
            delete_url = reverse('admin:shop_flower_delete', args=[obj.id])
            return format_html(
                '''
                <div style="text-align:center;">
                    <img src="{}" width="60" style="border-radius:5px;" />
                    <div>
                        <a href="{}">✏️ Edit</a> | 
                        <a href="{}" style="color:red;">🗑 Delete</a>
                    </div>
                </div>
                ''',
                obj.image.url, edit_url, delete_url
            )
        return "(No Image)"

    photo_preview.short_description = "Photo"


# ================= Order Admin =================
@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer_name',
        'flower',
        'flower_category',
        'flower_photo',
        'quantity',
        'order_type',
        'total_price',
        'action_buttons'
    )
    list_display_links = ('customer_name', 'flower')
    search_fields = ('customer_name', 'flower__name', 'order_type')
    list_filter = ('order_type', 'flower__category')
    ordering = ('-id',)

    # Flower को category देखाउने
    def flower_category(self, obj):
        return obj.flower.category
    flower_category.short_description = "Category"

    # Flower को photo देखाउने
    def flower_photo(self, obj):
        if obj.flower.image:
            return format_html(
                '<img src="{}" width="50" style="border-radius:5px;" />',
                obj.flower.image.url
            )
        return "(No Image)"
    flower_photo.short_description = "Photo"

    # Edit / Delete buttons
    def action_buttons(self, obj):
        edit_url = reverse('admin:shop_order_change', args=[obj.id])
        delete_url = reverse('admin:shop_order_delete', args=[obj.id])
        return format_html(
            '''
            <a href="{}" style="color:green; font-weight:bold;">✏️ Edit</a>
            &nbsp; | &nbsp;
            <a href="{}" style="color:red; font-weight:bold;">🗑 Delete</a>
            ''',
            edit_url, delete_url
        )
    action_buttons.short_description = "Actions"
