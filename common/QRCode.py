from django.conf import settings
from datetime import datetime
from django.core.mail import EmailMessage
from YoyakuKanri.models import T_KANZYA
import qrcode
import os

class QRCodeOperation:

    # コンストラクタ
    def __init__(self, argID):
        
        # QRコードを生成するときのファイルパスを指定
        now = datetime.now().strftime('%Y年%m月%d日%H%M%S')
        filename = "qr" + now + ".png"
        save_path = os.path.join(settings.MEDIA_ROOT, "qrcodes", filename)

        # 患者名を取得
        KanzyaName = T_KANZYA.objects.get(pk=argID)

        # QRコードのパス・ID・患者名をselfに指定
        self.save_path = save_path
        self.ID = argID
        self.KanzyaName = KanzyaName


    def __enter__(self):
        return self
    
    
    # インスタンス破棄
    def __exit__(self, exc_type, exc_val, exc_tb):

        # QRコードのファイルを削除する
        if os.path.exists(self.save_path):
            os.remove(self.save_path)


    # QRコード作成
    def QRCodeCreate(self):

        # QRコード生成
        img = qrcode.make(self.ID)

        # 保存
        img.save(self.save_path)

    
    # QRコードをメールで送信する
    def QRCodeSendMail(self, argEmail, argYoyakubi):

        # メールのテンプレートを読み込む
        content = ""
        mail_file_path = os.path.join(settings.BASE_DIR, "common", "data", "MailTemplate.txt")

        with open(mail_file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        
        #テンプレートの文字列を置換
        content = content.replace("KANZYA_NAME", str(self.KanzyaName))                               #患者名
        content = content.replace("ZIKAI_YOYAKUBI", argYoyakubi.strftime('%Y年%m月%d日 %H時%M分～'))  #予約日

        email = EmailMessage(
            subject='次回予約日のお知らせ',
            body=content,
            from_email=None,
            to=[argEmail],
        )
    
        email.attach_file(self.save_path)
        email.send()