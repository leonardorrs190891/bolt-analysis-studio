# PREREG — `rousseau2025_steel_t10`: ratchet cinemático com TODAS as constantes lidas do θ(N) publicado (adoção-de-MELHORIA)

**2026-08-19 (noite)** · **gates congelados neste commit** · store `4c14f69f1d81`
(censo 146/205) · mandato das 18:5x: *"siga agora para …rousseau2025_steel_t10.html"*.

## 1. O que mudou desde a falsificação de 2026-08-15

O veredicto *transfer-limited* (`rousseau_ratchet_transferencia_resultado.md`)
morreu de causa certa — nenhuma constante compartilhada serve às 4 abertas — mas
media a pergunta errada: a fonte publica **a rotação da porca** (Figs. 4/5, eixo
secundário, *"bolt–nut relative rotation"*), e a rotação dá as constantes POR
LEITURA, sem compartilhar nada e sem fitar a métrica.

**Dado novo digitalizado hoje** (da extração vetorial existente; validação: θ_fim
t10 = 10,92° vs 10,97° da leitura manual do §4.27; t12 = 4,36° vs 4,23°):

| leitura | valor | validação |
|---|---|---|
| dF/dθ (aço t10) | **919,7 N/deg**, r²=0,9997 (168 pts) | t12 dá 893,6 (3 % — lei da junta) |
| dF/dθ (HDPE) | 117,9 / 117,0 N/deg (t10/t12) | mesma lei, laço ~8× mais mole |
| θ(N) pós-onset | linear, r²=0,983 | slope 0,0736°/ciclo |
| onset de dreno | fim da folga ~1° ⇒ N≈25 | F publicado plano: (20, 1,0000) |

## 2. Capacidades construídas hoje (default-inertes, TDD 7/7)

1. **`free_spin_kin`** (§4.56): fração da rotação relativa que NÃO drena —
   `dF_0 = −k_b·lead·(1−fsk)·dθ`; θ e dE ficam com a rotação total. Física: a
   rigidez de dreno real é a série do laço (parafuso+membro+interfaces), menor
   que o k_b puro da hélice. `fsk=0` = OFF bit-idêntico.
2. **`loose_amp_exp` no graded_scrit**: a docstring já prometia e o ramo não lia
   (medido inerte — classe item R do lado do código). Implementado com a fórmula
   do sítio k_ratchet; `exp=1` = bit-idêntico; `exp=0` = taxa constante.

## 3. O pacote (per_case `steel_t10`; TUDO lido, ZERO fit à métrica)

| campo | valor | leitura |
|---|---|---|
| `loose_rate_mode` | graded_scrit | forma existente (kernel cinemático) |
| `s_crit_loose` | 0,0 | rotação medida arranca de N~16 |
| `free_spin_kin` | **0,7195** | 1 − 919,7/3278,3 (dF/dθ ÷ k_b·lead) |
| `loose_amp_exp` | **0,0** | θ(N) pós-onset linear r²=0,983 ⇒ taxa constante |
| `k_loose_graded` | **0,01394** | slope 0,0736°/ciclo ÷ 5,28°/(ciclo·k) |
| `slip_onset_W` | **3,5465 J** | W_slip_acc no N=25 (fim da folga de 1° do traço θ) |
| `emb_depth` | **0,0** | ponto publicado (20, 1,0000): zero queda em 20 ciclos |
| `C_creep` | **0,0** | mesma leitura de limite (emb+creep ≤ 0,5 % em 20 ciclos) |

Blindagem de token: `steel_t10` é substring de `steel_t10_amp0p2` e o matcher
per_case aplica o PRIMEIRO token na ordem do dict — a entrada
`"steel_t10_amp0p2": {}` vem ANTES (casa, nada muda, break). Teste-guarda fixa
o invariante de ordem.

## 4. Medições sandbox (já feitas) — isto é adoção de MELHORIA, não fechamento

**0,1548/0,2702/0,0994 → 0,0289/0,0668/0,0324** (5,4×/4,0×/3,1×). MAE e res.máx
FECHAM (0,58×/0,67×); **σ_res fica a 1,30×** — a curva NÃO entra no tripé.
Validação independente: **θ_fim do modelo 10,42° vs 10,92° medido** (−4,6 %).

Resíduo restante NOMEADO com número: a derivada do F publicado é um **sino**
(pico 0,0099/ciclo em N=100, meia-altura N=60) e o dreno local **cai** no fim
(919,7 → ~500 N/deg entre θ=8° e 10,4° — contato de flanco parcial em F baixo).
O engine não tem nenhuma das duas formas; re-leituras alternativas da mesma
estrutura (meia-altura, k do pico, floor lido 0,1086) foram MEDIDAS e PIORAM
(0,065–0,184) — o pacote está no ótimo da estrutura disponível. O floor lido
0,1086 foi RECUSADO: o dado publicado atravessa-o (último ponto 0,0951) — regra
da barreira artificial (§7 ICMEZ).

## 5. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | alvo reproduz | 0,0289/0,0668/0,0324 ao dígito pelo caminho canônico |
| **G2** | irmãs | as 7 bit-idênticas (incl. `steel_t10_amp0p2` pelo token-vazio) |
| **G3** | isolamento | Δ=0 exato fora do ROUSSEAU no re-stamp |
| **G4** | re-stamp íntegro | fingerprint único nos 210 (gotcha do sintético) |
| **G5** | censo | **146/205 inalterado** (a curva NÃO fecha — predição declarada) |
| **G6** | sincronização | triagem (forma nomeada atualizada: sino+dreno-caindo), docs vivos, aging, HTML |

## 6. Predições registradas

1. G1 ao dígito. 2. Censo 146 (não fecha; σ 0,0324 = 1,30×). 3. θ_fim 10,42° —
consistência com o publicado a −4,6 % SEM ter usado θ_fim para fixar k (k veio
da taxa). 4. A t10 deixa de ser a pior aberta do ROUSSEAU (0,0289 < hdpe_t10
0,0927). 5. As 3 curvas com traço θ na fig4 (HDPE) são o próximo passo com o
MESMO instrumento — prereg próprio, leituras próprias (dF/dθ=118, θ_fim
28/23/4°), fora do escopo deste.


## Estado

EXECUTADO 2026-08-19 (19:0x) como adocao-de-melhoria (predicao confirmada: sigma 1,30x, nao fecha). Superseded pelo passo 2 (taxa-regredida) na mesma noite. Resultado em rousseau_t10_ratchet_lido_resultado.md.
