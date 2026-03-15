import calendar
import json
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import T_KANZYA, M_SHIKAISHI, T_JUSHINREKI
from .forms import KanzyaDataForm, ShikaishiDataForm, JushinrekiDataForm
from datetime import datetime, timedelta, date
from django.conf import settings
from common.QRCode import QRCodeOperation
from django.http import JsonResponse

# 予約管理TOP
@login_required
def index(request):

    #すべての患者データを取得
    KanzyaData = T_KANZYA.objects.all()

    #各検索条件を取得
    OkyakusamaID = request.GET.get("OkyakusamaID")  #お客様ID
    Kanzyamei = request.GET.get('Kanzyamei')        #患者名
    YoyakubiS = request.GET.get('YoyakubiS')        #予約日Start
    YoyakubiE = request.GET.get('YoyakubiE')        #予約日End
    UketsukebiS = request.GET.get('UketsukebiS')    #受付日Start
    UketsukebiE = request.GET.get('UketsukebiE')    #受付日End
    
    #お客様ID
    if OkyakusamaID:
        KanzyaData = KanzyaData.filter(ID__exact = OkyakusamaID)

    #患者名
    if Kanzyamei:
        KanzyaData = KanzyaData.filter(KANZYA_NAME__contains = Kanzyamei)
    
    #予約日
    if YoyakubiS and YoyakubiE:
        KanzyaData = KanzyaData.filter(ZIKAI_YOYAKUBI__gte = YoyakubiS, ZIKAI_YOYAKUBI__lt = YoyakubiE)

    #受付日
    if UketsukebiS and UketsukebiE:
        KanzyaData = KanzyaData.filter(UKETSUKEBI__gte = UketsukebiS, UKETSUKEBI__lt = UketsukebiE)

    return render(request, "YoyakuKanri/YoyakuKanri.html", {"kanzyadatas": KanzyaData})


# 問診票
@login_required
def MonshinhyouCreate(request):

    if request.method == "POST":
        form = KanzyaDataForm(request.POST)
        if form.is_valid():
            new_kanzya = form.save()

            # 受信歴に新規レコード追加
            T_JUSHINREKI.objects.create(KANZYA_ID=new_kanzya.ID, JUSHINBI=datetime.now().date())

            return redirect("MonshinhyouClose")
    else:
        form = KanzyaDataForm()
    return render(request, "YoyakuKanri/MonshinhyouCreate.html", {"form": form})


# 問診票を閉じたときの画面
@login_required
def MonshinhyouClose(request):
    return render(request, "YoyakuKanri/MonshinhyouClose.html")


# 受付画面
@login_required
def Uketsuke(request):
    return render(request, "YoyakuKanri/Uketsuke.html")


# 受付完了
@login_required
def UketsukeKanryou(request):

    if request.method == "POST":

        data = json.loads(request.body)
        qr_value = data.get("qr_value")

        # 現在日付を受付日とする
        now = datetime.now()

        # 受付日の登録
        obj = get_object_or_404(T_KANZYA, pk=qr_value)
        obj.UKETSUKEBI = now
        obj.save()

        # 受験歴に受付した日付を登録する
        T_JUSHINREKI.objects.create(KANZYA_ID=qr_value, JUSHINBI=now.date())

        return JsonResponse({"status": "受付が完了しました"})

# 患者データ編集画面
@login_required
def KanzyaDataEdit(request, pk):

    obj = T_KANZYA.objects.get(pk=pk)
    JushinData = T_JUSHINREKI.objects.filter(KANZYA_ID=pk)

    if request.method == "POST":
        form = KanzyaDataForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect("YoyakuKanri")  # 保存後、一覧へ戻る
    else:
        form = KanzyaDataForm(instance=obj)
    
    return render(request, "YoyakuKanri/KanzyaDataEdit.html", {"form": form, 'object': obj, 'jushinDatas': JushinData })


# 受診歴編集画面
@login_required
def JushinrekiEdit(request, ID):

    JushinData = T_JUSHINREKI.objects.get(ID=ID)

    if request.method == "POST":
        form = JushinrekiDataForm(request.POST, instance=JushinData)
        if form.is_valid():
            form.save()
            return redirect("KanzyaDataEdit", JushinData.KANZYA_ID)  # 保存後、患者データ編集画面へ戻る
    else:
        form = JushinrekiDataForm(instance=JushinData)

    return render(request, "YoyakuKanri/JushinrekiDataEdit.html", {"form": form, 'JushinData': JushinData})


# 次回予約画面
@login_required
def ZikaiYoayakuShow(request, ID, year, month):

    # 30分刻みのデータを取得する
    dict_time_slots = GetTimeSlots(year, month)

    # 当月の予約されている日と時間を取得する
    dict_yoyaku_table = GetMonthYoyakubiTable(year, month, dict_time_slots["time_slots"], dict_time_slots["days"])

    # 患者名を取得する
    KANZYA_DATA = T_KANZYA.objects.get(pk=ID)

    # 画面に渡すデータを辞書型に格納
    context = {
        "ID": ID,
        "year": year,
        "month": month,
        "days": dict_time_slots["days"],
        "prev_year": dict_time_slots["prev_year"],
        "prev_month": dict_time_slots["prev_month"],
        "next_year": dict_time_slots["next_year"],
        "next_month": dict_time_slots["next_month"],
        "KANZYA_NAME": KANZYA_DATA.KANZYA_NAME,
        "dict_yoyaku_table": dict_yoyaku_table
    }

    return render(request, "YoyakuKanri/ZikaiYoyaku.html", context)



