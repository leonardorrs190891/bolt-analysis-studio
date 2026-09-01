# Prereg — **backfill de PROCEDÊNCIA por campo** (item A da fila, ASSINADO)

**2026-08-13** · executor: sessão do cron · gates **IMUTÁVEIS** depois desta linha.

## Estado

⛔ **ADIADO em 2026-08-13 por COLISÃO DE ESCRITOR — não executado, e a razão importa.**

O backfill foi escrito (38 entradas, gate P4 verificado: **0 grupos com `cfg` alterado**) e o
re-stamp dos 205 chegou a iniciar. **Interrompido e revertido** ao descobrir que a sessão
paralela está numa campanha **ativa** no `CHU_2026` — 5 commits no mesmo dia
(`48c1787` prereg → `64e1bed` rodada 1 → `775ca09` paper lido → `74f3a1a`/`a513f2f` rodada 2
falsificada, rodada 3 declarada).

**Por que isso barra este trabalho, embora ele não toque `cfg`:** `engine_fingerprint()`
hasheia `prov`. Re-stampar mudaria o fingerprint dos 205 registros **debaixo** de uma
campanha em curso, e os gates dela comparam contra o store. As métricas seriam
bit-idênticas — a física não muda —, mas o **fingerprint esperado** não, e isso reprova gate
por instrumento, não por mérito. É a armadilha que o `CLAUDE.md` já nomeia: *"toda edição de
metadado do `adopted_configs.json` embarca no próximo re-stamp"*.

Regra da casa aplicada: **diagnóstico em paralelo, adoção em série** — e quem estava no
recurso primeiro eram eles.

**Estado restaurado e verificado:** `adopted_configs.json` limpo (HEAD), store limpo com
fingerprint uniforme `bd74eaf0b11d` em 210 registros, `git status` sem resíduo. O batch
escreve o store só no fim, então a interrupção não deixou escrita parcial.

**Trabalho preservado:** o JSON com as 38 `prov` está em
`$CLAUDE_JOB_DIR/tmp/adopted_com_prov38.json`, e o executor em `backfill_prov.py`. Ele é
**idempotente e verificado por valor** (só escreve onde o valor bate com o *starter*), então
re-aplicar depois da campanha CHU é re-rodar o script — **de preferência embarcando no
re-stamp da adoção CHU**, que já vai acontecer de qualquer modo. Custo marginal: zero.

⚠️ **Erro meu no caminho, registrado:** o backup do store usou o caminho errado
(`New_Theory/validation_store.json`; o real é
`Models/CALIBRATION_AND_VALIDATION/validation_store.json`) e o `2>/dev/null` **engoliu o
erro**. Só não houve dano porque o batch ainda não havia escrito. O `cp` silencioso é a
mesma classe de defeito que o `CLAUDE.md` documenta para `git add` e para `cmd | tail`:
**silenciar stderr de um passo de segurança transforma proteção em teatro.**

## Contexto: o passivo é REAL, mas era menor do que eu publiquei

A auditoria de 08-12 publicou *"238 de 467 constantes (51 %) sem `prov`"*. **Corrigido hoje
para 206 (44 %)**: o lookup era `prov.get(campo)` **exato**, e a campanha grava chaves
**COMPOSTAS** quando um único argumento cobre várias constantes
(`'c_bend/emb_depth/floor'` no `ROUSSEAU_HDPE`). Errata nos 3 documentos + pino de regressão
em `test_procedencia_catraca.py`. **O item C da fila morreu junto** — a procedência que ele
dizia faltar existia desde 2026-07-12.

Este prereg ataca o estoque **restante e real**, por CAMPO, como o professor assinou.

## ⚠️ A regra que governa este trabalho: documentar ≠ inventar

Só escrevo `prov` onde a origem é **rastreável a um registro existente**. Onde não for, a
constante **fica no baseline da catraca**, com comentário — porque "sem procedência
declarada" é informação, e um rótulo inventado a **destrói**.

## O que SERÁ documentado (origem rastreável, medida hoje)

| classe | campo · valor | n | origem citável |
|---|---|---:|---|
| *starters* de dano | `k_dmg_wear` = **4,0** | 7 | `CLAUDE.md`: *"Damage physical starters: c_D=2, k_dmg_mu=1, k_dmg_wear=4, W_ref=1e4"* (design surface_damage, 2026-06-20) |
| *starters* de dano | `W_ref` = **1e4** | 11 | idem |
| *starters* de dano | `k_dmg_mu` = **1,0** | 8 | idem |
| canal desligado | `slip_regime_mode` = **`'off'`** | 7 | não é constante fitada: desliga o canal (valor = o próprio default semântico) |
| default de pack | `loose_arrest_floor` = **0,08** | 3 | default documentado do pack (registrado em `rousseau_piso_arresto_lacuna_resultado.md`) |
| herança de grupo-pai | `c_bend` = **50,0** (`LIU_2025_amp0p4/amp0p5`) | 2 | o grupo-pai `LIU_2025` traz `prov` = *"fixture L de alta rigidez (servo; classe PESADA PR-4, k_tr ~3,6e8)"*; os subgrupos-token herdam o mesmo valor |

