# YANG_2023_IJPEM 0,25 mm — trabalhada a pedido (15:09) e ASSINADA na classe SUB-SLIP

**2026-08-15 · store `20be19aabe11` · pedido direto do professor:** *"ten um
erro muito elevado, trabalhe nele"* · assinatura sob a delegação vigente
("continue o loop, eu assino tudo", renovada 12:41).

## Anatomia medida (antes de qualquer proposta)

| medida | valor | leitura |
|---|---|---|
| tripla vigente | 0,1664 / 0,4256 / 0,1452 | pior MAE aberto da fonte |
| viés | **+0,1664 = MAE** | sinal único — modelo perde devagar demais |
| ρ(resíduo, N) | **+0,96** | rampa: o erro acumula a taxa ~constante |
| classe mecânica | **STICK 100%** (slip=0 nos 4000 semiciclos, instrumentado) | alavancas de slip **não alcançam** (regra do censo de classes) |
| config aplicado | grupo `_m8` (c_bend 8 · k_ratchet 0,05 · emb 1,16 µm · delta_free 0,18 mm) | conferido por `config_used` — chave NÃO estava morta |
| dado | n=7 pontos, passos ~0,08, colapsa 42% em 2000 ciclos | paper paywalled; 0,25 ficou na fila POR MÉRITO (salto < 0,10) |

Em stick, os únicos canais vivos são embedding/creep (nível, finito) — o dado
colapsando sustentadamente é a assinatura **sub-slip** (a mesma das duas
YANG_2021 já assinadas: *canal estrutural ξ-dependente confundido*).

## A única forma stick do engine foi VARRIDA — e não fecha

`gth` (ratchet de stick com incubação; `gth_q=3,8` default = **a lei
N_L∝δ^−3,8 do PRÓPRIO paper**, PR-21): grade 27 células
(dref {0,15·0,20·0,25} mm × k {1e-5·5e-5·2e-4} × A0 {0·200·1000}), no grupo
`_m8` em sandbox:

- **Melhor célula: 0,1664→0,0861** (−48%; mx 0,2964; σ 0,1130) — **nenhuma
  perna fecha** (mx 3× o limite; σ 4,5×). O ratchet a taxa ~constante inclina
  a reta; o colapso do dado exige ~3× mais perda tardia.
- **A canária 0,18-flat (below-threshold, MAE 0,0076) trava as células
  fortes**: k≥5e-5 a destrói (+0,06 a +0,57) salvo A0=1000 — e aí o ganho da
  0,25 murcha para −10/−23%.
- **Inércia nas irmãs que deslizam: bit-idêntica** (0,45/0,65 — stick-only por
  construção funciona).
- Mesma estrutura do T13/YANG_2019 (2026-08-10): a forma trata a rampa, não o
  colapso — 2ª fonte, mesmo veredito.

## Veredicto

**ASSINADA em `_F5_EXCECOES`, classe sub-slip**, com esta prova. Reabre com:
(a) forma sub-slip nova que produza colapso (não só rampa) sem quebrar as
below-threshold; ou (b) dado de resolução melhor (o PDF segue inacessível;
companion OA só tem vidas). A gêmea de viés (+0,239, a 0,50-M6) **NÃO é da
classe** (desliza 0,32 mm/ciclo — medido) e fica na fila com defeito próprio.

## Reprodutibilidade

Sondas no scratchpad da sessão 3d12ac81 (`gth_yang23.txt` + instrumentação de
`resolve_transverse_slip`); grade completa impressa; sanidade: célula vazia
reproduz o store.
