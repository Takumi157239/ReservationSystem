from django import forms
from .models import T_KANZYA, M_SHIKAISHI, RAIIN_RIYUU_CHOICES, ZYOUHOU_MOTO_CHOICES
from datetime import time
from django.conf import settings


# 患者データフォーム
class KanzyaDataForm(forms.ModelForm):

    # 次回予約日の入力チェック
    def clean_ZIKAI_YOYAKUBI(self):
        dt = self.cleaned_data['ZIKAI_YOYAKUBI']

        if dt is not None:
            # 土日チェック（0=月曜, 6=日曜）
            if dt.weekday() >= 5:
                raise forms.ValidationError("土日は予約できません。")

            # 時間チェック（9:00〜18:00）
            if dt.time() < settings.RESERVATION_START_TIME or dt.time() > settings.RESERVATION_END_TIME:
                raise forms.ValidationError("予約時間は9:00〜18:00の間で指定してください。")

        return dt
    

    # チェックボックスの設定
    RAIIN_RIYUU = forms.MultipleChoiceField(
        choices=RAIIN_RIYUU_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    ZYOUHOU_MOTO = forms.MultipleChoiceField(
        choices=ZYOUHOU_MOTO_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    # 入力フォームの指定
    class Meta:

        # HTMLで定義するクラスを定義
        CLASS_FORM_CONTROL = "form-control"

        model = T_KANZYA
        fields = '__all__'

        widgets = {
            "SEINENGAPPI": forms.DateInput(
                attrs={"type": "date", 
                       "class": CLASS_FORM_CONTROL,
                       "placeholder": "例：1990/01/01"
                       }
            ),
            "EMAIL_ADDRESS": forms.EmailInput(
                attrs={"class": CLASS_FORM_CONTROL}
            ),
            "ZIKAI_YOYAKUBI": forms.DateTimeInput(
                attrs={"type": "datetime-local", 
                       "class": CLASS_FORM_CONTROL,
                       "step": "1800",
                       "readonly": "readonly"
                }
            ),
            "UKETSUKEBI": forms.DateTimeInput(
                attrs={"type": "datetime-local", 
                       "class": CLASS_FORM_CONTROL
                }
            )
        }

class ShikaishiDataForm(forms.ModelForm):

    # 入力フォームの指定
    class Meta:

        model = M_SHIKAISHI
        fields = '__all__'