# O MÉTODO DA LEITURA DE CONSTANTES — consolidação do arco 2026-08-19/20 (censo 143 → 166)

**2026-08-20 (22:4x)** · material de artigo (item 7 do mapa de melhorias,
mandato "o que podemos fazer para melhorar?"). Vinte e três curvas fecharam o
tripé em ~36 h pela MESMA estrutura metodológica; este documento a nomeia,
enumera as instâncias com procedência, e destila as regras que nasceram no
caminho. Nada aqui é novo — tudo está nos preregs/resultados citados; isto é a
síntese que o artigo precisa.

## 1. A tese

> **Uma curva fecha quando a forma certa recebe constantes com procedência de
> LEITURA — extraídas de observáveis publicados da própria fonte — em vez de
> fitadas à métrica.** Onde a leitura é possível, o fecho é rápido e robusto;
> onde ela é impossível, o fit puro é recusado e a curva recebe estatuto
> honesto. A fronteira entre os dois casos é ela própria medida.

A hierarquia de procedência praticada, da mais forte à mais fraca:

1. **LIDO direto** — o número está impresso (terminal de tabela, demarcação
   desenhada, definição do protocolo). Ex.: floors do LU (Tabela 9),
   N_onset=161 da fig3 (linha desenhada), frac=0,25 (o paper define o fim do
   Estágio II em P=25 %).
2. **LIDO por leitor canônico** — um algoritmo público extrai o número do dado
   cru (`arrest_floor_from_curve`, `emb_from_curve`), com o *bias* declarado
   (plateau=False ⇒ limite inferior).
3. **REGREDIDO** — LSQ de uma lei fechada a um observável publicado, com r²
   reportado e critério explícito: **r² ≥ ~0,65 e o valor dentro da região que
   fecha ⇒ leitura** (amp1p5: aexp=1,864, r²=0,685); **r² < 0,6 ⇒ a regressão
   NÃO suporta leitura** e vira tentativa registrada (T28: 0,863/0,515).
4. **ANCORADO** — fitado numa grade mas validado contra um observável (emb da
   T16: o modelo reproduz o 1º ciclo digitalizado a 1 %).
5. **FITADO-DECLARADO** — sem âncora; aceito apenas com região interior
   comprovada (não fio de navalha), rótulo honesto no `prov`, e contagem de
   DOF no ledger. Degenerescências (alvo↔relógio, floor↔aexp, scrit↔k)
   DECLARADAS — o par degenerado conta como ~1 parâmetro efetivo.

## 2. As instâncias (23 fechamentos + 1 caso didático)

| # | curva(s) | constante(s) e procedência | resultado |
|---|---|---|---|
| 1–2 | SUN standard (2 passos) | kernel cinemático + floor LIDO (leitor, plateau=False) + C_creep do token da própria fonte | σ 4,73×→0,89× |
| 3 | LU T10 | lei de pressão MEDIDA na fonte (r=+0,995) + floor LIDO do terminal publicado (0,309→lido 0,3195, 3,4 %) | 0,2514→0,0198 |
| 4–7 | ROUSSEAU ×4 | traços θ das Figs. 4/5: dF/dθ regredido (r² 0,9997) ⇒ free_spin_kin; taxa regredida (Hill×arrest, r²=0,891) | fonte 8/8 |
| 8–12 | ICMEZ ×5 | caracterização de dreno dos AUTORES (Fig. 3) + settling lido do intercepto | fonte 8/8 |
| 13–15 | YANG_2023 ×3 | P-13: lei fracionária com (fe,K) por LSQ da solução fechada ao F publicado (r² 0,997–0,9999) | 3 fecham |
| 16 | YANG_2019 amp0p4 | pacote gth LIDO do próprio dado + causa-raiz do gate de grupo + trim §B | 5/5 na fonte |
| 17 | LU T28 | floor LIDO do terminal publicado (0,234, 3,2 %) + aexp fitado-declarado (regressão tentada e recusada) | 0,1008→0,0338 |
| 18 | IJPEM 0_45 | o "colapso" era PASSO DE AMOSTRAGEM — closed-form P-13 cruza os pontos crus a 0,011 | 0,1042→0,0102 |
| 19 | LU amp1p5 | aexp **REGREDIDO do dado** (1,864, r²=0,685, dentro da região que fecha) — floor lido FALSIFICADO antes | 0,0314→0,0139 |
| 20 | BAUER test1 | transição de fração do espectro (física do PRÓPRIO paper, p.8) — limiar ligado, s_crit por espécime | 0,0745→0,0305 |
| 21 | BAUER test2 | idem (região 4/4 vizinhos) — exceção retirada por mérito | 0,0290→0,0149 |
| 22 | LU T16 | floor LIDO (terminal 0,187, 4,3 %) + emb ANCORADO no 1º ciclo (1 %) — errata do diagnóstico "meio-de-rampa" | 0,1572→0,0226 |
| 23 | YANG_2023_AME (CFRP) | embedment LENTO nomeado pelos AUTORES (nota G8); taxa regredida do cru (r²=0,92); degenerescência declarada | 0,3875→0,0285 |
| (didático) | zhang2006_fig3 | traço θ DIGITALIZADO (826 cols) ⇒ lei de taxa lida (fe 5,80 ≡ 5,93 de 2 regressões independentes); forma runaway construída; segue DECLARADA (proveniência) | 0,2110→0,0320 |

