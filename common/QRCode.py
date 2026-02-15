from django.conf import settings
from datetime import datetime
from django.core.mail import EmailMessage
import qrcode
import os

class QRCodeOperation:

    # コンストラクタ
    def __init__(self):
        
        now = datetime.now().strftime('%Y年%m月%d日%H%M%S')

        filename = "qr" + now + ".png"
        save_path = os.path.join(settings.MEDIA_ROOT, "qrcodes", filename)

        # QRコードのパスを作成
        self.save_path = save_path


    def __enter__(self):
        return self
    
    
    # インスタンス破棄
    def __exit__(self, exc_type, exc_val, exc_tb):

        # QRコードのファイルを削除する
        if os.path.exists(self.save_path):
            os.remove(self.save_path)


    # QRコード作成
    def QRCodeCreate(self, argID):

        # QRコード生成
        img = qrcode.make(argID)

        # 保存
        img.save(self.save_path)

    
    # QRコードをメールで送信する
    def QRCodeSendMail(self, argEmail, argYoyakubi):
        email = EmailMessage(
            subject='次回予約日のお知らせ',
            body=argYoyakubi,
            from_email=None,
            to=[argEmail],
        )
    
        email.attach_file(self.save_path)
        email.send()