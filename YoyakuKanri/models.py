from django.db import models

# Create your models here.

# 患者データ
class T_KANZYA(models.Model):
    ID = models.AutoField(primary_key=True)
    KANZYA_NAME = models.CharField(max_length=128)
    SEINENGAPPI = models.DateField()
    EMAIL_ADDRESS = models.EmailField()
    RAIIN_RIYUU = models.IntegerField()
    RAIIN_RIYUU_SONOTA = models.TextField(null=True, blank=True)
    ZYOUHOU_MOTO = models.IntegerField()
    ZYOUHOU_MOTO_SONOTA = models.TextField(null=True, blank=True)
    TANTOU_SHIKAISHI_ID = models.IntegerField()
    SONOTA_YOUBOU = models.TextField(null=True, blank=True)
    UPDATE_DATE = models.DateTimeField(auto_now=True)
    CREATE_DATE = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "T_KANZYA"


# 受信歴
class T_JUSHINREKI(models.Model):
    ID = models.AutoField(primary_key=True)
    KANZYA_ID = models.IntegerField()
    SHIKAISHI_ID = models.IntegerField()
    JUSHINBI = models.DateField()
    JUSHIN_RIYUU = models.TextField()
    RYOUKIN_ZENGAKU = models.DecimalField(max_digits=10, decimal_places=2)
    RYOUKIN_KANZYAFUTAN = models.DecimalField(max_digits=10, decimal_places=2)
    UPDATE_DATE = models.DateTimeField(auto_now=True)
    CREATE_DATE = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "T_JUSHINREKI"


# 予約データ
class T_YOYAKU(models.Model):
    ID = models.AutoField(primary_key=True)
    KANZYA_ID = models.IntegerField()
    YOYAKUBI = models.DateTimeField()
    UKETSUKEBI = models.DateTimeField()
    BIKOU = models.TextField()
    UPDATE_DATE = models.DateTimeField(auto_now=True)
    CREATE_DATE = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "T_YOYAKU"


# 歯科医師
class M_SHIKAISHI(models.Model):
    ID = models.AutoField(primary_key=True)
    SHIKAI_NAME = models.CharField(max_length=128)
    YAKUSHOKU = models.IntegerField()

    class Meta:
        db_table = "M_SHIKAISHI"


# コンボボックス値
class M_CMB_ITEM(models.Model):
    ID = models.AutoField(primary_key=True)
    CMB_TYPE = models.CharField(max_length=128)
    CMB_VALUE = models.CharField(max_length=128)

    class Meta:
        db_table = "M_CMB_ITEM"