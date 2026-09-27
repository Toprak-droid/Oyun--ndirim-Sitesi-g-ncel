const aramaKutusu = document.getElementById("arama");
const onerilerAlani = document.getElementById("oneriler");
const oyunKartlari = Array.from(
    document.querySelectorAll(".oyun-karti")
);

aramaKutusu.addEventListener("input", function () {
    const arama = aramaKutusu.value
        .toLocaleLowerCase("tr-TR")
        .trim();

    onerilerAlani.innerHTML = "";

    const eslesenKartlar = oyunKartlari.filter(function (kart) {
        const oyunAdi = kart.querySelector("h2")
            .textContent
            .toLocaleLowerCase("tr-TR");

        return oyunAdi.includes(arama);
    });

    oyunKartlari.forEach(function (kart) {
        kart.style.display = eslesenKartlar.includes(kart)
            ? "block"
            : "none";
    });

    if (arama !== "") {
        eslesenKartlar.slice(0, 8).forEach(function (kart) {
            const oneri = document.createElement("div");
            oneri.className = "oneri";
            oneri.textContent = kart.querySelector("h2").textContent;

            oneri.addEventListener("click", function () {
                aramaKutusu.value = oneri.textContent;
                onerilerAlani.innerHTML = "";

                oyunKartlari.forEach(function (digerKart) {
                    digerKart.style.display =
                        digerKart === kart ? "block" : "none";
                });
            });

            onerilerAlani.appendChild(oneri);
        });
    }
});
