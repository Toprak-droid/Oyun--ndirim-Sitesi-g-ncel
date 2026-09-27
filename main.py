from flask import Flask, render_template, request, redirect, url_for
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from pathlib import Path
import json
import time


app = Flask(__name__)

# Dosyaların proje klasöründe tutulmasını sağlar
PROJE_KLASORU = Path(__file__).parent
ISTEK_DOSYASI = PROJE_KLASORU / "oyun_istekleri.txt"

# API verilerini 5 dakika önbellekte tutar
veri_onbellek = {
    "zaman": 0,
    "oyunlar": []
}


def indirimleri_getir():
    """
    Steam ve Epic Games indirimlerini CheapShark API'den alır.
    """

    simdi = time.time()

    # Son güncellemeden itibaren 5 dakika geçmediyse eski veriyi kullan
    if simdi - veri_onbellek["zaman"] < 300:
        return veri_onbellek["oyunlar"]

    oyunlar = []

    # CheapShark mağaza kodları
    # 1  = Steam
    # 25 = Epic Games
    magaza_listesi = [
        ("1", "Steam"),
        ("25", "Epic Games")
    ]

    for magaza_kodu, magaza_adi in magaza_listesi:
        parametreler = urlencode({
            "storeID": magaza_kodu,
            "pageSize": 100,
            "page": 0
        })

        api_adresi = (
            f"https://www.cheapshark.com/api/1.0/deals?"
            f"{parametreler}"
         )

        try:
            istek = Request(
                api_adresi,
                headers={
                    "User-Agent": "OyunIndirimSitesi/1.0"
                }
            )

            with urlopen(istek, timeout=20) as cevap:
                veriler = json.loads(
                    cevap.read().decode("utf-8")
                )

            for oyun in veriler:
                try:
                    indirim_orani = float(
                        oyun.get("savings", 0)
                    )
                except (TypeError, ValueError):
                    indirim_orani = 0

                deal_id = oyun.get("dealID", "")

                oyunlar.append({
                    "ad": oyun.get(
                        "title",
                        "İsimsiz oyun"
                    ),
                    "magaza": magaza_adi,
                    "eski_fiyat": (
                        f"${oyun.get('normalPrice', '0')}"
                    ),
                    "yeni_fiyat": (
                        f"${oyun.get('salePrice', '0')}"
                    ),
                    "indirim": (
                        f"%{indirim_orani:.0f} indirim"
                    ),
                    "resim": oyun.get("thumb", ""),
                    "link": (
                        "https://www.cheapshark.com/redirect"
                        f"?dealID={deal_id}"
                     )
                })

        except Exception as hata:
            print(
                f"{magaza_adi} verisi alınamadı: {hata}"
            )

    # En yüksek indirim oranlarını üstte göster
    def indirim_degeri(oyun):
        try:
            return float(
                oyun["indirim"]
                .replace("%", "")
                .replace(" indirim", "")
            )
        except ValueError:
            return 0

    oyunlar.sort(
        key=indirim_degeri,
        reverse=True
    )

    # Verileri önbelleğe kaydet
    veri_onbellek["zaman"] = simdi
    veri_onbellek["oyunlar"] = oyunlar

    return oyunlar


@app.route("/")
def ana_sayfa():
    """
    Ana sayfayı ve indirimli oyunları gösterir.
    """

    oyunlar = indirimleri_getir()

    return render_template(
        "index.html",
        oyunlar=oyunlar
    )


@app.route("/oyun-istegi", methods=["POST"])
def oyun_istegi():
    """
    Kullanıcının istediği oyunu dosyaya kaydeder.
    """

    oyun_adi = request.form.get(
        "oyun_adi",
        ""
    ).strip()

    magaza = request.form.get(
        "magaza",
        "Fark etmez"
    ).strip()

    if oyun_adi:
        tarih = time.strftime(
            "%d.%m.%Y %H:%M"
        )

        with open(
            ISTEK_DOSYASI,
            "a",
            encoding="utf-8"
        ) as dosya:
            dosya.write(
                f"[{tarih}] "
                f"Oyun: {oyun_adi} | "
                f"Mağaza: {magaza}\n"
            )

    return redirect(
        url_for("ana_sayfa")
    )


if __name__ == "__main__":
    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
