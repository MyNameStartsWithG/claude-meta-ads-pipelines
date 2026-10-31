---
name: butce-optimize
description: Meta kampanyaları arasında bütçe yeniden dağıtımı. Performansa göre artırma/azaltma/durdurma planı çıkarır, kullanıcı onaylarsa ads_update_entity ile uygular. Tetikleyici - "bütçeyi optimize et", "bütçeyi kazanana kaydır", "zarar eden kampanyaları kıs", /butce-optimize.
---

# Pipeline 2 — Bütçe Optimizasyonu (önce plan, sonra onaylı uygulama)

## Kurallar
- Tek seferde bir bütçeyi **en fazla %20** değiştir (öğrenme aşamasını sıfırlamamak için).
- Öğrenme aşamasındaki (son 7 günde < 50 dönüşüm) ad set'lere dokunma; planda "öğreniyor" diye işaretle.
- Toplam günlük harcama, kullanıcı aksini söylemedikçe **sabit kalsın**: azaltılan tutar kazananlara aktarılır.
- Bütçeler hesabın para biriminin en küçük biriminde (kuruş/cent) gönderilir. `guardrails.json` sınırlarını aşan değer hook tarafından reddedilir; sınırı aşmaya çalışma, kullanıcıya bildir.
- Yayına alma (ACTIVE) bu pipeline'ın işi değil.

## Adımlar
1. Son 7 ve 14 günün verisini `ads_get_ad_entities` + `ads_insights_performance_trend` ile çek (bütçenin CBO'da kampanya düzeyinde mi, ad set düzeyinde mi olduğunu not et).
2. Her birimi sınıflandır:
   - **Ölçekle** — CPA hedefin ≤ %80'i veya ROAS hedefin ≥ %120'si → +%10–20
   - **Koru** — hedefin ±%20'si
   - **Kıs** — CPA hedefin %120–200'ü → −%10–20
   - **Durdur önerisi** — CPA > hedefin 2 katı ve ≥ 2× hedef CPA harcanmış, dönüşüm yok
   Hedef CPA/ROAS bilinmiyorsa kullanıcıya sor; sormadan hesap ortalamasını kullanma.
3. **Plan tablosu** göster: birim, mevcut bütçe, yeni bütçe, değişim %, gerekçe. Toplam günlük harcamanın önce/sonra değerini ekle.
4. Kullanıcıdan açık onay al ("uygula" / satır numaraları). Onay yoksa dur.
5. Onaylanan her satır için `ads_update_entity` çağır. Durdurma: `status: PAUSED`.
6. `reports/butce-YYYY-MM-DD.md` dosyasına planı, uygulananları ve hook'un reddettiklerini yaz.
