---
name: hedef-kitle
description: Meta için hedef kitle tasarımı - ürün/hizmet tanımından ve mevcut performans verisinden ilgi alanı, demografi, konum ve Advantage+ kitle önerileri çıkarır; onaylanınca PAUSED ad set olarak kurar. Tetikleyici - "hedef kitle oluştur", "kime reklam vermeliyim", "yeni kitle test et", /hedef-kitle.
---

# Pipeline 3 — Hedef Kitle

## Adımlar
1. **Brief** — Kullanıcıdan al (yoksa sor): ürün/hizmet, fiyat aralığı, satış bölgesi, ideal müşteri, kampanya hedefi.
2. **Veri** — Varsa mevcut ad set'leri `ads_get_ad_entities` ile çek; en iyi CPA'lı ad set'lerin hedeflemesini referans al. `ads_insights_advertiser_context` ile sektör bağlamını ekle.
3. **3 kitle varyantı** öner, her biri birbirinden belirgin farklı olsun:
   - **A — Geniş / Advantage+**: yalnızca konum + yaş + dil, algoritmaya alan bırakır.
   - **B — İlgi alanı**: 3–6 ilgili ilgi alanı, ortak tema.
   - **C — Sıcak kitle / benzer kitle**: hesapta mevcut özel/benzer kitleler varsa.
   Her varyant için: konum, yaş, cinsiyet, ilgi alanları, yerleşimler, önerilen günlük bütçe ve test süresi (en az 7 gün).
4. Özel reklam kategorisi (konut, istihdam, kredi, sosyal/siyasi) söz konusuysa hedefleme kısıtlarını hatırlat; yaş/cinsiyet/posta kodu daraltması yapma.
5. Kullanıcı onaylarsa seçilen varyantları mevcut bir kampanyanın altına `ads_create_ad_set` ile **status: PAUSED** kur. Kampanya yoksa `kampanya-kur` pipeline'ına yönlendir.
6. Oluşan ad set ID'lerini ve ayarlarını `reports/kitle-YYYY-MM-DD.md` dosyasına yaz.