**Total previsto: 38 constantes** ⇒ baseline da catraca **206 → 168** (esperado).

Cada `prov` escrita nomeia a origem E o fato de ser origem-de-classe, não medição
per-rig — p.ex. `"starter físico do design de surface_damage (2026-06-20); NÃO fitado nesta
fonte"`. Isso é mais informativo que o silêncio atual e mais honesto que `fitado-this-rig`.

## O que NÃO será documentado — e fica FLAGRADO

| grupo | campo | valor | por que fica |
|---|---|---:|---|
| ~~`CHU_2026_test1`~~ | ~~`k_dmg_mu`~~ | **−2,43** | ✅ **PROCEDÊNCIA ENCONTRADA — não é fit cego.** `MODEL_LEGITIMACY.md:3530`: *"`test1` (limiar) tem adoção (PR-38, `k_dmg_mu=−2,43` — **µ subindo, o sinal da Fig. 5**)"*. O negativo é **lido do artigo**: no rig do CHU o atrito medido **sobe** com a ciclagem, e `mu_eff = mu·(1−k_dmg_mu·D)` representa isso com sinal invertido. **Confirmado de forma independente** pela sessão paralela no mesmo dia (`775ca09`: *"mu_plate 0,2 SOBE com desgaste (k_dmg_mu negativo por par)"*) |
| `CHU_2026_test1` | `c_D` | 5,5 | mesmo PR-38; a **taxa** de crescimento do dano não tem a mesma âncora que o sinal |
| `YANG_2019` | `W_ref` | 3000 | único fora do starter; `verdict` só diz *"sec4.21 — 5Hz fecha"* |
| `LU_2024` | `emb_um` | 0,0 | assentamento zerado sem registro do porquê |

Estes **permanecem no baseline** com comentário nomeando a suspeita. Documentá-los exige
medir ou ler o PR original — trabalho separado, não este.

⚠️ **O `k_dmg_mu = −2,43` mudou de classe durante a redação deste prereg, e isso é o
resultado mais instrutivo do dia.** Eu o flaguei como *"fitado, sinal invertido, sem
registro"* — a leitura natural de um outlier num campo cujos outros 8 valores são `1,0`
exato. Bastou procurar por `PR-38` para achar a âncora física, **numa seção do
`MODEL_LEGITIMACY` que eu mesmo mantenho**. ⇒ *"sem `prov`"* significa **"não indexado onde
a auditoria olha"**, não **"sem origem"**; e o passivo real é menor que 206 pelo mesmo
motivo que já era menor que 238. O backfill honesto é, em boa parte, **transcrição** — o que
o torna mais barato e menos arriscado do que eu supunha, e reforça que a rota certa é ler o
registro antes de escrever, nunca inferir do valor.

## Gates (congelados)

| # | gate | esperado |
|---|---|---|
| **P1** | **as 205 métricas bit-idênticas** após re-stamp (MAE, res.máx, σ_res) | **Δ = 0 exato em todas** — `prov` não pode tocar física |
| **P2** | censo | **147/205, inalterado** |
| **P3** | fingerprint muda (é esperado: o hash cobre `prov`) e o store fica **uniforme** no novo valor | 205/205 iguais |
| **P4** | `cfg` intocado | **zero** chaves de `cfg` adicionadas/removidas/alteradas em qualquer grupo |
| **P5** | catraca | baseline encolhe p/ **168**; **zero** pares novos |
| **P6** | suíte completa | verde |

⚠️ **P1 e P4 são o par decisivo.** Se qualquer métrica mover, a edição vazou para a física e
o trabalho é revertido inteiro — não "investigado".

## Rollback

`.bkp_prov` em `adopted_configs.json` e no store. Qualquer gate divergente ⇒ restaura.

## Por que isto vale o custo do re-stamp (~25–40 min)

Porque `engine_fingerprint()` hasheia `prov`, e o `CLAUDE.md` registra que *"toda edição de
metadado do `adopted_configs.json` embarca no próximo re-stamp, nunca solta"*. Fazer o
re-stamp AGORA, com `cfg` intocado, é o cenário mais barato possível de verificar: o gate P1
é uma igualdade exata. Deixar a `prov` para embarcar numa adoção futura misturaria uma
mudança inócua com uma mudança real, e nenhuma das duas seria auditável em separado.
