# Meta Ads Pipelines — Codex talimatları

Bu depo hem Claude Code hem Codex ile çalışır. Codex'te Meta MCP sunucusu `.codex/config.toml` içinde `meta_ads` adıyla tanımlıdır.

Kullanıcı aşağıdaki işlerden birini istediğinde ilgili dosyayı oku ve adımlarını harfiyen uygula:

| İstek | Dosya |
|---|---|
| Reklam analizi, rapor, "nasıl gidiyor" | `.claude/skills/reklam-analiz/SKILL.md` |
| Bütçe optimizasyonu | `.claude/skills/butce-optimize/SKILL.md` |
| Hedef kitle | `.claude/skills/hedef-kitle/SKILL.md` |
| Kampanya kurulumu | `.claude/skills/kampanya-kur/SKILL.md` |
| Piksel / CAPI / katalog kontrolü | `.claude/skills/olcum-saglik/SKILL.md` |

Kurallar `CLAUDE.md` içindeki "Değişmez kurallar" bölümüyle aynıdır ve Codex için de geçerlidir. Codex'te guardrail hook'u otomatik çalışmaz: her yazma çağrısından önce `guardrails.json` sınırlarını kendin kontrol et; şüphedeyken araç girdisini şu komutla doğrula:

```
echo '{"tool_name":"ads_create_campaign","tool_input":{...}}' | python scripts/guardrail.py
```

Çıktı boşsa geçer; `"deny"` içeriyorsa çağrıyı yapma.