# 次回予約確認画面表示
@login_required
def ZikaiYoyakuKakunin(request, ID, year, month, day, hour, minute):

    # 予約日をdatetimeの形に変換する
    ZikaiYoyakubi = datetime(year, month, day, hour, minute)

    # 患者名を取得する
    KANZYA_DATA = T_KANZYA.objects.get(pk=ID)

    context = {
        "ID": ID,
        "KANZYA_NAME": KANZYA_DATA.KANZYA_NAME,
        "ZikaiYoyakubi": ZikaiYoyakubi,
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "minute": minute
    }

    return render(request, "YoyakuKanri/ZikaiYoyakuKakunin.html", context)


# 次回予約完了
@login_required
def ZikaiYoyakuKanryou(request, ID, year, month, day, hour, minute):

    if request.method == "POST":

        # 予約日をdatetimeの形に変換する
        ZikaiYoyakubi = datetime(year, month, day, hour, minute)

        obj = get_object_or_404(T_KANZYA, pk=ID)
        obj.ZIKAI_YOYAKUBI = ZikaiYoyakubi
        obj.UKETSUKEBI = None
        obj.save()

        
        # QRコードをメールで送る処理
        with QRCodeOperation(ID) as qrCodeOperation:
            qrCodeOperation.QRCodeCreate()                                       #QRコード生成
            qrCodeOperation.QRCodeSendMail(obj.EMAIL_ADDRESS, ZikaiYoyakubi)     #メール送信


        return redirect("KanzyaDataEdit", ID)



# 歯科医師データ画面-----------------------------------------------------------------------------

# 歯科医師リスト表示
@login_required
def ShikaishiList(request):

    # 歯科医師データ取得
    ShikaishiData = M_SHIKAISHI.objects.all()

    return render(request, "Shikaishi/ShikaishiList.html", {"ShikaishiDatas": ShikaishiData})


# 歯科医師編集画面
@login_required
def ShikaishiEdit(request, add_or_edit=-1, ID=-1):

    if request.method == "POST":

        if add_or_edit == 0:
            form = ShikaishiDataForm(request.POST)

        else:
            ShikaishiData = M_SHIKAISHI.objects.get(pk=ID)
            form = ShikaishiDataForm(request.POST, instance=ShikaishiData)

        if form.is_valid():
            form.save()
            return redirect("ShikaishiList")  # 保存後、一覧へ戻る
    else:

        # 新規登録
        if add_or_edit == 0:
            form = ShikaishiDataForm()
        
        # 編集
        else:
            ShikaishiData = M_SHIKAISHI.objects.get(pk=ID)
            form = ShikaishiDataForm(instance=ShikaishiData)

        return render(request, "Shikaishi/ShikaishiEdit.html", {"form": form, "add_or_edit": add_or_edit})


# ここからは関数----------------------------------------------------------------------------

# 営業時間内の30分刻みの時間を取得する関数
def GetTimeSlots(argYear, argMonth):
    # 前月計算
    if argMonth == 1:
        prev_year = argYear - 1
        prev_month = 12
    else:
        prev_year = argYear
        prev_month = argMonth - 1

    # 来月計算
    if argMonth == 12:
        next_year = argYear + 1
        next_month = 1
    else:
        next_year = argYear
        next_month = argMonth + 1

    # 月の日数取得
    days = []
    weekday_jp = ["(月)", "(火)", "(水)", "(木)", "(金)", "(土)", "(日)"]
    _, last_day = calendar.monthrange(argYear, argMonth)
    for day in range(1, last_day + 1):
        d = date(argYear, argMonth, day)
        days.append({
            "day": day,
            "weekday": weekday_jp[d.weekday()],
        })

    # 30分刻み生成
    start_time = settings.RESERVATION_START_TIME
    end_time = settings.RESERVATION_END_TIME

    current = datetime.combine(datetime.today(), start_time)
    end = datetime.combine(datetime.today(), end_time)

    time_slots = []

    while current <= end:
        time_slots.append(current.time())
        current += timedelta(minutes=30)

    # 辞書型に値を格納する
    slots_dict = {"prev_year": prev_year, "prev_month": prev_month,
                  "next_year": next_year, "next_month": next_month,
                  "time_slots":time_slots, "days": days}

    return slots_dict


# 指定された月の予約時間を取得する関数
def GetMonthYoyakubiTable(argYear, argMonth, argSlots, argDays):

    table = []

    # 月の開始・終了
    start_date = datetime(argYear, argMonth, 1)

    if argMonth == 12:
        end_date = datetime(argYear + 1, 1, 1)
    else:
        end_date = datetime(argYear, argMonth + 1, 1)

    YoyakubiTimes = T_KANZYA.objects.filter(
        ZIKAI_YOYAKUBI__gte=start_date,
        ZIKAI_YOYAKUBI__lt=end_date
    )

    for slot in argSlots:
        row = []
        for d in argDays:
            dt = datetime(argYear, argMonth, int(d["day"]), slot.hour, slot.minute)
            is_reserved = YoyakubiTimes.filter(ZIKAI_YOYAKUBI=dt).exists()
            row.append({
                "day": int(d["day"]),
                "weekday": d["weekday"],
                "slot": slot,
                "is_reserved": is_reserved,
            })
        table.append({
            "slot": slot,
            "cells": row
        })

    return table

