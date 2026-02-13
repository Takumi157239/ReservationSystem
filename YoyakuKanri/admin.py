from django.contrib import admin
from .models import T_KANZYA, T_YOYAKU, T_JUSHINREKI
from .models import M_SHIKAISHI, M_CMB_ITEM
# Register your models here.

admin.site.register(T_KANZYA)
admin.site.register(T_YOYAKU)
admin.site.register(T_JUSHINREKI)
admin.site.register(M_SHIKAISHI)
admin.site.register(M_CMB_ITEM)
