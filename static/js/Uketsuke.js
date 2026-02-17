document.addEventListener("DOMContentLoaded", function() {

    let qrScanner = null;
    let isScanning = false;

    const BtUketsuke = document.getElementById('bt-uketsuke');              //受付はこちらをタップしてくださいボタン
    const UketsukeReader = document.getElementById('uketsuke-reader');      //QRコード読み取り画面
    const BtUketsukeCancel = document.getElementById('bt-uketsuke-cancel'); //QRコード読み取りキャンセルボタン


    // 受付はこちらをタップしてくださいボタン処理
    BtUketsuke.addEventListener('click', function(){

        UketsukeReader.style.display = "block";
        BtUketsukeCancel.style.display = "block";
        BtUketsuke.style.display = "none";

        qrScanner = new Html5Qrcode("uketsuke-reader");

        qrScanner.start(
            { facingMode: "user" }, // 前面カメラ設定
            { fps: 10, qrbox: 500 }, //解析範囲
            (decodedText) => {
                stopScanner()
                onQrScanned(decodedText)
            }
        );

        isScanning = true;
    });


    // キャンセルボタン処理
    BtUketsukeCancel.addEventListener("click", function(){
        stopScanner();
    });


    //QRコード読み取り画面を閉じる処理
    function stopScanner() {
        if (qrScanner && isScanning) {
            qrScanner.stop().then(() => {
                
                BtUketsuke.style.display = "block";
                UketsukeReader.style.display = "none";
                BtUketsukeCancel.style.display = "none";
                qrScanner = null;
                isScanning = false;
            });
        }
    }


    //QRコードスキャン後の処理
    function onQrScanned(qrText) {

        //トークン
        const CsrfToken = document.getElementById('csrf-token').value           

        fetch("/YoyakuKanri/UketsukeKanryou", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": CsrfToken
            },
            body: JSON.stringify({
                qr_value: qrText
            })
            })
        .then(response => response.json())
        .then(data => {
            alert(data.status);
        });
    }

});