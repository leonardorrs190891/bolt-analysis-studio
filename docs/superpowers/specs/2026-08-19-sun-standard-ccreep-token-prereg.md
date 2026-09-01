# PREREG — `sun…grease_standard`: estender o `C_creep` per-token `standard` (ZERO número novo)

**2026-08-19 (17:0x)** · **gates congelados neste commit** · store
`76a39eb7e17b`, censo 144/205 · continuação direta do mandato *"trabalhe mais
em …grease_standard.html"*, sobre o kernel adotado em `7adaca7`/`bfaf773`.

## 1. O resíduo pós-kernel, e onde a rota apareceu

Após o kernel cinemático, sobrou um **arco único**: modelo 23 % lento no 1º
terço, 53 % rápido no último (pico +0,110 em N≈150). O shell canônico mostrou
`C_creep` como a única alavanca livre com dose fisicamente sã que move o arco —
e a extensão da varredura encontrou que **9e-11 fecha as três pernas**
(0,0191 / 0,0431 / 0,0223).

## 2. Por que 9e-11 NÃO é um número novo — e por que a crimp o rejeita é parte da prova

O per_case vigente do `SUN_2025_CRIMP` já carrega o padrão:

| token | C_creep |
|---|---|
| `axial_f7.5kn_standard` | **9e-11** |
| `axial_f17.5kn_standard` | **9e-11** |
| axiais **crimp** | (herdam o shared 1,867e-11) |
| transversais | (herdavam o shared) |

A proposta é **estender o valor do token `standard` ao terceiro membro
standard** (a transversal greased). E a medição de coerência foi feita ANTES
deste prereg, com o resultado que o padrão prediz: a **greased crimp REJEITA**
o 9e-11 (0,0221→0,0628, piora 3×) — consistente com os axiais crimp, que nunca
o receberam. O conector crimpado é outra junta; a fonte já a trata assim.

⚠️ **Ressalva de procedência, herdada e declarada:** o 9e-11 dos axiais tem
prov *"fitado-this-rig PER-TOKEN — PROXY do canal axial ausente (L1)"*. A
extensão herda esse estatuto (proxy, não âncora); o que este passo NÃO faz é
criar número novo nem re-fitar o kernel (k_graded fica no 0,020 adotado).

⚠️ **Escopo do token, dito com precisão:** a `nogrease_standard` (SECA, no
tripé com trim) **não** recebe — C_creep é por PAR TRIBOLÓGICO (§4.7) e o par
seco é outro. A gravação usa o token `_grease_standard` existente (o underscore
não casa `nogrease`).

## 3. A grade que sustenta (medida antes, D-Z: kernel × creep juntos)

| k_graded | C_creep | pior perna |
|---:|---:|---:|
| 0,020 (adotado) | 1,87e-11 (shared) | 1,62× |
| 0,020 | 7e-11 | 1,02× |
| **0,020** | **9e-11 (token)** | **0,89× FECHA** |
| 0,020 | 1,2e-10 | 0,82× FECHA |
| 0,017 | 9e-11 | 0,94× FECHA |

Região de 4 células fechando — não é navalha. A célula adotada **não é
escolhida pela grade**: é fixada pelo token (9e-11) e pelo k já adotado
(0,020). A grade só demonstra vizinhança.

## 4. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | **alvo fecha o tripé** | 0,0191 / 0,0431 / 0,0223 reproduzidos ao dígito pelo caminho canônico (MAE ≤0,05 · mx ≤0,10 · σ ≤0,025) |
| **G2** | **as 7 irmãs bit-idênticas** | incluindo a crimp (não recebe) e a nogrease_standard (par seco, não recebe) |
| **G3** | **isolamento** | Δ=0 fora do SUN no re-stamp |
| **G4** | **re-stamp íntegro** | fingerprint novo uniforme nos 210 (com o gotcha do sintético) |
| **G5** | **censo** | **144 → 145** (a curva FECHA; nenhuma outra muda) |
| **G6** | **catraca de estatuto** | se a curva fechar, a forma nomeada da triagem é atualizada (a curva sai das 21 abertas); docs vivos sincronizados; aging verde |

## 5. Predições registradas

1. G1 ao dígito (mesmo caminho da sonda).
2. Censo **145/205** — a primeira curva a FECHAR por trabalho de modelo desde o
   pico espúrio (que era dado). Abertas 21 → 20.
3. A crimp segue aberta a 1,21× (intocada) e vira a única aberta do SUN.
4. σ da curva: 0,0223 (0,89×) — margem de 11 %, não raspando.


## Estado

EXECUTADO 2026-08-19 (17:1x): a curva FECHOU o tripe (0,0191/0,0431/0,0223); censo 144->145 confirmado no re-stamp e6b18851a6af. Resultado no sec6 de sun_standard_kernel_cinematico_resultado.md.
