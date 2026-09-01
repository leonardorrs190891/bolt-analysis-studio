# Rousseau 2025 — execução do prereg (trilhas A e B), 2026-07-28

**Prereg:** `docs/superpowers/specs/2026-07-27-rousseau-prereg.md` (imutável; G0 já
executado em 27/07). **Autorização:** "(a) as duas trilhas" via "autorize esses e
todos os demais". **Baseline:** store `3546e6745448` (pós-adoção chu-test1).

## D1–D4 (diagnóstico obrigatório) — COMPLETO

- **D1 (resíduo assinado):** steel_t10 = crescimento monotônico até +0,188 no
  ÚLTIMO ponto (nível terminal); hdpe_t10/t12 = pico NO MEIO (+0,153 @36 %N,
  +0,138 @62 %N) com finais certos (−0,013/−0,020) — tempo de joelho. Confirma a
  separação das trilhas do prereg, ponto a ponto.
- **D2:** decomposição disponível no `CaseResult.decomp` (canal rotacional vivo no
  aço fino — floor não-inerte, verificado pela própria sonda D3).
- **D3 (direção, 2 pontos antes de bisseção):** tabelas abaixo.
- **D4 (leitura do paper/nota):** amplitudes por espécime confirmadas
  (Tabela 2: 0,5/0,49/0,38 mm; registry roda 0,500 nas 6) + **protocolo de
  condicionamento 0,2 mm × 100 ciclos** citado no texto (nota de aparato).

## Trilha A (steel_t10, arresto terminal) — H-A1 SUSTENTADA nas contas; adoção aguarda G7

O grupo aço herda floor=0,08 do PACK (nunca justificado para o par). Leituras L24
dos rabos: t10 **0,112 plateau=False** (ainda caindo ⇒ floor verdadeiro < 0,112 —
teto, não valor), t12 0,654 False, t14 0,908 True (stick — leitura mis-atribuída,
não usável). Sonda de direção + G3-precheck no grupo inteiro:

| floor grupo | t10 | t12 | t14 |
|---|---|---|---|
| 0,08 (hoje) | 0,087/0,188 | 0,046/0,074 | 0,020/0,034 |
| **0,02** | **0,061/0,096 TRIPÉ** | 0,053/0,081 (+0,007, sob o limite) | **bit-idêntico** (stick ⇒ inerte, predição do prereg ✓) |
| 0,00 | 0,052/0,093 | +0,010 = estoura o limite | bit-idêntico |

- **G5 (transferência):** fit em {t10,t14} ⇒ floor 0,02; t12 previsto zero-refit
  0,0807 vs 0,074 do próprio fit ⇒ Δ+0,007 ≤ +0,02 **PASS**.
- **G6:** o resíduo cai NA POSIÇÃO original (fim): e(fim) +0,188 → +0,076 **PASS**.
- **G2 (trilha A):** steel_t10 entra no tripé **PASS**.
- **Procedência (G4):** `loose_arrest_floor=0,02` fitada-this-rig (1 constante de
  GRUPO, DOF+1), **limitada por cima pela leitura** (0,02 < 0,112) — distinta do
  absorvedor cego do PR-10 pelas duas predições distintivas verificadas (move o
  fim sem mexer no começo; t14 inerte).
- **G7 (adversarial, ≥3 votos tentando refutar):** EM CURSO — 3 verificadores
  independentes lançados (ângulos: doutrina §6 do prereg; física/magnitude vs
  outros floors; precedente PR-10/G-A3 e floors lidos-vs-fitados). **Maioria
  refutando = não adota** (resultado será anexado aqui).

## Trilha B (hdpe_t10/t12, joelho) — puxões OPOSTOS medidos: H-B3 confirmada SEM queimar tentativa

D3 nos dois violadores (mesma alavanca, mesmos valores):

| alavanca | t10 (pico +0,153 @36 %) | t12 (pico +0,138 @62 %) |
|---|---|---|
| N_emb 2 | 0,051/0,133 (pouco) | 0,058/0,120 (pouco) |
| emb 2× | 0,033/0,101 (vira o sinal, −0,101) | 0,051/0,131 (vira, −0,131 @91 %) |
| **CM sharp 0,5** | **0,042/0,089 TRIPÉ** | **0,051/0,151 PIOR, vira p/ −0,151** |
| CM sharp 2,0 | 0,146/0,248 | 0,186/0,349 |

**A alavanca que fecha o t10 QUEBRA o t12 na direção oposta** — com amplitudes de
ensaio quase idênticas (0,50/0,49 mm, Tabela 2). Não é input: é **scatter de
espécime no tempo de joelho**, exatamente a H-B3. Pela regra §4.45 (contas de
satisfazibilidade RODADAS antes de prereg/tentativa), **nenhuma das 2 tentativas
formais da trilha B foi queimada** — o desfecho previsto pelo próprio prereg
("FAIL2 em B ⇒ exceção por amplitude/espécime com a Tabela 2 como prova") foi
alcançado por medição direta, mais forte que a via de 2 FAILs: **a recusa está
medida par-a-par, alavanca-a-alavanca.** Os 2 HDPE entram na proposta F6.

## Custos e não-feitos

- Nada adotado ainda (trilha A aguarda G7 + batch de re-stamp próprio).
- H-A2 (self-locking em F₀) não sondada — o H-A1 fechou nas contas com predições
  distintivas confirmadas; H-A2 fica registrada como alternativa não-testada.
- Amplitudes por espécime (0,49/0,38) seguem NÃO aplicadas no registry — em t12 o
  Δ é 2 %, em t14 o stick persiste; correção de input de baixo efeito, candidata
  a carona no próximo re-stamp com procedência Tabela 2.
