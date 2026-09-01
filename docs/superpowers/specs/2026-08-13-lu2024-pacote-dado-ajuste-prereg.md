# PREREG — pacote LU_2024 dado+ajuste (molde D-Y/D-S): CSVs corrigidas + re-fit + pisos, num passo só

**Data:** 2026-08-13 (noite) · **Sessão B** · Gates IMUTÁVEIS depois deste commit.
**Antecedentes medidos (nada disto é novo aqui):**
`lu2024_fig18_extracao_resultado.md` (figura reproduz Tabela 8 a ±0,002; CSVs
vigentes com erro real +0,0100/+0,0439/+0,0792 em 0,5/1,0/2,0 mm),
`lu2024_fig20_extrai.json` (T10/T16/T22/T28 contra Tabela 9),
`lu2024_redigit_premeasure.json` (adoção SEM re-fit: saldo 0, 5 pioram —
T10 mx 0,331→0,802 —, 2 melhoram; piso σ 0,1030→0,1361),
`lu2024_redigit_premeasure_resultado.md` + adendo 20:2x (pré-requisito 1
satisfeito: a fig14 do P4 tem round-trip com `assert` contra a prosa).

## Escopo

1. **Substituir 7 CSVs** pelo instrumento validado (calibração D-W, off-by-one
   consertado): `fig18_amp0p5`, `fig18_amp1p0` (fora do censo, mas é metade do
   par de piso), `fig18_amp2p0`, `fig20_T10Nm`, `fig20_T16Nm`, `fig20_T22Nm`,
   `fig20_T28Nm`. A `fig18_amp1p5` JÁ é a corrigida (D-W).
2. **As 2 pretas ficam FORA, com motivo declarado AGORA:** `fig18_amp0p25`
   (máscara preta não separável do frame/ticks com o instrumento atual; a curva
   está NO TRIPÉ com o dado vigente — mexer sem instrumento é risco sem tese) e
   `fig20_T4Nm` (JÁ DECLARADA por escopo desde o P5: o próprio paper diz que
   T4 "does not reach the tightening effect"). Gate: ambas bit-idênticas.
3. **Re-fit no MESMO passo** (a constante absorveu a deriva do dado antigo):
   descida coordenada nas **5 alavancas per-rig já adotadas** do grupo único
   `LU_2024` — `k_ratchet`, `loose_arrest_floor`, `c_bend`, `delta_free`,
   `emb_depth` — doses {×0,5 · ×0,75 · 1 · ×1,5 · ×2} (delta_free {−30 % ·
   −15 % · 0 · +15 % · +30 %}), **máx. 2 passadas**, partindo do vigente.
   **Nenhuma constante nova, nenhuma forma nova, nenhum per_case novo.**
   Célula final pela regra de **CENTRALIDADE** (D-AA/D-I): entre as células que
   passam os gates, a de mais vizinhos que também passam; desempate pela pior
   perna. NUNCA por MAE mínimo.
4. **Pisos re-medidos** dos pares declarados (`fig14_*_long × fig18/fig20`,
   janela comum, helper do report) ⇒ `limite_sres(LU)` novo; **re-julgar as
   exceções F7 vigentes do LU** contra o piso novo (cair ⇒ retratação com prova
   preservada, idioma `_EXCECOES_RETRATADAS_*`) e **PROPOR** (não assinar) F7
   das 2 `_long` se e só se as 3 pernas ficarem cobertas pela prova de piso.

## Gates (congelados)

- **G1 instrumento:** cada CSV nova reproduz as âncoras da sua Tabela (8 ou 9)
  a ±0,005 por âncora (medido: ±0,002); grade x conferida contra o off-by-one
  (âncora c1 explícita).
- **G2 isolamento:** re-sim de TODAS as fontes ≠ LU_2024 bit-idêntica
  (Δ = 0 exato em mae/maxerr/resid_std) — as CSVs e o cfg do LU não vazam.
- **G3 censo:** tripé global SÓ cresce; dentro do LU, nenhuma curva hoje no
  tripé (fig18_amp0p25 · amp1p5 · amp2p0) sai dele.
- **G4 pisos/exceções:** piso por par re-medido e publicado; F7 re-julgadas;
  retratação/proposta com as 3 pernas explícitas contra o piso da MESMA
  condição (nunca média da fonte).
- **G5 re-stamp:** fingerprint uniforme nos 210 + guards verdes
  (fp-uniformidade, catraca, anti-envelhecimento) + suíte de validação do LU.
- **G6 procedência:** cada constante re-fitada ganha prov atualizado no mesmo
  commit (catraca não abre par novo).

## Ramos

- **ADOTA** (G1–G6 todos verdes): CSVs + cfg + pisos + docs + re-stamp num
  commit por pathspec (CSVs com `git add -f`).
- **FALHA** (qualquer gate): rollback pelos backups; o resultado vira doc de
  falsificação com os números; as CSVs corrigidas ficam nas extrações
  (arquivos `*_extrai.json`) aguardando decisão do professor.

