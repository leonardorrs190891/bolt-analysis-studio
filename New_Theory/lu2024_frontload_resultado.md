# Lu2024 — a forma front-loaded (b) morre nas CONTAS de transferência intra-fonte; três linhas fechadas, zero preregs

**Data:** 2026-07-28 · **Custo:** zero preregs (3 linhas mortas em contas de projeto)
**Scripts:** `lu_frontload_conta.py` (+ variante normalizada inline), `lu_nemb_percase_conta.json`,
`lu_nemb_regra_feature.json` · **Baseline:** store `294808504d83` (controles negativos 0,00e+00)

## 1. Linha N_emb (saída (a) do diagnóstico de 27/07) — FECHADA, gate FAIL 2×

O diagnóstico `6a1c9f2` deixou a decisão: per_case no T4Nm com justificativa
pré-medida, ou aceitar o gate como falho. Executei a versão DEFENSÁVEL da (a):
regra de isenção **por feature pré-medida** (N_emb=1 só onde fração-de-perda-cedo
do dado > modelo default). A regra discrimina exatamente o T4Nm (28 % vs 39 % —
déficit não existe nele) e inclui todos os outros 9 — **inclusive o amp0p25, que
tem o MAIOR déficit (80 % vs 28 %) e mesmo assim PIORA sob N_emb=1** (+0,013).
⇒ cláusula "nenhum caso pior" falha DE NOVO, agora com a regra limpa. MAE mediano
−31,7 % (passaria); maxerr mediano −25,3 %. **Não adotado; ajustar o valor para
passar seria metric-chasing** (o 1,0 é feature-selected; mexer quebra a procedência).
Nota: o leitor per-curva (`emb_depth_from_early_drop`) é DOUTRINA-BLOQUEADO aqui —
método axial; no transversal a queda-inicial é loosening-dominada (mis-atribui).

## 2. Forma (b) "taxa front-loaded" — FALSIFICADA em 2 parametrizações

Emulação bit-exata por monkeypatch em `RotationalLooseningLoss.rate` (fator
multiplicativo em dF_0/dE/dθ), desenho anti-FAIL1 da própria fila: **âncora na
varredura de amplitude (fig18, 5 curvas), transferência ZERO-REFIT cega na
varredura de torque (fig20, 5)**.

| variante | driver do decaimento | âncora (fig18) | cegas (fig20) | PR-37′ |
|---|---|---|---|---|
| hiperbólica | θ_acc absoluto (θ0=0,020 rad) | mediana −38 % | T4/T10 melhoram; **T22 0,052→0,102, T28 0,041→0,089 PIORAM** | ✗ (2 piores) |
| normalizada | fração de F₀ perdida via hélice (c0=0,10) | mediana −41 % | **4 pioram** (até T16 que era boa) | ✗ (4 piores) |

**O padrão nas duas:** a forma melhora exatamente as curvas onde o modelo
sub-front-loada e **danifica as que já estavam certas** (torques altos) —
assinatura de redistribuição de erro, não de física faltante. O front-load que o
Lu pede é **dependente de condição dentro da própria fonte** (fig18 quer forte;
fig20 de torque alto recusa); nenhuma constante única transfere — e constante
por condição = "tuner com nome bonito" (critério G-A3, já registrado).

## 3. Estado final da fonte

- **LU_2024 (10 curvas) segue form-limited**, com a descrição afinada: *demanda de
  front-loading heterogênea por condição; embedding-cinético e decaimento
  rotacional (2 drivers) falham a transferência intra-fonte pelo mesmo padrão* —
  a mesma classe de veredicto do Chu (estrutura temporal do kernel, §4.54a),
  medida aqui com o desenho de transferência que o Chu não permitia.
- **Sun grease-standard (1 curva, 0,0999/0,319)**: sem desenho possível (n=1);
  segue form-limited documentada, dorme com o Karlsen.
- Ganhos reais ficam registrados como INFORMAÇÃO (não adotados): T16Nm entraria
  no tripé sob N_emb=1; fig18 mediana cairia ~40 % sob front-load — quem
  destravar a heterogeneidade ganha isso de volta.

## 4. Reprodutibilidade

```bash
py -3.12 New_Theory/lu_frontload_conta.py     # variante hiperbolica (ancora+cegas)
# variante normalizada + contas N_emb: blocos inline no historico da sessao
```
