# ROUSSEAU HDPE vive **entre os dois atratores** — a mesma forma faltante do SUN, agora com 2 fontes

**2026-08-07** · só-leitura · **nada adotado**.

## O caminho até aqui

Com a fila form-limited em zero e as quatro assinaturas executadas, o maior
grupo sem rota passou a ser as **8 indecidíveis** (fonte sem piso ⇒ prova F7
impossível): **4 do ROUSSEAU** e **4 do YANG_2023_IJPEM**. As do ROUSSEAU são as
mais próximas de todas.

Anatomia das quatro — e o padrão é inequívoco:

| curva | MAE × | mx × | σ × | viés | \|viés\|/MAE | rotacional |
|---|---:|---:|---:|---:|---:|---:|
| `steel_t10` | 3,10 | 2,70 | 3,98 | **+0,1548** | **1,00** | **83 %** |
| `steel_t10_amp0p2` | 1,91 | 1,55 | 1,65 | +0,0957 | **1,00** | 72 % |
| `hdpe_t10` | 1,85 | 1,79 | 2,76 | +0,0834 | 0,90 | 72 % |
| `hdpe_t12` | 1,13 | 1,13 | 1,82 | +0,0521 | 0,92 | 72 % |

Viés **positivo** (o modelo **retém demais**), erro de **nível quase puro**
(`|viés|/MAE` 0,90–1,00) e o **canal rotacional carregando 72–83 %**. É a
assinatura **idêntica** à da `karlsen_run14p2`, que o D-Z fechou horas antes com
`k_ratchet`. E o contraste confirma: as duas que **passam** com viés
**negativo** são as espessas (`t14`), que entram em *stick* permanente.

## A hipótese que eu tinha, e por que era boa

O grupo **HDPE** carrega `loose_arrest_floor = 0,2`; o grupo **aço** carrega
**0,0**. O aço foi a zero na recuperação de 2026-08-01 por **procedência de
aparato**: *"o rig apoia o membro móvel em roletes que removem o atrito
parasita ⇒ não há auto-travamento"*.

**Mas é o mesmo rig.** Os roletes não sabem de que material é o membro. Logo o
0,2 do HDPE parecia resíduo de herança do *pack*, e corrigi-lo seria **zero
número novo** com o argumento já aceito no grupo irmão.

## ⛔ FALSIFICADA — e na direção oposta

| curva | nominal (floor 0,2) | floor 0,0 |
|---|---|---|
| `hdpe_t10` | 0,0927 / 0,1786 / 0,0691 | **0,1550 / 0,3999 / 0,1782** |
| `hdpe_t12` | 0,0566 / 0,1133 / 0,0456 | **0,1023 / 0,3903 / 0,1490** |
| `hdpe_t10_amp0p2` | 0,0260 / 0,0728 / 0,0237 | 0,0258 / 0,0720 / 0,0234 |
| `hdpe_t14` | 0,0413 / 0,0636 / 0,0211 | 0,0413 / 0,0636 / 0,0210 |

Tripé da fonte: **4 → 4**. O viés era **positivo**, então afrouxar mais deveria
**ajudar** — e piora pela metade. As duas insensíveis são justamente as de baixa
amplitude e alta espessura, onde o floor **não morde**.

## A varredura que fecha o caso

| `loose_arrest_floor` | `hdpe_t10` | `hdpe_t12` |
|---|---|---|
| 0,00 | 0,1550 / 0,3999 / 0,1782 | 0,1023 / 0,3903 / 0,1490 |
| 0,10 | 0,1044 / 0,2317 / 0,1197 | 0,0635 / 0,2318 / 0,0908 |
| **0,15** | **0,0906** / **0,1669** / 0,0919 | **0,0542** / 0,1182 / 0,0600 |
| 0,20 (nominal) | 0,0927 / 0,1786 / 0,0691 | 0,0566 / **0,1133** / 0,0456 |
| **0,25** | 0,1173 / 0,1973 / **0,0575** | 0,0782 / 0,1359 / **0,0501** |
| 0,40 | 0,1942 / 0,2711 / 0,0802 | 0,1306 / 0,2391 / 0,0881 |

**Nenhum valor em [0; 0,40] fecha.** E o diagnóstico está na estrutura, não no
melhor valor: **as pernas têm ótimos em floors DIFERENTES** — MAE e res.máx
querem **0,15**, o σ quer **0,25**. Nenhum valor único satisfaz as três, e o
melhor de cada perna ainda erra (MAE **1,81×**, σ **2,30×**).

⚠️ **Ótimos conflitantes entre pernas é assinatura de defeito de FORMA, não de
nível.** O nominal 0,20 já está praticamente no ótimo de MAE — não há calibração
a extrair daqui.

## O que isto identifica: a MESMA forma faltante do SUN, com 2 fontes

`sun_crimp_resultado.md` (2026-08-06) mediu exatamente isto na
`sun2025efa109235_transverse_grease_crimp`:

> *"Com floor = 0 o modelo **bifurca**: ganho ≤1,0 → final 0,65–0,70; ganho ≥1,5
> → final **0,0000 exato**. … é o 'bifurcação arrest/zero, sem meio' que o
> `CLAUDE.md` já registra — aqui medido contra uma curva que vive **exatamente
> no meio**. **O engine não tem modo de afrouxamento de taxa fracionária
> constante.**"*

⇒ o ROUSSEAU HDPE é a **segunda fonte independente** com a mesma assinatura, em
outro rig, outro material de membro e outra escala de amplitude. Uma forma
faltante confirmada em duas fontes é qualitativamente diferente de uma
diagnosticada em uma.

E há um corolário desconfortável: o `loose_arrest_floor = 0,2` do HDPE **não
modela o rig** — ele **compensa a forma que falta**. Por isso o argumento de
aparato, que é fisicamente correto, piora a métrica: remover a compensação
expõe o buraco.

## PROPOSTA (P-13) — a segunda forma faltante, agora com 2 fontes

Registrar como candidato de **forma** (não de calibração) o **modo de
afrouxamento de taxa fracionária constante** — o regime intermediário entre
arresto no piso e *runaway* a zero:

* **Fontes que o exigem:** `SUN_2025_CRIMP` (τ = 172,7 ciclos, **R² = 0,9961**
  em `ln(F/F₀)` vs N) e **`ROUSSEAU_2025` HDPE** (ótimos de perna conflitantes,
  nenhum floor fecha).
* **Alcance medido:** 2 curvas do ROUSSEAU (`hdpe_t10`, `hdpe_t12`) + as do SUN
  já diagnosticadas. As `steel_t10`/`steel_t10_amp0p2` têm a mesma assinatura de
  viés mas já rodam com floor 0 — precisam de medição própria.
* **Distinta da P-9:** a P-9 é **frequência nos relógios de Estágio I** (defeito
  de *quando*); esta é **taxa fracionária constante no canal rotacional**
  (defeito de *como*). As duas são de forma, e nenhuma se resolve com constante.

⚠️ **Não implemento.** Forma nova no engine está fora do mandato de execução
autônoma, como a P-9.

## Reprodutibilidade

Ambas as varreduras estão no scratchpad da sessão e são recomputáveis do store
em minutos (8 curvas do ROUSSEAU × floor nominal e 0; depois 8 valores de floor
nas 2 finas).
