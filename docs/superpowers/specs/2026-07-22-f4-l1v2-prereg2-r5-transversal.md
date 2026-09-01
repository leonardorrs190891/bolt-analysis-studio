# Pré-registro 2 (F4 L1 v2) — rota TRANSVERSAL do flanco + painel R5 (22 casos)

**Data:** 2026-07-22 · **Branch:** feature/l1-v2 (worktree C:\basl1v2, commit 1dd09a5) ·
**Executor:** sessão mestre (prompt-mestre §4). Escrito ANTES de qualquer fit R5 — imutável.
2º e ÚLTIMO prereg do candidato (c) (máx. 2 por candidato, plano-mestre §4.2).

## Correção factual ao prereg-1 (registrada, não improvisada)

O prereg-1 (G4-b) rotulou liu2020 como "axial coatings". **Errado**: o registry e o
apparatus_note (`liu2020.md`) documentam **transversal disp-controlled** (delta_amp
0,1–0,4 mm, 5 Hz, rollers). zhang18/19 idem (0,25/0,2 mm). Consequência: o canal L1
axial-only NÃO toca nenhum dos 22 casos R5 — o G4-b do prereg-1 era insatisfazível como
escrito. Este prereg-2 restaura o gate do plano-mestre §4.2 em força total (os 22 casos
R5 no tripé) usando a rota transversal do flanco (`flank_transverse_on`, commit 1dd09a5,
default-inerte, TDD 6 contratos), que o ledger F4 já antecipava ("fechar os 22 pode
exigir o flanco também sob excitação transversal").

## Diagnóstico pré-fit (ponto-a-ponto, lição F3 — feito ANTES deste prereg)

Baseline dos 3 casos sondados: colapso a F0=0 por mecanismos default M16-UFU
(wear 0,40–0,46 + embedding 0,31–0,62 + loosening rotacional 0,17–0,21 + creep
0,03–0,05) vs dado 0,83–0,99. O gap NÃO é canal de perda faltante — é (i) supressão
por leitura dos canais que os papers excluem + (ii) a forma de flanco transversal
para o Estágio II. Alvos de forma (apparatus_notes): zhang19 perda 12% @2e5 =
6% Estágio I (≤500 ciclos) + 6% Estágio II log-linear desacelerante; liu2020
looseness ∝ A_F^1,5–1,6 (0,1→0,3 mm) com salto p/ ^3,2 em 0,4 mm = trinca de fadiga
(~1e4 ciclos, atribuição explícita do paper §3.1.2); MENOS perda relativa com MAIS
preload nos 2 rigs (P0-sweeps fig5b/fig13).

## Receitas per-fonte (leitura primeiro; DOF de fit explícito)

Comum às 3 fontes (prov entre parênteses):
- `flank_wear_on=1` + `flank_transverse_on=1` (switches por prereg, nunca fitados);
- `tr_loose_gain=0` (zhang18: paper — porca prevailing-torque + ZERO rotação medida;
  zhang19: paper — zero rotação medida, sensor 0,045°; liu2020: assumed/paper-attribution
  — estágios I/II = plasticidade + fretting de flanco, sem rotação reportada, retenção
  96%+ @0,2mm incompatível com back-off);
- `K_archard=0` (paper-attribution: SEM/EDX localiza o desgaste no FLANCO da rosca;
  liu2020: rollers isolam a fricção placa-placa);
- `C_creep=0` (paper-attribution: nenhum canal lento além de plasticidade+wear
  reportado; reavaliar SE o resíduo pós-fit mostrar deriva log-t sistemática — nesse
  caso documentar e re-fitar UMA vez com C_creep lido do platô);
- `emb_depth` LIDO da curva (leitor L24 `emb_from_curve` na curva de referência da
  fonte; Estágio I: zhang19 ≈6% de 10 kN; zhang18 ≈metade da perda total; liu2020
  ≈3,5% de 18 kN incl. micro-transiente) + `N_emb` da escala do Estágio I (~300–1000).

Fit (grade determinista, curvas completas, cap na extensão do CSV):
- **LIU_2020 zinc** (7 casos): fitar **{k_wear_flank, flank_s_crit}** nas 4 curvas do
  amplitude-sweep (fig9); `flank_amp_exp=1,5` FIXO (medido no próprio paper, 1,5–1,6).
  As 3 curvas do P0-sweep (fig5b) são VALIDAÇÃO zero-fit-extra (direção: mais P0 =
  menos perda relativa). Seed k: âncora KB thread 8,34e-15 (ordem de grandeza).
- **LIU_2020 DLC** (2 casos): par tribológico DISTINTO — fitar **{k_wear_flank}** só;
  `flank_s_crit` herdado do zinc; µ=0,126 (paper).
- **ZHANG_2018** (9 casos): fitar **{k_wear_flank}** (amplitude única 0,25 mm →
  s_crit/k degenerados; `flank_s_crit=0` documentado: slip profundo, limiar absorvível
  em k). Seed = âncora KB 8,34e-15 (35CrMo/SCM435 = ESTE par). Grupo
  `fig16_with_locker`: `flank_transverse_on=0` no grupo (paper: o locker separa os
  flancos e PREVINE o slip relativo — Estágio II ~flat; Estágio I igual).
- **ZHANG_2019** (4 casos): idem zhang18, **{k_wear_flank}** próprio (SCM435), µ=0,241.

Total de DOF fitados novos: 4 (k zinc, s_crit zinc, k DLC, k z18, k z19 = 5 números,
sendo s_crit forma-por-par e 4 magnitudes per-rig/par — mesmo padrão "formas
transferem, constantes por-par" do resto do projeto).

## Trim declarado ANTES do fit (bloco C, convenção F3/CLAUDE.md)

- `liu2020_fig9_zinc_AF0.4mm`: cauda de trinca de fadiga (atribuição explícita do
  paper, ~1e4 ciclos) — trim pela regra da taxa (>3× mediana do Estágio II, contígua
  até o fim), changepoint auditável registrado no resultado. O caso conta no gate com
  a métrica janelada (mesmo tratamento li2022ti_full/F3-LOTE3).

## Gate G4-b-v2 (imutável)

- **PASS:** os 22 casos R5 com **MAE<0,1 E maxerr<0,1** (métrica janelada nos trims
  declarados acima), com as receitas/DOF acima — nada além dos 5 números fitados.
- **G4-c (zero regressão):** os cfg novos só existem nas 3 fontes R5; fora delas o
  engine é default-inerte (TDD bit-identidade). Verificação por amostra: 6 controles
  (2 transversais adotados, 2 axiais Liu2017, li2022ti axialmin com per-rig F2,
  1 UFU) re-simulados bit-idênticos.
- **FAIL:** qualquer caso >0,1 fora de trim declarado ⇒ FAIL2 do candidato (c)
  (2º prereg) → candidato (b) debris (prereg novo) e, se também FAIL2, rodada 6 +
  **PARE** (professor) — caminho do plano §4.3.

## Registro

Resultado em `New_Theory/f4_r5_panel_result.json` + curvas per-caso; adoção NÃO
acontece no branch — se PASS, protocolo F0 (merge gateado + adoção per-rig no main,
F4.4, escritor único).
