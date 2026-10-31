# Claude / Codex ile Meta Reklam Pipeline'ları

Meta'nın resmi **Ads MCP** sunucusunu Claude Code'a (veya Codex'e) bağlayıp reklam hesabını bir "reklam ekibi" gibi yöneten hazır yapılandırma: analiz, bütçe optimizasyonu, hedef kitle, kampanya kurulumu ve ölçüm kontrolü. Para harcayan her işlem onaya ve kod düzeyindeki bir güvenlik bariyerine bağlıdır.

```
┌──────────────┐   OAuth (Facebook)   ┌──────────────────────────────┐
│ Claude Code  │ ───────────────────▶ │ Meta Ads MCP                 │
│   / Codex    │ ◀─────────────────── │ https://mcp.facebook.com/ads │
└──────┬───────┘   29 araç            └──────────────────────────────┘
       │
       ├─ skills/  → 5 pipeline (adım adım iş akışı)
       ├─ agents/  → salt okunur analist alt ajanı
       └─ hooks    → scripts/guardrail.py  (bütçe sınırı, PAUSED zorunluluğu)
```

## Pipeline'lar

| Komut | Ne yapar | Hesapta değişiklik |
|---|---|---|
| `/reklam-analiz` | KPI trendleri, anomaliler, sektör kıyası → `reports/analiz-*.md` | Yok |
| `/olcum-saglik` | Piksel/CAPI olayları, eşleşme kalitesi, katalog hataları | Yok |
| `/butce-optimize` | Ölçekle / koru / kıs / durdur planı; ±%20 sınırlı, toplam harcama sabit | Onaydan sonra |
| `/hedef-kitle` | 3 kitle varyantı (geniş, ilgi alanı, sıcak/benzer) → PAUSED ad set | Onaydan sonra |
| `/kampanya-kur` | Brief → kampanya → ad set → reklam, hepsi PAUSED; yayına alma ayrı onayla | Onaydan sonra |

Doğal dille de tetiklenir: *"Son 7 günün reklamlarını analiz et"*, *"bütçeyi kazanan kampanyaya kaydır"*.

## Kurulum

**Gerekenler:** Claude Code (veya Codex CLI), Python 3.9+, Meta Business hesabında reklam yönetme yetkisi.

```bash
git clone https://github.com/<kullanici>/claude-meta-ads-pipelines.git
cd claude-meta-ads-pipelines
```

### Claude Code
```bash
claude
```
1. Proje `.mcp.json` dosyasındaki `meta-ads` sunucusunu onayla.
2. `/mcp` → `meta-ads` → **Authenticate**. Facebook girişi açılır; erişim verilecek reklam hesaplarını ve sayfaları seç.
3. `/reklam-analiz` ile başla.

> Claude.ai / masaüstü uygulamasında: Ayarlar → Connectors → *Add custom connector* → `https://mcp.facebook.com/ads`.

### Codex
```bash
codex mcp login meta_ads
codex
```
`.codex/config.toml` sunucuyu tanımlar, `AGENTS.md` Codex'i aynı pipeline dosyalarına yönlendirir.

## Güvenlik

- **İzinler** (`.claude/settings.json`): okuma araçları otomatik; `create`, `update`, `activate` araçları her seferinde onay ister.
- **Guardrail hook** (`scripts/guardrail.py`, ayarlar `guardrails.json`): Meta'ya gitmeden önce çağrıyı reddeder, eğer
  - günlük / toplam bütçe sınırı aşılıyorsa (tutarlar kuruş/cent cinsinden),
  - yeni kayıt `PAUSED` değilse,
  - `ads_update_entity` ile yayına alınmaya çalışılıyorsa,
  - `allowed_ad_account_ids` doluysa ve başka bir hesaba yazılıyorsa,
  - `block_activate: true` iken yayına alma deneniyorsa.
- İlk denemelerde Meta tarafında **salt okunur** yetki vermen ve Business Suite'te hesap harcama limiti tanımlaman önerilir. Erişimi Business Suite → Ayarlar → İş Entegrasyonları'ndan geri alabilirsin.

```json
{
  "max_daily_budget": 50000,        // 500,00 TL / gün
  "max_lifetime_budget": 1000000,   // 10.000,00 TL
  "require_paused_on_create": true,
  "block_activate": false,
  "allowed_ad_account_ids": []      // ör. ["act_1234567890"]
}
```

## Test
```bash
python -m unittest discover -s tests -v
```

## Notlar
- Meta Ads MCP Nisan 2026'da açık beta olarak çıktı; araç adları değişirse `.claude/settings.json` ve skill dosyalarını güncelle.
- Bu proje Meta ile bağlantılı değildir. Hesabında yapılan değişikliklerin sorumluluğu kullanıcıya aittir.

## Lisans
MIT
