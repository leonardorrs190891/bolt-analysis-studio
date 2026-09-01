# Auditoria de COBERTURA DE PROCEDÊNCIA: **44 % das constantes adotadas não têm nenhuma**

> # ⚠️ ERRATA DE 2026-08-13 — o número publicado estava **inflado em 32**
>
> **Era 238 (51 %). É 206 (44 %).** A cobertura sobe de 49 % para **56 %**.
>
> **Causa:** minha sonda testava `prov.get(campo)` — lookup **exato** —, e a campanha grava
> chaves **COMPOSTAS** quando um único argumento cobre várias constantes. Exemplo que
> destravou o achado: `ROUSSEAU_HDPE` tem `prov['c_bend/emb_depth/floor'] = "PR-14
> fitado-this-rig (rig + assentamento + piso de arresto)"` — **três** constantes
> documentadas numa entrada só, e a minha varredura contava as três como indocumentadas.
>
> Re-medido com casamento por **token** da chave composta (split em `/` e `,`, mais um mapa
> de alias curto: `floor`→`loose_arrest_floor`, `emb`→`emb_depth`, `mu`→`mu_thread`/
> `mu_bearing`, `creep`→`C_creep`/`t_0`, `dano`→os 4 de dano). Token é mais estrito que
> substring **de propósito**.
>
> | | publicado (08-12) | **corrigido (08-13)** |
> |---|---:|---:|
> | com procedência | 229 (49 %) | **261 (56 %)** |
> | **sem** procedência | 238 (51 %) | **206 (44 %)** |
>
> **Recuperadas por chave composta (32):** `mu_thread` 9 · `mu_bearing` 8 · `t_0` 5 ·
> `creep_conform_exp` 2 · `p_ref_emb` 2 · `delta_free`, `c_bend`, `emb_depth`,
> `loose_arrest_floor`, `loose_rate_mode`, `C_creep` 1 cada.
>
> **A consequência mais cara não foi o número, foi a decisão que ele gerou:** o
> `ROUSSEAU_HDPE::loose_arrest_floor` foi levado ao professor como *"constante fitada em
> silêncio, `prov = None`"* — e a procedência existia desde 2026-07-12. Errata completa em
> `rousseau_piso_arresto_lacuna_resultado.md`.
>
> ⚠️ **A tese qualitativa da auditoria sobrevive**: 206 constantes seguem sem registro,
> `c_bend` (16) e `loose_arrest_floor` (12) continuam os dois campos mais indocumentados, e
> o `CHU_2026` segue em **100 % sem procedência**. O que muda é a magnitude e uma das três
> anedotas que motivaram a varredura.
>
> Baseline e lookup corrigidos em `tests/test_procedencia_catraca.py` (206 pares, 4 testes).
> O texto original segue abaixo, **intacto**, como registro.

**2026-08-12** · só-leitura · **nada adotado** · store `bd74eaf0b11d`, censo **147/205**.

## Por que esta auditoria

Em três dias consecutivos, três achados independentes tiveram a **mesma forma**:

| dia | constante | situação |
|---|---|---|
| 08-10 | `CHU_2026` — rugosidade | input do paper contradiz o registrado; corrigir **piora** |
| 08-10 | `gth_q` = 7,0 | fecharia uma curva com custo zero; **recusei** por quebrar a lei do IJPEM |
| 08-11 | `ROUSSEAU_HDPE` — `loose_arrest_floor` = 0,2 | **`prov = None`**; a métrica depende 2,2× dele |

⇒ *onde a procedência não cobre, um ajuste entrou e a métrica passou a depender dele.* Isso é
uma hipótese sobre a **população**, e a campanha inteira se apoia na premissa oposta —
"physics first, procedência por constante". Nunca foi medida.

## O número

Varri **todos** os grupos de `adopted_configs.json`, contando cada constante do `cfg` e
verificando se há entrada correspondente no `prov` (excluídos os campos que não são
constante: `per_case`, `trim_n_max`, `chain`, `pack`, espectros e geometrias).

> ## **467 constantes adotadas · 229 (49 %) com procedência · 238 (51 %) SEM**

Das 238 sem procedência:

| categoria | n | leitura |
|---|---:|---|
| **campo válido de `JointMaterial`** | **202** | **chegam ao engine e carregam peso métrico, sem justificativa registrada** |
| input do runner (`emb_um`, `emb`, `mu`) | 19 | procedência pode viver na tabela VDI / nota de aparato |
| legado ou não-engine declarado | 17 | ver a correção abaixo |

### Por campo — os mais frequentes sem procedência

`c_bend` **17** · `loose_arrest_floor` **13** · `mu_thread` 12 · `W_ref` 12 ·
`k_wear_scale_tr` 11 · `mu_bearing` 10 · `emb_um` 9 · `emb_depth` 9 · `k_dmg_mu` 9 ·
`c_D` 8 · `k_dmg_wear` 7 · `C_creep` 7 · `slip_regime_mode` 7

⚠️ **`loose_arrest_floor` é o 2º campo mais indocumentado** — e foi exatamente ele que a
investigação de ontem pegou por acaso no `ROUSSEAU`. O achado não era isolado: era **uma
amostra de 13**.

### Por fonte

| fonte | com | sem | % sem |
|---|---:|---:|---:|
| **`CHU_2026`** | 0 | 7 | **100 %** |
| `LIU_2025` | 7 | 52 | 88 % |
| `UFU_LAB` | 3 | 21 | 88 % |
| `BAUER_2024` | 12 | 30 | 71 % |
| `LIU_2022` | 24 | 44 | 65 % |
| `YANG_2019` | 10 | 14 | 58 % |
| `CACCESE_2009` | 12 | 12 | 50 % |
| `JCSR_2023` · `LI_2022` | 17 | 2 | **11 %** |

