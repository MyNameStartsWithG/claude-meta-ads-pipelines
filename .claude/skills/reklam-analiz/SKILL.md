---
name: reklam-analiz
description: Meta reklam hesabının performans denetimi. Hesapları, kampanya/ad set/reklamları, trendleri, anomalileri ve sektör kıyaslarını çekip reports/ altına Türkçe bir rapor yazar. Yalnızca okur. Tetikleyici - "reklamlarımı analiz et", "kampanyalar nasıl gidiyor", "haftalık reklam raporu", /reklam-analiz.
---

# Pipeline 1 — Performans Analizi (salt okunur)

Bu pipeline hiçbir şeyi değiştirmez. Yazma aracı çağırma.

## Girdi
- Hesap: kullanıcı belirtmediyse `ads_get_ad_accounts` ile listele; birden fazlaysa sor.
- Dönem: belirtilmediyse son 7 gün, önceki 7 günle kıyaslı.

## Adımlar
1. **Bağlam** — `ads_insights_advertiser_context` (sektör, ülke) ve `ads_get_opportunity_score`.
2. **Envanter** — `ads_get_ad_entities` ile aktif kampanya, ad set ve reklamları çek. Durdurulmuş olanları ayrı say, analiz dışı bırak.
3. **Trend** — Her aktif kampanya için `ads_insights_performance_trend`: harcama, gösterim, CTR, CPC, CPM, dönüşüm, CPA, ROAS.
4. **Anomali** — `ads_insights_anomaly_signal` ile sapan KPI'leri bul.
5. **Kıyas** — `ads_insights_industry_benchmark` ve `ads_insights_auction_ranking_benchmarks` ile sektör ortalamasına göre konumla.
6. **Teşhis** — Her sorun için olası nedeni yaz (kreatif yorgunluğu: frekans > 3 ve düşen CTR; hedef kitle daralması: yükselen CPM; ölçüm sorunu: dönüşüm sıfıra düştü ama tıklama sürüyor → `olcum-saglik` öner).

## Çıktı
`reports/analiz-YYYY-MM-DD.md` dosyası, şu bölümlerle:
- **Özet** — 3 madde: en iyi, en kötü, en acil.
- **KPI tablosu** — kampanya başına metrikler ve önceki döneme göre değişim (%).
- **Anomaliler** — Meta'nın işaretledikleri ve senin teşhisin.
- **Öneriler** — öncelik sırasıyla, her birinde beklenen etki ve hangi pipeline ile uygulanacağı (`butce-optimize`, `hedef-kitle`, `kampanya-kur`).

Sohbette yalnızca özeti ve dosya yolunu ver. Sayıları uydurma: bir metrik gelmediyse "veri yok" yaz.
