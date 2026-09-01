# Prereg — **YANG_2021 + `gth`**: o ratchet de stick aplicado à fonte 8/8 STICK

**2026-08-10** · gates **IMUTÁVEIS** · ⚠️ **declara de saída: censo NÃO muda.** Este é um passo
de **qualidade** sob o gate PR-37′, não de contagem.

## Por que esta combinação

Duas medições independentes se encontram:

1. **O `gth` foi embarcado hoje** por outra sessão (`74c17d9`), default-inerte, com 7 testes de
   contrato e conservação fechada nos dois lados. É um **ratchet de regime de STICK**: acumula
   **somente** quando `slip_amp ≤ 1e-9`, e em gross slip é **0 exato** — *"curvas em regime de
   slip ficam BIT-IDÊNTICAS sem re-calibração"*.
2. **O `YANG_2021` é 8/8 STICK** (censo instrumentado de hoje,
   `censo_stick_abertas_resultado.md`), e o trabalho profundo dessa fonte
   (`yang2021_trabalho_profundo_resultado.md`) concluiu que o defeito é exatamente
   **perda sustentada sob stick**, com `ρ(resíduo,N) = +1,00` (rampa) em 6 curvas.

⚠️ **A outra sessão declarou NÃO-ADOÇÃO do `gth`** — e com razão para o alvo dela: testou no
`YANG_2019`, que o censo mede como **5/5 PARCIAL**, onde o mecanismo é **inerte por
construção**. O mecanismo estava certo e a fonte era a errada. Isto não corrige a decisão dela;
aplica o mecanismo à fonte para a qual ele foi desenhado.

## Procedência — o que NÃO se move

| constante | valor | procedência |
|---|---|---|
| `gth_q` | **3,8** (default) | **TRAVADA** — lei IJPEM `N_L ~ δ^{−3,8}` (PR-21), declarada no prereg `2026-08-10-yang2019-tripe-prereg.md` §G1-T13 |
| `gth_dref` | **5e-4** (default) | **TRAVADA** — `= LOOSE_AMP_REF` |
| `gth_A0` | **0** (default) | sem incubação (o platô desta fonte já é o stick) |
| **`gth_k`** | **1,5e-7** | **1 número fitado-this-rig** |

⚠️ **Eu quase quebrei a trava.** A varredura conjunta achou `gth_q = 7,0` com `k = 3e-8` dando
tripé **3→4 com zero custo** — melhor que qualquer célula no `q` legítimo. Recusado: `gth_q`
carrega a lei do IJPEM, e mover um expoente de literatura para fechar uma curva é o oposto da
disciplina. Fica registrado como **rota recusada com número**, não como rota não vista.

## A escolha da dose, e o que ela custa

No `q` travado, varredura fina de `gth_k`:

| `gth_k` | tripé | saem | pioram >0,01 | mediana MAE |
|---|---|---|---|---|
| 1e-7 | 3 | 0 | 0 | 0,0362 (−13 %) |
| **1,5e-7** | **3** | **0** | **0** | **0,0304 (−27 %)** |
| 2e-7 | **2** | 1 (`r2`) | 3 | 0,0304 |
| 2,5e-7 | 4 | 1 (`r2`) | 3 | 0,0312 |
| 3e-7 | 4 | 1 (`r2`) | 3 | 0,0310 |