O `CHU_2026` — a fonte que anteontem eu re-diagnostiquei como *"não-calibrada por condição"* —
tem **100 % das suas constantes sem procedência**. As duas leituras se confirmam.

## ⚠️ Correção de um alarme meu, no mesmo dia

Primeiro classifiquei **17 entradas como ÓRFÃS** (nem campo do engine nem input) e escrevi que
seriam *"ruído puro: não chegam ao engine"*. **Errado nos dois casos:**

* `k_wear_scale_tr` (×11) — o **`tuner_shim` conhece**: `k_wear_scale_tr → k_wear_spec *= v`
  (senão `K_archard *= v`), e o **runner chama o shim** (linha 172 de `runner.py`). Prova: o
  `LIU_2025` traz `k_wear_scale_tr = 0,0` e o material sai com `k_wear_spec = 0` — o tuner é
  **exatamente o que zera o canal de wear** naquela fonte.
* `c_D_dry`, `c_D_oil`, `c_D_per_lube` (×6) — estão em `knowledge_base._NON_ENGINE`,
  **declaradas** como chaves não-engine.

⇒ **zero órfãos de verdade.** A config é estruturalmente limpa; o problema é de **documentação**,
não de lixo.

⚠️ E o caminho do erro merece registro: meu primeiro teste injetou `k_wear_scale_tr` por
`_effective_overrides` e deu **bit-idêntico**, o que eu quase li como "morto". Era **teste
inválido** — o shim roda **dentro** de `_effective_overrides`, sobre o `cfg`, e a minha injeção
acontecia **depois**. O teste válido mexe na **config** (cópia isolada via
`BAS_ADOPTED_CONFIGS`). Sexta vez neste mês que "Δ = 0" era instrumento no caminho errado.

## O que isto significa — e o que NÃO significa

**Não significa** que as 202 constantes estejam erradas. Significa que **não há registro de
onde vieram**, e portanto:

* não dá para saber se são `fitado-this-rig` (legítimo, é a maioria da campanha) ou input de
  paper mal-copiado (como a rugosidade do CHU acabou sendo);
* qualquer auditoria futura terá de **re-derivar** cada uma, e é isso que torna o passivo caro;
* a leitura publicada *"physics first, procedência por constante"* descreve **49 %** do que está
  adotado, não o todo.

**Não é acusação de má prática:** a campanha cresceu por adoções incrementais sob gates de
métrica, e `prov` nunca foi **obrigatório**. É exatamente por isso que o passivo acumulou em
silêncio — nenhum gate o media.

## A proposta (decisão do professor)

1. **Gate de procedência nas adoções NOVAS** — nenhuma constante entra em `cfg` sem entrada
   correspondente em `prov`. Custo ~0, impede o passivo de crescer, e é um teste de 5 linhas
   (`test_prov_obrigatoria`) sobre o mesmo `adopted_configs.json`.
2. **Backfill priorizado** pelas 2 fontes de maior peso e menor cobertura (`LIU_2025` 52 sem,
   `LIU_2022` 44 sem) ou pelos 2 campos mais frequentes (`c_bend` 17, `loose_arrest_floor` 13) —
   a segunda opção é mais barata porque o argumento é o mesmo dentro do campo.
3. **Declarar o passivo** no `MODEL_LEGITIMACY.md` com o número, sem backfill — honestidade sem
   custo de trabalho.

A (1) é a única que impede o crescimento; as outras duas atacam o estoque.

## Reprodutibilidade

Sonda no scratchpad: percorre `adopted_configs.json['sources']`, cruza `cfg` × `prov`, e
classifica cada chave contra `JointMaterial.__dataclass_fields__`,
`knowledge_base._NON_ENGINE` e o mapa do `tuner_shim`. Saída em `prov_faltante.json`
(238 entradas). Segundos.

---

## FASE 1 DO BACKFILL EXECUTADA (2026-08-13, item A assinado) — 206 → 162

Os 3 maiores campos, como assinado: **c_bend 16 · W_ref 12 · loose_arrest_floor
12 = 40 constantes**, mais 4 de bônus por chave composta (CHU `c_D/W_ref/
k_dmg_mu`; YANG `c_D/W_ref/k_dmg_wear` — um argumento, três campos). Método:
**arqueologia de commit por grupo** (`git log -S` no valor), não redação
genérica — cada prov cita o commit adotante:

| classe | grupos | argumento |
|---|---|---|
| PR-22 (097dd7e) | BAUER fig6 ×7 | c_bend/floor fitados per-espécime coerente |
| PR-38 re-key | CHU test1 | âncora D_cr + trio fitado no µ(N) do test2 (já narrado em `leituras`; agora keyado por campo) |
| PR-40/D-Z | KARLSEN ×2 | c_bend per-rig |
| PR-18 (01eeb76) | UFU ×3 | c_bend per-specimen; floor = default do pack explicitado |
| F3 LOTE2 (f77d3af) | ZHANG_2006 | fitado-this-rig |
| Herança E2 (d721b14) | LIU_2025 amp0p4/0p5 | cfg copiado do pai na cisão; argumento vive no prov do pai |
| Starter físico | KARLSEN/UFU/LIU_2022 ×10 | W_ref=1e4 = escala de referência 2026-06-20, não fitada |
| ADOTA 6e19494 | YANG_2019 | trio de dano v2 varamp, dossiê T1–T13 |

**Atual: 162 sem procedência** (baseline congelado do teste segue 206 por
design — a catraca mede contra o snapshot; o progresso é `atual`, não o
baseline). ⚠️ prov entra no fingerprint ⇒ esta fase embarcou com **re-stamp
completo do store + auditoria de deriva zero** no mesmo commit.
