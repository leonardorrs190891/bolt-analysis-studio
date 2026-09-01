# PREREG — `rousseau2025_steel_t10_amp0p2`: a Fig. 6 TAMBÉM publica θ(N) — leituras próprias + partição

**2026-08-19 (21:3x)** · **gates congelados neste commit** · caso 3 da fila do
mandato 20:47 · casos 1–2 (steel_t10, hdpe_t12) fechados hoje.

## 1. A rota que quase foi descartada

Sem traço θ atribuído, 4 formas foram medidas e falsificadas (arrest-proxy
r²=0,22; g_trig r²<0; exp=1 mata a curva; taxa-média mata cedo — derivada do
CSV oscila ±50 %). A rota REAL: **a Fig. 6 publica a rotação** (eixo
secundário, 0–9°) — extraída HOJE direto do PDF pelo pipeline validado
(dashes + ticks; θ_ini = −0,01 ✓ zero).

## 2. Leituras (todas da própria curva)

| leitura | valor | origem |
|---|---|---|
| θ_fim | **9,05°** | traço Fig. 6 (visual ~8,4–9) |
| dF/dθ cru | −333,4 N/deg (r²=0,977) | regressão F-vs-θ — ⚠️ 2,7× menor que os 920 da Fig. 5 (mesma junta, F₀ 3,5 vs 10 kN): rigidez de contato cai com a carga — consistente com o dreno-caindo do fim da t10 |
| **partição** | dreno_rot = (2926 − 798)/9,05 = **235 N/deg** | paralelos = emb+creep+wear do grupo (798 N; a regressão crua os atribui à rotação pois θ ∝ N) — procedimento validado na hdpe_t12 |
| `free_spin_kin` | **0,9283** | 1 − 235/3278 |
| `k_loose_graded` | **0,01729** | slope θ = 0,0913°/ciclo (r²=0,996 LINEAR) ÷ 5,28 |
| `loose_amp_exp` | 0,0 | θ(N) linear ⇒ taxa constante |
| `s_crit_loose` | 0,0 | rotação arranca cedo |

Pacote no per_case do `ROUSSEAU_2025` (grupo do aço), token `steel_t10_amp0p2`
— a entrada JÁ EXISTE como `{}` (blindagem da adoção steel_t10) e vem ANTES do
token `steel_t10` na ordem do dict: o pacote entra NELA (a ordem continua
blindando: a amp0p2 casa a própria entrada; a steel_t10 não casa o token da
amp0p2). Floor do grupo 0,0 fica (o dado atravessa 0,1795 lido ⇒ barreira).

## 3. Medições sandbox — FECHA

**0,0957/0,1545/0,0412 → 0,0324/0,0694/0,0194** (0,65×/0,69×/0,78×). θ_fim
9,03° vs 9,05 lido; F_fim 0,172 vs 0,164. Robustez: fsk pela banda ±10 % dos
paralelos fecha 3/3; k×1,1 fecha, k×0,9 não (além da incerteza da leitura
r²=0,996) — 4/5.

## 4. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | alvo fecha | 0,0324/0,0694/0,0194 ao dígito pelo canônico |
| **G2** | irmãs | as 7 bit-idênticas |
| **G3** | isolamento | vs o store commitado `3bb2ca3c9128`: mudam EXATAMENTE hdpe_t12 (prereg anterior) e amp0p2 — nada mais (a errata de prov é Δ=0) |
| **G4** | re-stamp íntegro | fingerprint único nos 210 |
| **G5** | censo | **148 → 149/205** (com a t12 em voo: 147→149 no carimbo único) · abertas 17 → 16 |
| **G6** | sincronização | triagem, docs vivos, aging, HTML, lista, parada |

## 5. Predições registradas

1. G1 ao dígito. 2. Censo **149/205** — QUINTA curva a fechar por modelo no
dia. 3. O dF/dθ dependente de F₀ (920 → 333 na mesma junta) é evidência nova
da física do dreno (série com rigidez de contato ∝ carga) — registrar no
§4.56. 4. Próximo da fila: `hdpe_t10` (dado ruidoso — medir o piso primeiro).

## Estado

EXECUTADO 2026-08-19 (21:3x-21:4x): G1/G2 na hora; carimbo único com t12+errata.
