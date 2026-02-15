document.addEventListener("DOMContentLoaded", function() {

    const btn = document.getElementById("confirmBtn");

    if (btn) {

        // 予約確定ボタンで最終確認を行う処理
        btn.addEventListener("click", function(e) {
            if (!confirm("この日時で予約を確定します。患者様にメールで予約の連絡を行いますがよろしいですか？")) {
                e.preventDefault();
            }
        });
    }
});