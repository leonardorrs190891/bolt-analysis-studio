# σ_res: onde ele mora ao longo da curva — decomposição por estágio

**Medido em 2026-07-29** · store `3546e6745448` · 202 comparáveis · régua de três
pernas (`res.máx ≤ 0,10` E `MAE ≤ 0,05` E `σ_res ≤ 0,025`).
Sem re-simulação: lê os vetores `metric_x`/`metric_pred`/`metric_data` que o
runner já gravou — **os mesmos três que a métrica comparou**, nunca `ratio`
reinterpolado (defeito de 2026-07-27).

## Por que esta medição existe

O σ_res é a perna que **manda em 87 das 98 curvas fora** (89 %). Uma varredura
de sensibilidade das **18 alavancas** do modelo não fechou essa perna em
nenhuma. A conclusão natural — "falta uma alavanca" — é a errada: antes de
procurar a 19ª, vale perguntar **onde**, ao longo do ensaio, o resíduo varia.
σ_res é uma estatística de *forma*, não de nível; a informação de forma está nos
vetores e ninguém tinha olhado.

## O instrumento: lei da variância total

Com os estágios I (0–10 % dos ciclos), II (10–70 %) e III (70–100 %), e
`w_k = n_k/n`:

```
σ_res²  =  Σ w_k · σ_k²        +        Σ w_k · (μ_k − μ)²
           └── DENTRO ──┘                └──── ENTRE ────┘
        oscilação local              deslocamento de nível
        (forma dentro do trecho)     entre trechos do ensaio
```

A partição é exata (identidade, não aproximação). A leitura:

* **DENTRO** grande ⇒ o resíduo oscila dentro do trecho — ruído/forma local.
* **ENTRE** grande ⇒ o modelo acerta um trecho e erra outro: a **distribuição da
  perda ao longo do ensaio** está errada, mesmo que o total esteja certo.

## Resultado

**84 curvas** (das 87 em que o σ_res manda; 3 saem por não terem os 3 estágios
com ao menos um ponto ou < 6 pontos na janela da métrica).

| termo | mediana | p25–p75 |
|---|---|---|
| **ENTRE estágios** (nível/forma) | **59,7 %** | 46–76 % |
| DENTRO dos estágios (oscilação) | 40,3 % | 24–54 % |

Sobre o conjunto inteiro (**195** curvas com os três estágios preenchidos) a razão
é 55,3 % / 44,7 % — a concentração no termo ENTRE **aumenta** justamente onde o
σ_res reprova.

### E o termo ENTRE é curvatura, não deriva de taxa

Olhando o **sinal** da média do resíduo em cada estágio:

| padrão | curvas | leitura |
|---|---|---|
| **troca de sinal** entre estágios | **53 de 84 (63 %)** | o modelo **cruza** o dado: está acima num trecho e abaixo em outro ⇒ **curvatura errada** |
| média monótona nos 3 estágios | 30 de 84 (36 %) | compatível com deriva de **taxa** |
| monótona **e sem** troca de sinal (taxa pura) | **11 de 84** | só aqui "errar a taxa" descreve o defeito |
| troca de sinal **e** não-monótona (curvatura pura) | 34 de 84 | |

Padrões mais comuns (I,II,III): `---` não-monótono (16), `--+` (10), `-++`
monótono (8), `++-` (8), `+--` (8), `+++` (6).

## O que isto quer dizer — e por que 18 alavancas falharam

O defeito dominante **não é de magnitude, é de distribuição no tempo**: em 63 %
das curvas que o σ_res reprova, o resíduo troca de sinal ao longo do ensaio.
Uma alavanca que **escala** um mecanismo (qualquer `k_*`, `C_creep`,
`K_archard`, `emb_depth`…) move o resíduo **para cima ou para baixo em bloco** —
muda o nível, e portanto o MAE e o viés. Ela **não muda onde o resíduo cruza
zero**. Logo:

> Nenhuma alavanca de escala pode fechar a perna do σ_res em 63 % das curvas em
> que ela manda. Isso não é falha da varredura das 18 — é consequência
> algébrica do que uma alavanca de escala faz.

O que moveria: uma forma cuja **taxa dependa do estado acumulado**, redistribuindo
a perda entre os estágios em vez de reescalá-la. Os candidatos já nomeados na
fila do professor são exatamente dessa classe — **limiar graduado**
(`graded_scrit`, já existe default-inerte no engine), **kernel desacelerante**,
**bifurcação de limiar**. Esta medição diz que a classe está certa; não diz qual.

## Segunda passada: POR QUAL CANAL a curvatura entra

A leitura acima diz que a classe de forma certa é *taxa dependente do estado
acumulado*. O candidato nomeado na fila — **`graded_scrit`** (já no engine,
default-inerte) — modula **só o canal de afrouxamento rotacional**. E este repo
já registrou que alavancas desse tipo são **inertes onde o canal que elas gateiam
carrega ~0 da perda** (a classe `channel_gated_levers` da `knowledge_base`). Logo
"a classe está certa" **não** implica "este candidato serve": faltava verificar
quanto da perda passa pelo canal, curva por curva.

