# Plano-mestre — aplicar os modelos L1–L7 e atingir MAE E maxerr < 0,1 em todas as curvas

**Data:** 2026-07-17 · **Meta declarada (professor):** todos os modelos do branch `feature/l1-l7-gaps`
aplicados + software validado com **erro médio (MAE) E máximo (maxerr) < 0,1 para todas as curvas
comparáveis** da suíte. · **Métrica:** o tripé por curva (MAE/maxerr/σ_res) já adotado pela campanha.

**Estado de partida (pós-branch, paridade certificada):** 202 casos (180 herdados + 22 R5);
mediana 0,047; **54 casos MAE>0,1**; maxerr>0,1 em fração maior (censo #48: ~110/178 — recensear
no passo 1.4). Os 22 casos R5 têm MAE 0,33–0,75 **por design** (alvo declarado do gap L1).

---

## Princípio de sincronização (papéis, para nunca colidir)

| Ator | Escreve | Nunca escreve |
|---|---|---|
| **Campanha** (rotina de otimização, `converge-model`/`paper-study`) | `adopted_configs.json`, `joint_calibrations.json`, store canônico, ledger | formas novas de engine |
| **Branches de forma** (como o l1-l7) | engine default-inerte + gates + casos + KB | adopted_configs/joint_calibrations |
| **Professor** | decisões de adoção (prereg aprovado), exceções | — |

Regras permanentes: (i) forma nova só entra default-inerte via branch gateado; (ii) ligar qualquer
switch = prereg da campanha (os switches estão `fittable=False` de propósito — a otimização não pode
"descobri-los"); (iii) um único escritor por vez no main (campanha em vigília durante merges);
(iv) todo gate usa o tripé e o baseline re-pinado vigente.

---

## Ordem de execução

### Fase 0 — Integração (imediata, ~1 sessão)
0.1 Fechar a onda final de fixes do branch (DOF-guard 94, VarSpecs×12, pasta F versionada) — em curso.
0.2 **Pausar a campanha** (vigília) e fazer o merge `feature/l1-l7-gaps` → main (zero conflitos
    esperados; o fix do `test_transfer_validation` já está no main e resolve a única falha herdada).
0.3 Pós-merge no main: suíte completa + `report --all` (lá com os 3 CSVs UFU → 202 casos) e commit
    do store pela via normal da campanha. NÃO carregar o store do worktree.
0.4 **Re-pinar o baseline da campanha**: novo indicador = 202 casos / mediana ~0,0471 / MAE>0,1: 54
    + **censo de maxerr>0,1** (rodar `error_budget` e registrar o tripé por curva — este censo é a
    lista-mestre da meta). Atualizar o prompt/instruções da campanha com: baseline novo, alavancas
    novas disponíveis (tabela do `l1l7_final_report.md` §2) e a regra dos switches.

### Fase 1 — Adoções Onda A: risco-zero (1 prereg em lote)
1.1 `kj_mode="pedersen"` como proveniência de geometria (PASS-inert comprovado no PACK).
1.2 Check L7 ligado por default (informacional; avisa par não-casado µ×k_wear).
1.3 Bandas do KB no `check_input` (avisos fora-da-banda na calibração/GUI).
Gate: paridade exata (nada muda por construção) + report limpo. **Não move a meta; remove risco.**

### Fase 2 — Adoções Onda B: comportamentais per-rig (3 preregs da campanha, em ordem de alavancagem)
2.1 **Canal de flanco per-rig no H.Li2022** (nível 0,268→0,033 no gate T4): fecha ~4 casos axial×freq.
2.2 **Creep saturante vs log-t** nos blocos de creep (JCSR/Caccese/Qin/Nah/li2022marstruc): alvo =
    caudas longas; adota-se por fonte apenas onde o tripé melhora.
2.3 **Clamp L3 (`famp_couple_on`) + re-fit conjunto de `tr_loose_gain`** (nota T2: o gain atual foi
    calibrado com F_amp sem clamp): alvo = transversais força-mode e casos com F_amp registrado.
Cada prereg: fit em curvas completas, tripé no gate, adoção por-fonte (nunca global cega).

### Fase 3 — Varredura sistemática até a meta (o grosso do trabalho)
3.1 Rodar `error_budget` pós-Onda-B → **ranquear os violadores por mecanismo dominante** (a
    decomposição por mecanismo do pacote validation faz isso) em 3 blocos:
    - **Bloco A — fitável**: erro de nível/constante → `paper-study` per-fonte (a rotina existente),
      com o tripé como gate. Estimativa: maioria dos ~54 MAE>0,1 herdados.
    - **Bloco B — forma faltante**: hoje = **L1** (22 casos R5 + folgas dos sweeps axiais). Ver Fase 4.
    - **Bloco C — irredutível**: caudas de fratura (li2022ti, liu2022_fig8_t4, Liu2025 amp0p4 —
      convenção de trim já existente), scatter de réplicas (Bauer fig6 MAX 0,157 já demonstrado
      irredutível; Lu T10 piso). Para estes: **protocolo de exceção** (abaixo).