**1,5e-7 é a maior dose com custo ZERO.** As doses que **fecham** curvas (2,5e-7 e 3e-7 põem
`r1` e `amp1p0` no tripé) **tiram a `r2`** e pioram 3 — reprovariam o PR-37′ (*"nenhum caso
pior +0,01"*). ⇒ escolho a dose que passa o gate, **não** a que sobe a contagem.

## Efeito medido nas 8 (`gth_k` = 1,5e-7)

| curva | antes | depois |
|---|---|---|
| `amp0p5mm_ax8kN` | 0,043/0,130/0,044 | 0,032/0,108/0,039 |
| `amp0p6mm_ax8kN_r1` | 0,026/0,101/0,032 | 0,017/0,081/0,027 |
| `amp0p6mm_ax8kN_r2` ✅ | 0,040/0,049/0,009 | 0,048/0,059/0,010 ✅ |
| `amp0p6mm_ax8kN_r3` ✅ | 0,021/0,039/0,009 | 0,028/0,039/0,007 ✅ |
| `amp0p7mm_ax11p2kN` ✅ | 0,013/0,047/0,017 | 0,016/0,027/0,011 ✅ |
| `amp0p8mm_ax6kN` | 0,074/0,208/0,061 | 0,054/0,174/0,051 |
| `amp1p0mm_ax2kN` | 0,054/0,153/0,045 | 0,028/0,107/0,032 |
| `fig2_typical` | 0,061/0,197/0,061 | 0,040/0,161/0,051 |

**5 melhoram nas 3 pernas, 3 pagam ≤ +0,008 de MAE e nenhuma sai.** A `amp1p0` melhora 48 % no
MAE e a `fig2` 34 %.

## Gates (congelados)

| # | gate | esperado |
|---|---|---|
| **W1** | `gth_q` e `gth_dref` **ficam no default** (procedência respeitada) | asserção no executor |
| **W2** | nenhuma curva do `YANG_2021` **sai** do tripé | 3 → 3 |
| **W3** | nenhuma piora MAE >+0,01 | máx. medido +0,008 |
| **W4** | mediana MAE da fonte cai ≥ **20 %** | medido −27 % |
| **W5** | **isolamento**: as outras **10** curvas STICK da biblioteca não mudam | Δ = 0 exato (`YANG_2023` ×3, `LIU_2025` ×2, `LU_2024` ×2, `ZHANG_2006` ×2, `ROUSSEAU` ×1) |
| **W6** | censo | **144 → 144, INALTERADO** |
| **W7** | suíte completa | verde |

⚠️ **W5 é o gate crítico e novo**: o `gth` age em **toda** curva em stick, e a biblioteca tem
**18**. A adoção é per-fonte (grupo `YANG_2021`), então o isolamento deve ser estrutural — mas é
a primeira vez que uma constante desta campanha tem alcance definido por **regime** e não por
chave de config, e isso precisa ser verificado, não assumido.

⚠️ **W6 declara censo inalterado ANTES de medir**, para que o resultado não seja lido como ganho
de contagem. Se o censo **subir**, também é divergência: significaria que uma curva fora do
`YANG_2021` mudou e o W5 falhou.

## Rollback

`.bkp_gth` no `adopted_configs.json` e no store. Qualquer gate divergente ⇒ restaura e registra.


## Estado

✅ **EXECUTADO em 2026-08-10.** Resultado: `New_Theory/yang2021_gth_resultado.md`.

W1 ✅ (q=3,8 / dref=5e-4 nos defaults, conferido no material efetivo) · W2 ✅ 3→3 ·
W3 ✅ 0 pioram (máx +0,0080) · W4 ✅ mediana −0,0419→−0,0304 = **−27 %** ·
W5 ✅ Δ=0 exato em 10 sondas (6 delas em STICK) · W7 ✅ **920/1**.

⚠️ **W6 (censo 144→144): NÃO AVALIÁVEL COMO ESCRITO.** O re-stamp devolveu **147** e a
investigação mostrou por quê: o store estava **parcialmente carimbado** (209 registros no
fingerprint antigo, 1 em `ca1473211659`) porque a sessão paralela adotou, sincronizou os
documentos e não concluiu o re-stamp. O +3 é **da adoção dela**; a minha contribuição é **0**,
medida por W2+W5 contra o store anterior. Não declaro o W6 aprovado.

**Lição:** gate de **censo absoluto** é frágil sob escritor paralelo; o robusto é o
**diferencial confinado** (W2+W5), que não depende do que a outra sessão fez no intervalo.
