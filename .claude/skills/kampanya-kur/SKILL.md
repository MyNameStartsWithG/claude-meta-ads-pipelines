---
name: kampanya-kur
description: Uçtan uca Meta kampanya kurulumu - brief'ten kampanya, ad set ve reklam oluşturur; hepsi PAUSED kurulur, yayına alma ayrı onayla yapılır. Tetikleyici - "kampanya kur", "yeni reklam aç", "lansman kampanyası hazırla", /kampanya-kur.
---

# Pipeline 4 — Kampanya Kurulumu

Her şey **PAUSED** kurulur. `guardrails.json` bunu hook ile zorunlu kılar.

## 1. Brief (eksikse sor, tahmin etme)
- Hesap ve Facebook Sayfası (`ads_get_ad_accounts`, `ads_get_pages_for_business`)
- Hedef: bilinirlik / trafik / etkileşim / potansiyel müşteri / uygulama / satış
- Günlük veya toplam bütçe, başlangıç–bitiş tarihi
- Hedef kitle (yoksa `hedef-kitle` pipeline'ını çalıştır)
- Kreatif: görsel/video (mevcut kreatif ID'si veya kullanıcının verdiği materyal), ana metin, başlık, CTA, hedef URL
- Dönüşüm hedefliyorsa: hangi piksel/dataset ve olay → kurulumdan önce `olcum-saglik` ile kontrol et

## 2. Plan
Kurulacak yapıyı tablo olarak göster:
`Kampanya (hedef, bütçe tipi) → Ad set(ler) (kitle, yerleşim, bütçe, takvim) → Reklam(lar) (kreatif, metin, CTA, URL)`
Adlandırma: `YYYYMM_Hedef_Ürün_Kitle` (ör. `202611_Satis_KisKoleksiyon_Genis`).
Metin varyantı istenirse 3 başlık + 3 ana metin öner; politika ihlali riski olan iddialardan (kesin sonuç, "garanti", kişisel özelliklere hitap) kaçın.

## 3. Onaydan sonra kurulum
1. `ads_create_campaign` — status: PAUSED
2. `ads_create_ad_set` — her kitle için, status: PAUSED
3. `ads_create_ad` — her reklam, status: PAUSED
Bir adım hata verirse dur; o ana kadar oluşturulanları listele, yarım kalan yapıyı kullanıcıya bildir.

## 4. Yayına alma
Kullanıcıya özet + ID'leri göster ve **ayrıca** "yayına alayım mı?" diye sor. Yalnızca açık "evet" gelirse `ads_activate_entity` ile kampanya → ad set → reklam sırasıyla aktifleştir.

## 5. Kayıt
`reports/kampanya-YYYY-MM-DD-<ad>.md`: brief, yapı, ID'ler, durum.