3.2 Loop da campanha no Bloco A: passada MAE<0,1 primeiro, depois passada dedicada de **maxerr**
    (o maxerr cai com forma certa no trecho certo — joelhos/pisos — não com nível; usar o
    diagnóstico ponto-a-ponto início/taxa/forma/piso que já é lição da campanha).
3.3 A cada N adoções: re-run mestre + painel; parar o loop quando o ganho marginal por prereg < tol.

### Fase 4 — L1 mecanismo v2 (a única física nova pendente; branch gateado novo)
4.1 Candidatos já delimitados pela falsificação (não partir do zero): expoente de amplitude ≥1,5–3,2
    (medido no Liu2020), termo de onset/terceiro-corpo (debris), ou acoplamento slip-limiar. 
4.2 Mesmo protocolo deste branch: default-inerte → gate B1-v3 (slope Liu2017 −2,2e-5/N ± 2×) **+**
    os 22 casos R5 como gate de forma (MAE alvo <0,1 neles) + zero regressão transversal.
4.3 Se 2 preregs falharem de novo → rodada 6 de literatura focada no mecanismo (leads Mäntylä 2020,
    Juoksukangas, Jiménez-Peña já nomeados) e/ou experimento UFU.
Fechar L1 é o que converte os 22 casos (0,33–0,75) para a meta — maior alavanca individual.

### Fase 5 — Certificação final
5.1 `report --all` + `error_budget`: **100% das curvas comparáveis com MAE<0,1 E maxerr<0,1**, exceto
    as do **ledger de exceções** (cada uma com causa demonstrada — scatter de réplica quantificado ou
    trecho out-of-model trimado por convenção — e autorizada pelo professor, como Karlsen run7p1).
5.2 Atualizar `concept_coverage.html`, `MODEL_LEGITIMACY.md` (§ novo: estado da meta), CLAUDE.md
    (roadmap: itens 4/9/10 fechados/reescritos) e o relatório mestre com o painel final.
5.3 (Opcional) Experimento-âncora UFU do `W_conf_ref` segue como único item físico externo ao software.

### Fase 6 — Documentação completa do processo (o Manual; fecha o projeto)
Deliverable: `docs/MANUAL_BAS_V2/` (pt-BR) + hub `manual.html` no explorador de variáveis. O manual
é o **fio condutor** que linka os docs vivos existentes (concept_*, MODEL_MATH_REFERENCE,
MODEL_LEGITIMACY, METHODOLOGY/MEM, estudos por fonte, reports) — nunca cópia deles. Três volumes:
- **01 — Entender o modelo**: paradigma MSD + estado lento + 4 mecanismos + dano; energia como
  invariante; two-factor; a tese "formas transferem, constantes são por-par/rig"; tabela de
  constantes × proveniência (medida/âncora/handbook/fitada + onde vive); L1–L7 (limitação → forma
  → gate); histórico de falsificações como força do método (MEM/FAIL2).
- **02 — Explicar o modelo** (aula/defesa/paper/revisor cético): narrativa em 3 níveis (elevator /
  10 min / seminário); 5 figuras-chave geradas do store real por `scripts/manual_figs.py` (anatomia,
  decomposição, painel 202 casos antes/depois, tornado §4.42, mapa formas×fontes); FAQ de objeções
  com evidência (overfitting/identifiabilidade/LOCO/exceções/cobertura); glossário.
- **03 — Aplicar o software** (manual do usuário): instalação + comandos; fluxo launch→wizard→
  Builder→Solver→Results (módulo V2); **junta nova passo-a-passo** (inputs e proveniência de cada
  um, bandas do KB, leitura de decomposição/estágios); **paper novo fim-a-fim** (digitalizar→nota→
  caso→fit gateado→adoção→report); reprodutibilidade total; troubleshooting.
Gate: números só do store/ledger real; figuras por script versionado; links verificados. É a
última fase — depende da certificação (Fase 5) para os números finais serem os definitivos.

---

## Protocolo de exceção (para a meta ser honesta)
Uma curva só sai da meta com: (1) demonstração quantitativa (ex.: dispersão entre réplicas do mesmo
ensaio > 0,1 — caso Bauer fig6), ou (2) trecho fisicamente fora do modelo (fratura por fadiga) com
trim registrado; (3) entrada no ledger com assinatura do professor. Meta reformulada com precisão:
**tripé <0,1 em todas as curvas comparáveis não-excepcionadas, com ledger de exceções ≤ ~5% do total.**

## Riscos operacionais
- **Limite de gasto**: as fases 2–4 são intensivas em fits; elevar o teto antes de cada onda (5
  interrupções nesta execução).
- **Concorrência**: merges só em vigília da campanha; worktree curto (`C:\bas2l17`) para branches de
  forma; store nunca commitado a partir do worktree.
- **Meta maxerr**: é mais dura que a mediana — esperar que o Bloco C (exceções) concentre os últimos
  ~3–5% e resistir à tentação de fitar scatter (lição per-curva/coerência preditiva do MEM).
