# PREREG — `rousseau2025_hdpe_t12`: kernel cinemático com fsk PARTICIONADO e k lido do θ publicado

**2026-08-19 (21:0x)** · **gates congelados neste commit** · mandato das 20:47
(fila): *"faça as melhorias nos demais casos, um por vez, e só parar quando
atingir o tripé"* — caso 2 da fila; caso 1 (`steel_t10`) fechou às 20:0x.

## 1. O grupo REAL e a lição do achado

As curvas HDPE resolvem para **`ROUSSEAU_HDPE`** (grupo próprio: floor 0,2,
`GA_member`, `delta_amp_mm` por espécime), NÃO para o `ROUSSEAU_2025` — achado
desta sonda; o raciocínio anterior usava a entry errada. O floor 0,2 do grupo
FICA (procedência própria; o dado termina em 0,346 > 0,2 = não-barreira).

## 2. As leituras (traço θ da Fig. 4 re-extraído e validado — errata §8 do doc steel_t10)

| leitura | valor | origem |
|---|---|---|
| θ_fim | **12,65°** | re-extração do PDF por ticks (validada vs impresso ~12,5-13) |
| dF/dθ | −209,4 N/deg (r²=0,9965) | regressão F-vs-θ |
| **partição** | dreno_rot = (ΔF_total − paralelos)/θ = (2616−760)/12,65 = **147 N/deg** | paralelos = emb+creep+wear do grupo (760 N) — na t12 os canais paralelos são REAIS (zerá-los piora 3×), diferente da steel_t10; a regressão crua atribui à rotação o que os paralelos perdem (θ ∝ N) |
| `free_spin_kin` | **0,948** | 1 − 147/2826 (k_b da t12 = 5,814e8) |
| `k_loose_graded` | **0,01018** | bisseção por θ_fim = 12,65° (VÁLIDA aqui: floor 0,2 impede a exaustão que degenerou a bisseção na steel_t10) |
| `loose_amp_exp` | 0,0 | θ(N) quase-linear (slope 0,0317°/ciclo) — taxa constante |
| `s_crit_loose` | 0,0 | rotação arranca cedo (θ>0,5° em N≈5) |

Zero fit à métrica: as 3 pernas são PREDIÇÃO. Pacote no `per_case` do
`ROUSSEAU_HDPE` com token `t12` — ⚠️ conferir colisão de token com o
`delta_amp_mm` existente e com `hdpe_t12` vs outros; usar token que case SÓ a
t12 (`hdpe_t12` casa apenas ela na fonte HDPE: t10/t14 não contêm).

## 3. Medições sandbox (já feitas)

**0,0566/0,1133/0,0456 → 0,0230/0,0604/0,0227 — FECHA O TRIPÉ** (0,46×/0,60×/
0,91×). θ do modelo = 12,65° EXATO (bisectado). Robustez DO PROCEDIMENTO
(perturbar fsk e re-ler k por θ): fecha para dreno 147–158 N/deg, janela
consistente com a incerteza ±10 % dos paralelos (141–152). Vizinhança pontual
(sem re-leitura) é mais apertada — declarado: a variedade de leitura é
(fsk → k(fsk)), não o produto cartesiano.

## 4. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | alvo fecha | 0,0230/0,0604/0,0227 ao dígito pelo canônico |
| **G2** | irmãs | as 7 bit-idênticas (t10/t14/amp0p2 do HDPE e as 3+1 do aço) |
| **G3** | isolamento | Δ=0 exato fora do ROUSSEAU no re-stamp — o MESMO carimbo absorve a errata de prov da steel_t10 (`25d6ace5adca`), cujo gate é Δ=0 em TODAS as 210 exceto a t12 deste prereg |
| **G4** | re-stamp íntegro | fingerprint único nos 210 (gotcha do sintético) |
| **G5** | censo | **147 → 148/205** · abertas 18 → 17 · ROUSSEAU_HDPE 2 → 1 aberta |
| **G6** | sincronização | triagem (catraca), docs vivos, aging, HTML, lista, parada |

## 5. Predições registradas

1. G1 ao dígito. 2. Censo 148 — QUARTA curva a fechar por modelo no dia, mesma
estrutura (constantes de leitura/partição de observável publicado). 3. θ_fim
12,65 exato (bisectado — não é predição; a predição é o RESTO: as 3 pernas).
4. A próxima da fila é a `steel_t10_amp0p2` (sem traço θ — rota diferente).


## Estado

EXECUTADO 2026-08-19 (21:4x): G1 ao digito (0,0230/0,0604/0,0227 — FECHA), G2 as 7 irmas bit-identicas; consolidado no carimbo 6ccf85e6bff3 (censo 150) junto com amp0p2 e hdpe_t10.