## 3. As recusas — tão importantes quanto os fechos

- **bauer test3**: melhor célula com **0/4 vizinhos** (navalha medida; 3
  células diagonais = degenerescência) — RECUSADO. O gate anti-navalha
  existe para isto.
- **fig3 como censo**: mesmo com leitura plena, σ satura 1,4–1,56× — a
  declaração de proveniência fica, agora sustentada por "forma faltante
  medida", a versão mais forte do argumento.
- **runaway frac=0,75 no bauer**: o boost lido do joelho PIORA muito — o
  bauer é transição gradual, não bifurcação. Forma certa ≠ forma parecida.
- **fit por curva sem observável** (fig14_long, yang2021): recusado pelo
  item D; as curvas ficam com estatuto honesto (scatter/forma faltante).

## 4. Regras que nasceram no arco (todas com instância citável)

1. **Regra da regressão** (§ do doc de rotas): r²≥0,65 + valor na região ⇒
   leitura; r²<0,6 ⇒ fitado-declarado com a tentativa registrada.
2. **Quando há âncora, a âncora manda** sobre a centralidade (emb da T16:
   4,0 µm casa o c1; a célula central era 4,5).
3. **Releitura de resíduo antes de citar diagnóstico antigo** — 3 erratas de
   mapa num dia (T16 "meio-de-rampa" era 1º ciclo; fig3 "4 atos" eram 2
   estágios; yang2023ame "falta viscoelástico" era emb default do modelo).
4. **O limite é o helper, nunca reimplementado** — 2ª e 3ª ocorrências do
   erro no mesmo dia (σ 0,025 fixo vs `limite_sres` por fonte no BAUER).
5. **Ler o CRU, nunca `metric_data`** para cauda/onset/floor (FLOOR_TRIM).
6. **Grupo nasce mínimo** (D-AB) e **token per_case não pode colidir**.
7. **Degenerescência declarada** conta como ~1 DOF (alvo↔relógio, scrit↔k).
8. **A física do próprio autor primeiro** — 4 dos fechos usam o mecanismo
   NOMEADO no paper (BAUER p.8; AME nota G8; ICMEZ Fig. 3; LU Tabela 9).

## 5. O que isto significa para o artigo

- A validação não é "o modelo fita 166 curvas": é "**166 curvas fecham com
  constantes cuja origem está documentada uma a uma**, e as 39 restantes têm
  estatuto medido (22 exceções com prova, 12 declaradas com critério, 5 em
  teto duro nomeado)".
- O material das exceções (decisão do professor: exceções viram artigo) ganha
  o complemento: **as retiradas** — **7** exceções/declarações saíram POR MÉRITO
  em 2 dias (T22, T28, amp1p5, 0_45, test2, T16, yang2023ame), provando que
  os estatutos não são lixeira: são fila de espera com porta de saída.

  > ✅ **Contagem VERIFICADA em 2026-08-20 (22:5x)** contra o store `245dc93087d1`
  > (a prosa dizia **6** e a própria parêntese listava **7** — a lista estava certa).
  > Confirmado por **duas checagens independentes**, porque estar no tripé hoje não
  > prova que havia estatuto ontem:
  >
  > 1. **`_tripe_ok` = True e ausente de `_EXCECOES` e `_DECLARADAS`** nos 7;
  > 2. **cada um aparece numa lista de retirada** — 5 em
  >    `_DECLARACOES_RETIRADAS_FECHAM_POR_ADOCAO` (T28 · amp1p5 · 0_45 · T16 ·
  >    yang2023ame), a **T22** em `_DECLARACOES_RETIRADAS_PICO_ESPURIO` (o `CLAUDE.md`
  >    registra *"a `T22Nm` fecha por mérito ao sair o artefato"*) e o **test2** em
  >    `_EXCECOES_RETIRADAS_BAUER_SCRIT`.
  >
  > ⚠️ **Ambiguidade de nome resolvida por medição:** *"test2"* casa **três** curvas no
  > store. A que saiu por mérito é a `bauer2024_M12_fig8_test2` (coerente com a adoção
  > `BAUER_SCRIT` do mesmo dia); a `chu2026ti_D0p4mm_F0_49kN_test2` **segue exceção
  > ativa** e não deve ser lida nesta lista. Apelido curto em material de artigo
  > precisa do `case_id` ao lado quando o sufixo é reutilizado entre fontes.
- Benchmark externo direto: a Fig. 8 do Bauer traz as curvas CALCULADAS do
  método do próprio autor (P10/P50/P90) — comparação método-a-método
  disponível sem trabalho novo de dado.
