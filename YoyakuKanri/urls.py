from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='YoyakuKanri'),
    path('Monshinhyou', views.MonshinhyouCreate, name='Monshinhyou'),
    path('Uketsuke', views.Uketsuke, name='Uketsuke'),
    path('UketsukeKanryou', views.UketsukeKanryou, name="UketsukeKanryou"),
    path('MonshinhyouClose', views.MonshinhyouClose, name='MonshinhyouClose'),
    path('KanzyaDataEdit/<int:pk>/', views.KanzyaDataEdit, name='KanzyaDataEdit'),
    path('ZikaiYoyaku/<int:ID>/<int:year>/<int:month>/', views.ZikaiYoayakuShow, name="ZikaiYoyaku"),
    path('ZikaiYoyakuKakunin/<int:ID>/<int:year>/<int:month>/<int:day>/<int:hour>/<int:minute>',
          views.ZikaiYoyakuKakunin, name='ZikaiYoyakuKakunin'),
    path('ZikaiyoyakuKanryou/<int:ID>/<int:year>/<int:month>/<int:day>/<int:hour>/<int:minute>', 
          views.ZikaiYoyakuKanryou, name="ZikaiyoyakuKanryou"),
    path('ShikaishiList', views.ShikaishiList, name='ShikaishiList'),
    path('ShikaishiEdit/<int:ID>/<int:add_or_edit>', views.ShikaishiEdit, name='ShikaishiEdit'),
    path('JushinrekiEdit/<int:ID>', views.JushinrekiEdit, name='JushinrekiEdit')
]