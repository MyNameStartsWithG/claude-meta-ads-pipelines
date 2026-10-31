# Meta Ads Pipelines

Bu depo, Meta'nın resmi Ads MCP sunucusu (`meta-ads`, https://mcp.facebook.com/ads) üzerinden reklam hesabını yöneten pipeline'ları içerir. Kullanıcıyla Türkçe konuş.

## Pipeline'lar (`.claude/skills/`)
| Skill | İş | Yazar mı? |
|---|---|---|
| `reklam-analiz` | Performans denetimi ve rapor | Hayır |
| `olcum-saglik` | Piksel/CAPI ve katalog sağlığı | Hayır |
| `butce-optimize` | Bütçe yeniden dağıtımı | Onayla |
| `hedef-kitle` | Kitle tasarımı ve ad set | Onayla |
| `kampanya-kur` | Kampanya → ad set → reklam | Onayla |

Salt okunur, paralel inceleme için `reklam-analisti` alt ajanını kullan.

## Değişmez kurallar
1. Gerçek para harcanır. Her yazma işleminden önce ne yapılacağını tablo halinde göster ve açık onay al.
2. Yeni kampanya/ad set/reklam her zaman `status: PAUSED` kurulur. Yayına alma yalnızca `ads_activate_entity` ile ve ayrı bir onayla.
3. Bütçeler hesabın para biriminin en küçük biriminde (kuruş/cent) gönderilir; göndermeden önce birimi kullanıcıya TL/USD olarak doğrula.
4. `scripts/guardrail.py` hook'u `guardrails.json` sınırlarını uygular. Bir çağrı reddedilirse sınırı dolanmaya çalışma; nedeni kullanıcıya söyle.
5. Sayı uydurma. Araçtan gelmeyen veri "veri yok"tur.
6. Raporlar `reports/` altına yazılır (git'e girmez).

## Geliştirme
Guardrail testleri: `python -m unittest discover -s tests`