## Sequenciamento com a sessão paralela

O re-stamp deste pacote NÃO pode sobrepor o da fase 2 do backfill (escritor
único no store). Execução só depois de `git log` mostrar a fase 2 commitada
(ou o working tree limpo de `adopted_configs.json`/store alheios).

---

## RESULTADO da etapa de re-fit (2026-08-13 21:3x, sonda em memória — nada compartilhado escrito)

Grade executada conforme o §3 (descida coordenada, 2 passadas, 5 alavancas ×
5 doses; dados corrigidos servidos em memória pela MESMA construção do
premeasure; configs em sandbox `BAS_ADOPTED_CONFIGS`). Números:
`lu_grid_result.json` (scratchpad da sessão) + log integral.

- **Censo do LU é PLANO em 3** (as três protegidas) numa região ampla que
  INCLUI o ponto vigente: k_ratchet {0,00225–0,006} · floor {0,075–0,15} ·
  c_bend {15–60, linha inteira} · delta_free {0,000238–0,00028} ·
  emb_depth {8e-6}. **Nenhuma dose fecha curva nova.**
- O incumbente da descida ({k_ratchet 0,00225 · floor 0,15 · c_bend 15})
  reduz só a massa de violação (21,73→18,72, −14 %) — seletor que a regra de
  CENTRALIDADE proíbe —, senta na **borda de grade** no c_bend (eixo plano:
  18,72–19,02, o gotcha "empate = inércia") e na beira do floor (0,2 reprova),
  e corrói 3× a margem da protegida `fig18_amp2p0` (mx 0,030→0,096 vs teto
  0,10) enquanto piora `fig18_amp0p5` (0,128→0,154).
- **Veredicto pela regra declarada (centralidade, nunca massa de violação):
  as constantes vigentes FICAM.** O re-fit foi executado e seu resultado é
  "nenhum movimento" — desfecho legítimo da descida.

**O pacote reduz-se a DADO-ONLY:** 7 CSVs corrigidas + pisos honestos
(0,2208 / 0,4143 / 0,1361 — `limite_sres(LU)` 0,1030→0,1361) + F7 re-julgadas
por condição + saldo 0 no censo DECLARADO ANTES (o valor do passo é a
integridade do dado e a honestidade do piso, não censo). Gates G1–G6 seguem
como congelados; G3 lê-se "não encolhe" e as 3 protegidas permanecem OK com
as constantes vigentes (margens intactas). Execução na próxima janela do
escritor do store.

---

## EXECUÇÃO (2026-08-13 ~22:00) — ADOTADO no ramo dado-only; gates 20/20 + 32/32

- **G1**: 20/20 âncoras (c1 exato 0,0000 nas 7; c10/c50/c100 ≤ 0,004 — dentro
  do ±0,005). ⚠️ **A 1ª execução REPROVOU o G1 e o gate estava certo**: 3 das
  7 grades (amp0p5, amp1p0, T16) não têm linha em x=2, então o "c1 da tabela"
  declarado nunca aterrissava nelas — o vão âncora→1º ponto interpolava 0,79
  onde a tabela diz 0,64. Conserto de construção (não de gate): inserir a
  linha (x=2, c1_tabela) onde falta — +1 ponto nas 3, declarado aqui.
- **Execução**: 7 CSVs regravadas (backups `.bkp_luD`); **13 registros LU
  re-simulados no store; fingerprint INTOCADO** (`98f90e11ebb0` único antes e
  depois — dado-only não entra no hash, sem re-stamp global).
- **G2** isolamento por construção (só o LU relido/regravado). **G3**: 3
  protegidas no tripé; censo LU = 3; saldo 0 exatamente como declarado.
- **G4**: pisos por condição re-medidos — 1,0 mm 0,5187/0,8498/0,3044 ·
  0,5 mm 0,2630/0,5779/0,1768 · 0,25 mm 0,0936/0,2012/0,0564; par de
  digitalização T22↔amp1p0 **aperta** 0,0127→0,0078 (as metades corrigidas
  concordam melhor — erravam JUNTAS antes, como medido). `limite_sres(LU)`
  0,1030→**0,1361**. **As 5 provas F7 SOBREVIVEM** (re-numeradas no
  `_F7_EXCECOES` com o dado corrigido; zero retratações). **Proposta nova →
  DECISOES**: `fig14_amp0p5_long` qualifica FORTE (0,1257≤0,1860 ·
  0,3936≤0,4086 · σ 0,1235 já dentro de 0,1361). `fig14_amp1p0_long` **fica
  sem estatuto**: mx 0,8553 excede o piso do par (0,8498) por 0,6 % e a regra
  exige todas as pernas cobertas — é a ÚLTIMA form-limited do projeto.
- **G5**: guards 32/32 (fp-uniformidade + catraca + anti-envelhecimento +
  seção de exceções + export). **G6**: CSVs são dado (não constante) — nada a
  registrar na catraca; procedência do instrumento nos docs de extração.
