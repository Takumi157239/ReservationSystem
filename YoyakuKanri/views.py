from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import T_KANZYA
from .forms import KanzyaDataForm
from datetime import datetime, timedelta
from django.conf import settings
from common.QRCode import QRCodeOperation
import calendar


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
            form.save()
            return redirect("MonshinhyouClose")
    else:
        form = KanzyaDataForm()
    return render(request, "YoyakuKanri/MonshinhyouCreate.html", {"form": form})


# 問診票を閉じたときの画面
@login_required
def MonshinhyouClose(request):
    return render(request, "YoyakuKanri/MonshinhyouClose.html")


# 患者データ編集画面
@login_required
def KanzyaDataEdit(request, pk):

    obj = T_KANZYA.objects.get(pk=pk)

    if request.method == "POST":
        form = KanzyaDataForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect("YoyakuKanri")  # 保存後、一覧へ戻る
    else:
        form = KanzyaDataForm(instance=obj)
    
    return render(request, "YoyakuKanri/KanzyaDataEdit.html", {"form": form, 'object': obj})


# 次回予約画面
@login_required
def ZikaiYoayakuShow(request, ID, year, month):

    # 30分刻みのデータを取得する
    dict_time_slots = GetTimeSlots(year, month)

    # 当月の予約されている日と時間を取得する
    dict_yoyaku_table = GetMonthYoyakubiTable(year, month, dict_time_slots["time_slots"], dict_time_slots["days"])

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
        obj.save()

        
        # QRコードをメールで送る処理
        with QRCodeOperation() as qrCodeOperation:
            qrCodeOperation.QRCodeCreate(ID)                                     #QRコード生成
            qrCodeOperation.QRCodeSendMail(obj.EMAIL_ADDRESS, ZikaiYoyakubi)     #メール送信


        return redirect("KanzyaDataEdit", ID)


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
    _, last_day = calendar.monthrange(argYear, argMonth)
    days = list(range(1, last_day + 1))

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
        for day in argDays:
            dt = datetime(argYear, argMonth, day, slot.hour, slot.minute)
            is_reserved = YoyakubiTimes.filter(ZIKAI_YOYAKUBI=dt).exists()
            row.append({
                "day": day,
                "slot": slot,
                "is_reserved": is_reserved,
            })
        table.append({
            "slot": slot,
            "cells": row
        })

    return table

