# Prereg — bloqueio das FAMÍLIAS FALSAS por chave cega (δ=0 · F_amp=0)

**2026-08-01** · terceira ocorrência da mesma classe no dia (LU piso
cruzado 0,5×1,0 mm → ROUSSEAU espessuras diferentes → agora axiais).
Achado ao executar "(2) CACCESE" da sequência autorizada.

## O defeito

A chave mecânica de família é `(fonte, δ_mm, F_amp_N, modo)`. Em casos
**axiais/creep** δ=0 **e** F_amp=0 ⇒ **todas as curvas da fonte caem na
mesma chave**, viram "réplicas" e produzem um "piso" que é, na verdade,
**dispersão ENTRE CONDIÇÕES DIFERENTES**.

Varredura (todas as famílias com δ=0 ∧ F_amp=0 ∧ n≥2):

| fonte | n | σ da "família" | limite que isso impõe | o que são de fato |
|---|--:|---:|---:|---|
| **JCSR_2023** | 5 | **0,2214** | **0,2214** (8,9× o global) | 5 AMBIENTES (indoor/outdoor/seawater/galv/inox) |
| **CACCESE_2009** | 7 | 0,0270 | 0,0270 | 7 condições (compblock 34/71 kPa, protruding, retighten 12,7/19,1, tapered rep1/rep2) |
| LI_2022_MARSTRUC | 6 | 0,0023 | 0,0250 (global vence) | 6 rugosidades — inócuo |
| QIN_2024 | 3 | 0,0019 | 0,0250 (global vence) | 3 correntes — inócuo |

**Impacto medido no veredito** (curvas que passam SÓ pelo piso falso):
`jcsr2023_galv_seawater` (σ 0,0468), `jcsr2023_plain_seawater` (0,0371),
`caccese2009_retighten_19p1mm` (0,0263). **3 curvas.**

## Ação (mesma do erratum ROUSSEAU)

Bloquear o pareamento automático dessas curvas em
`_SEM_FAMILIA_MECANICA`, com motivo por curva. **Exceção**: o par
`caccese2009_tapered_45kN_rep1 ↔ rep2` **é réplica de verdade** (mesma
condição, "rep1"/"rep2" no nome) ⇒ entra em
`_PARES_REPLICA_DECLARADOS`, preservando o piso legítimo dessa condição
(medido: MAE 0,0372 · mx 0,0676 · **σ 0,0234**).

## Gates

- **G1 (integridade)**: depois do bloqueio, nenhuma família de δ=0∧F=0
  com condições diferentes sobra; o único par CACCESE é o rep1↔rep2.
- **G2 (efeito declarado ANTES)**: **3 curvas saem do tripé** (as da
  tabela acima) — é o preço de trocar limite falso por limite honesto,
  igual ao erratum ROUSSEAU. Censo previsto: 132 → **129**.
- **G3 (nada mais muda)**: nenhuma outra curva do censo muda de estatuto.
- **G4**: o novo limite do CACCESE passa a ser `max(0,025; 0,0234)` =
  **0,025** (o par verdadeiro é MAIS apertado que o falso); o JCSR volta
  ao global 0,025.
- **G5 (sincronia)**: censo/_VIVAS/docs/páginas/testes no mesmo commit.
  Fingerprint NÃO muda (piso é do report, não do engine/cfg).

## Nota de método

Isto **não é regressão do modelo**: as 3 curvas nunca estiveram
corretas — estavam sendo julgadas contra uma régua inventada pela
dispersão entre condições. O terceiro caso da mesma classe no dia
justifica a pergunta estrutural (fila do professor): **a chave de
família precisa de discriminador de condição**, não de remendo por lista.
