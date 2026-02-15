document.addEventListener("DOMContentLoaded", function() {

    const btn = document.getElementById("confirmBtn");               //予約確定ボタン
    const btnNowDateShow = document.getElementById('BtNowDateShow'); //本日の予約を表示ボタン

    // 予約確定ボタンで最終確認を行う処理
    if (btn) {
        btn.addEventListener("click", function(e) {
            if (!confirm("この日時で予約を確定します。患者様にメールで予約の連絡を行いますがよろしいですか？")) {
                e.preventDefault();
            }
        });
    }

    //本日の予約を表示ボタン
    if (btnNowDateShow){
        btnNowDateShow.addEventListener("click", function(e){
            // 現在の日時を取得
            const now = new Date();
            const year = now.getFullYear()
            const month = now.getMonth() + 1;
            const day = now.getDate();
            window.location.href = '/YoyakuKanri/?YoyakubiS=' + year + '-' + month + '-' + day + 
                                        'T09%3A00&YoyakubiE=' + year + '-' + month + '-' + day + 
                                        'T18%3A00'
        });
    }
});