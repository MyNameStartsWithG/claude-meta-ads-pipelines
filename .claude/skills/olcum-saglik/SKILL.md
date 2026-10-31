---
name: olcum-saglik
description: Meta piksel / Conversions API (dataset) ve katalog sağlık kontrolü - olay sayıları, eşleşme kalitesi, tekilleştirme, hatalar ve katalog teşhisleri. Salt okunur. Tetikleyici - "piksel çalışıyor mu", "dönüşümler gelmiyor", "CAPI kontrol", "katalog hatası", /olcum-saglik.
---

# Pipeline 5 — Ölçüm ve Katalog Sağlığı (salt okunur)

## Adımlar
1. Hesaba bağlı dataset'leri bul (`ads_get_dataset_details`).
2. Her dataset için:
   - `ads_get_dataset_stats` — son 7 günde olay bazında sayılar (PageView, ViewContent, AddToCart, InitiateCheckout, Purchase, Lead); tarayıcı vs. sunucu payı ve tekilleştirme oranı.
   - `ads_get_dataset_quality` — olay eşleşme kalitesi (EMQ). 6'nın altı zayıf.
   - `ads_get_errors` — son hatalar.
3. Kontrol listesi:
   - Huni sırası mantıklı mı? (Purchase > AddToCart ise yanlış tetikleme şüphesi)
   - Purchase olayında `value` ve `currency` geliyor mu?
   - Sunucu olayları varsa `event_id` ile tekilleştirme çalışıyor mu?
   - Herhangi bir olay 24 saattir sıfır mı?
4. Katalog varsa: `ads_catalog_get_catalogs` → `ads_catalog_get_diagnostics` ve `ads_catalog_get_product_feed_details`; reddedilen ürün sayısı ve en sık hata.
5. Belirsiz bir hata kodu için `ads_get_help_article` ile Meta'nın yardım makalesini getir.

## Çıktı
`reports/olcum-YYYY-MM-DD.md`: her kontrol için ✅ / ⚠️ / ❌, bulgu ve düzeltme adımı (geliştiriciye iletilebilecek netlikte).