Verificado (2026-07-29, sobre a decomposição por mecanismo do store, fração da
perda no ciclo final):

**Das 53 que trocam de sinal, o canal de afrouxamento está VIVO (>5 %) em 35 e
MORTO (≤5 %) em 18.** Mediana da fração no canal: **46,5 %** (p25 1,6 % · p75
71,5 %) — isto é, a distribuição é bimodal, não centrada.

| sub-população | n | canal que carrega a perda | forma que faria falta |
|---|---:|---|---|
| loosening vivo | **35** | rotacional domina em 24, embedding em 10, wear em 1 | **`graded_scrit`** é candidato plausível |
| loosening morto | **18** | **wear 8** · **embedding 5** · **creep 5** | taxa dependente de estado **nesses** canais — `graded_scrit` é **inerte aqui, para qualquer valor de parâmetro** |

Onde ele está morto, os casos são limpos e agrupados por fonte — o que sugere
mecanismo, não acidente:

* **embedding a 100 %** — `zhang18_fig2_test4`, `fig13`, `fig16`;
  `liu2022_fig8_multi_t4` a 80 %;
* **creep a ~90–100 %** — `caccese2009_retighten_19p1mm`, `caccese2009_tapered_45kN_rep2`,
  e as três do `JCSR_2023` (`plain/galv/stainless_seawater`, 89–93 %);
* **wear a ~76–79 %** — `CHU_2026` (`D0p7mm_F0_49kN_test4`, `D0p4mm_F0_61kN_test7`,
  `D0p4mm_F0_73kN_test8`).

### Consequência para a fila

O que era "uma decisão de forma" são **pelo menos duas**, e a segunda tem alvo
declarado: uma taxa dependente do estado em **embedding/creep/wear**, não no
afrouxamento. Atacar só o `graded_scrit` deixa **18 das 53** intocadas por
construção — e entre elas estão as 3 do `JCSR_2023`, que é justamente a fonte de
piso mais alto (0,2214 = 8,9× o limite global), onde a perna talvez nem devesse
ser cobrada (ver o prereg do piso por fonte).

## O que NÃO está medido aqui (limites declarados)

* Não há teste de **qual** forma fecha a perna — só de qual **classe** poderia.
  Escolher exige prereg com gates, por fonte.
* A partição por estágio usa as fronteiras 10 %/70 % de `_stage_maes`, que são
  **convenção do report**, não física. As curvas com joelho fora dessa janela
  têm o termo ENTRE inflado por artefato de recorte; não medi essa
  sensibilidade.
* Não separa **erro de digitalização** de erro de modelo. O piso medido de σ por
  fonte (0,0283 mediano, até **0,2214** no JCSR_2023) cobre parte do termo
  DENTRO — e é por isso que a perna precisa de limite por fonte
  (`sigma_res_por_fonte_prereg.md`).
* 3 das 87 curvas ficaram fora por amostragem, e **não** foram substituídas por
  estimativa.
* ⚠️ **CORRIGIDO por medição em 2026-07-29 (noite, sessão paralela): a fração no canal
  NÃO decide a inércia de uma alavanca de *lei de taxa*.** A tabela acima classifica
  `CHU_2026 test7`/`test8` como "loosening morto ⇒ `graded_scrit` inerte para qualquer
  valor de parâmetro". A sonda direta no engine mede o oposto: em `test8` o canal
  rotacional vai de **0,0120 → 0,1619 kN** (2,3 % → 25 % da perda, **13×**) ao ligar a
  alavanca, e **88 %** de todo o movimento vem do próprio canal — não de realimentação.
  As três pernas melhoram (σ 0,1924→0,1638; res.máx 0,3456→0,2382). Motivo do engano:
  uma alavanca que **multiplica** um canal (`loose_arrest_floor`, `eta_loose`) está
  limitada pela fatia dele; uma que **substitui a lei de taxa** não está — mudar a lei é
  o que muda a fatia. A fração é atribuição *a posteriori* de uma parametrização, não
  cota de capacidade. ⇒ 2 das 18 saem da lista de "intocáveis por construção"; a
  conclusão maior (**são pelo menos duas decisões de forma**, alvo em
  embedding/creep/wear) **fica de pé**. Detalhe e tabela:
  `chu_segundo_defeito_resultado.md` §6.
* **O roteamento por canal diz onde a perda passa, NÃO que uma forma conserta.**
  Ninguém ligou `graded_scrit` e mediu o σ_res depois. Não medi de propósito:
  `s_crit_loose` é **per-rig com procedência** (Bauer 76–108 µm, curva
  amplitude-vs-vida) e varrer o valor até o σ_res cair é **fitar**, que é o que
  esta campanha evita. Testar a forma exige prereg com âncora para o limiar, por
  fonte — não uma varredura.
* A fração no canal é lida no **ciclo final** da decomposição. Uma curva pode ter
  o canal morto no fim e vivo no meio; não medi a fração ao longo do ensaio, e
  para a pergunta "qual forma redistribui a perda no tempo" essa seria a leitura
  mais fina.

## Reprodução

```bash
py -3.12 New_Theory/sigma_res_stage_probe.py
```
