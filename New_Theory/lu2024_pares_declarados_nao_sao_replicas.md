# Os 3 "pares de réplica declarados" do `LU_2024` **não se comportam como réplicas**

> # ✅ CONFIRMADO DE FORMA INDEPENDENTE — e a CAUSA veio do artigo, não daqui
>
> **Atualização de 2026-08-14 ~07:05, uma hora depois de escrever este documento.** A sessão
> paralela chegou ao mesmo veredito **pelo caminho que eu não podia percorrer** (ler o
> paper), e já está implementando a correção. Do trabalho em curso dela:
>
> > *"as corridas longas (`fig14_*_long`) são a **§3.1.3 — half-sine**"* ·
> > `"lu2024_M8_fig14_*_long": "protocolo ≠ (**half-sine 1 Hz × manual §3.2**)"`
>
> ⇒ **a causa é PROTOCOLO DE CARREGAMENTO**: a Fig. 14 é half-sine a 1 Hz (§3.1.3) e as
> Figs. 18/20 são o ensaio manual (§3.2). Não são duas medições da mesma coisa; são dois
> ensaios diferentes na mesma amplitude nominal. Isso explica o platô de 27–56 ciclos, as
> durações díspares e a assimetria do modelo — as três evidências deste documento, com uma
> causa só.
>
> Ela está criando `_EXCECOES_RETRATADAS_LU_PROTOCOLO` e movendo as `fig14_*_long` para
> `_SEM_FAMILIA_MECANICA`. ⇒ **a "decisão do professor" que este documento pedia já está
> sendo executada com a resposta certa, e o que eu media como hipótese virou fato.**
>
> **O que este documento retém de valor:** as três evidências foram obtidas **sem o artigo**,
> por medição pura, e concordam com o que o artigo diz. Isso é útil como método — a
> assimetria sistemática 3/3 detectou a diferença de protocolo antes de alguém ler §3.1.3.
>
> ⚠️ **E retém um erro meu que vale mais que o acerto — ver a seção final.**

**2026-08-14** · só-leitura · **nada adotado, nada retratado** · store `55273eab12b0` ·
⚠️ **decisão do professor** — 5 exceções assinadas dependem disto.

## Como cheguei aqui (e o que isso diz do método)

Eu propus a **F8** de manhã, usando o piso de réplica do `LU_2024` para argumentar que a
`fig14_amp0p5_long` é *scatter-bound*, não *form-limited*. Ao atacar em seguida a curva que a
F8 **não** propunha (`amp1p0_long`), abri as trajetórias do par — e o par não fecha.

⇒ **retirei a F8 40 min depois de propô-la.** Este documento é o que sobrou, e vale mais.

## A medida que decide: quanto tempo o dado segura F/F₀ ≥ 0,90

| par (mesma condição nominal, 22 N·m) | `fig14_*_long` | `fig18/20` | razão |
|---|---:|---:|---:|
| 0,25 mm | **27** ciclos | **1** | **27×** |
| 0,5 mm | **27** | **1** | **27×** |
| 1,0 mm | **56** | **1** | **56×** |

**Três pares, três vezes, a mesma direção.** A `fig14` sempre tem um platô inicial; as
`fig18`/`fig20` **nunca** têm.

Trajetórias do par de 1,0 mm, para ver o tamanho da coisa:

| N | 0 | 11 | 21 | 32 | 42 | 53 | 63 | 74 | 95 |
|---|---|---|---|---|---|---|---|---|---|
| `fig14_amp1p0_long` | 1,000 | 0,965 | 0,961 | 0,960 | 0,959 | **0,958** | 0,384 | 0,273 | 0,105 |
| `fig20_T22Nm` | 1,000 | 0,412 | 0,287 | 0,168 | 0,117 | — | — | — | — |

E do par de 0,5 mm, na janela comum, `|A − B|` chega a **0,555**.

## Por que isto NÃO é dispersão de réplica

O contra-argumento legítimo seria: *"o sistema bifurca perto desse ponto (stick × gross
slip), 14 % de diferença no F₀ alcançado basta para virar, e o piso enorme é honesto — a
condição simplesmente não é reprodutível."*

**A bifurcação foi testada e reprovada pelo sinal:** bifurcação **espalha**. Se dois ensaios
nominalmente iguais caem em lados opostos por acaso, o platô apareceria ora de um lado, ora
do outro. Ele aparece **sempre na `fig14`**, em 3 de 3 pares, com fator 27–56×. Isso é
**sistemático**, e sistemático entre duas figuras é diferença **das figuras**, não do ensaio.

**Sinal independente, mesma direção:** as janelas não coincidem —
`fig14_amp0p25_long` vai a **N = 1040** e `fig18_amp0p25` a **N = 99**; a `fig14_amp0p5_long`
a 295 contra 99. São **corridas de duração diferente**. O `csv_x_offset` (0,0 na `fig14`;
1,0 na `fig18/20`, a *"âncora pré-ciclagem plotada em x=1"*) desloca **um** ciclo — não 27.

⚠️ **O que eu NÃO afirmo:** não digo qual figura está "certa", nem o que exatamente difere
(origem do eixo, protocolo, duração, ou o que a figura escolhe plotar). Isso exige o artigo,
e afirmar sem ele seria repetir o erro que este documento corrige. O que está medido é que
**as duas não são intercambiáveis**, e é só disso que o piso depende.

## ✅ O teste aplicado aos OUTROS pares: a maquinaria está sã, o `LU` é o outlier

O mesmo discriminante nos **7** pares declarados, com o `CACCESE` `rep1`/`rep2` — réplicas
pelo próprio nome — servindo de **controle positivo**:

| par declarado | razão `N(<0,90)` A/B | veredito |
|---|---:|---|
| `CACCESE` tapered 45 kN — `rep1` ↔ `rep2` | **1,0×** | ✅ réplicas |
| `LI_2022` 10 Hz — Fig. 8c × 8a (espécimes distintos) | **1,0×** | ✅ |
| `LIU_2016` Fig. 7 — `run1` ↔ `run2` | **1,0×** | ✅ |
| `KARLSEN` M30 HV (F₀ 333 × 313 kN) | **1,3×** | ✅ |
| **`LU_2024` 0,25 mm** | **27×** | ⚠️ |
| **`LU_2024` 0,5 mm** | **27×** | ⚠️ |
| **`LU_2024` 1,0 mm** | **56×** | ⚠️ |

⇒ **isto não é um problema da maquinaria de pisos, é dos 3 pares do `LU`.** Quatro pares
saudáveis a 1,0–1,3× contra três a 27–56× é **contraste**, não gradação — e o
`KARLSEN`, cujo F₀ alcançado difere **6 %** (333 × 313 kN), fica em 1,3×, o que mostra que
diferença de aperto **por si só não produz** a assimetria que o `LU` exibe.

**Consequência boa:** a correção, se houver, é **local**. Os pisos de `CACCESE`, `LI_2022`,
`LIU_2016` e `KARLSEN` — e as exceções que dependem deles — **não** estão implicados por este
achado.

## 🔬 Terceira evidência independente: o MODELO também separa as duas figuras

Se `fig14` e `fig18/20` fossem réplicas, um modelo calibrado teria **o mesmo desempenho** nas
duas. Ele não tem:

| par | MAE na `fig14` | MAE na `fig18/20` | razão |
|---|---:|---:|---:|
| 0,25 mm | 0,1017 | **0,0337** | **3,0×** |
| 0,5 mm | 0,1257 | 0,1259 | 1,0× |
| 1,0 mm | **0,4802** | **0,0520** | **9,2×** |

⚠️ **O caso que fecha:** a `fig18_amp0p25` **passa o tripé** (MAE 0,0337 · res.máx 0,0451 ·
σ 0,0124) e a sua "réplica" `fig14_amp0p25_long` **reprova em 2–5×** (0,1017 / 0,2314 /
0,0367). Um modelo calibrado não é excelente numa curva e ruim na réplica dela.

Três evidências independentes, todas na mesma direção:

1. **o dado** — platô de 27–56 ciclos na `fig14`, ausente nas `fig18/20`, 3 de 3;
2. **as janelas** — durações de 1040 vs 99 ciclos na mesma "condição";
3. **o modelo** — desempenho 3–9× melhor num lado, com uma curva passando o tripé e a
   "réplica" reprovando.

Nenhuma delas depende do artigo. Juntas, a leitura *"são duas medições da mesma coisa"* fica
insustentável.

## O que fica em risco, com número

O piso destes pares é a régua de **5 exceções F7 assinadas**:

| exceção assinada | classe | números registrados na assinatura |
|---|---|---|
| `lu2024_M8_fig18_amp0p5` | FORTE | MAE 0,126/**0,263** · mx 0,180/**0,578** |
| `lu2024_M8_fig20_T10Nm` | PROVA | MAE 0,288/**0,519** · mx 0,802/**0,850** · σ 0,155/**0,304** |
| `lu2024_M8_fig20_T16Nm` | FORTE | MAE 0,173/**0,519** · mx 0,442/**0,850** |
| `lu2024_M8_fig20_T22Nm` | FORTE | MAE 0,052/**0,519** · mx 0,255/**0,850** |
| `lu2024_M8_fig20_T28Nm` | FORTE | MAE 0,110/**0,519** · mx 0,270/**0,850** |

Os denominadores em negrito são os pisos medidos nestes pares.

⚠️ **NÃO as retrato.** Foram assinadas pelo professor; retratação é dele. Registro o número
e o motivo, que é o mesmo padrão de `_EXCECOES_RETRATADAS_LU_PISO_INVALIDO` (julho) e
`_EXCECOES_RETRATADAS_ROUSSEAU_PISO_INVALIDO` (agosto) — nas duas, a campanha retratou
contra si mesma quando o pareamento não se sustentou.

Observação que suaviza parcialmente o risco: a `T22Nm` tem MAE **0,052**, que passaria
folgado contra pisos muito menores; já a `T10Nm` (MAE 0,288, mx 0,802) depende **fortemente**
do piso grande. A exposição não é uniforme entre as cinco.

## Decisão do professor

1. **Manter** os pares e as 5 assinaturas, declarando que o piso do `LU_2024` mede
   *"diferença entre figuras da mesma condição nominal"* — defensável se o artigo mostrar que
   Fig. 14 e Figs. 18/20 são ensaios distintos e ambos válidos; ou
2. **Invalidar** os pares (como já se fez 2×) ⇒ o `LU_2024` volta a ter só a família de
   digitalização, `limite_sres(LU)` cai de 0,136 para ~0,025, e as 5 exceções precisam ser
   re-julgadas — provavelmente com perdas; ou
3. **Ler o artigo** e decidir com o que a Fig. 14 de fato reporta (o único caminho que
   produz resposta em vez de escolha).

Recomendo a **(3)**, e explicito o incentivo contrário para que ele fique visível: a **(1)**
preserva 5 exceções e a **(2)** as ameaça — ou seja, a opção confortável é também a que não
verifica nada.

## ⚠️ HAZARD NOVO, medido na própria execução: **medir um working tree sob edição alheia**

Enquanto eu media, a sessão paralela **editava `report_html.py` no working tree** (mudança
não-commitada). Consequência concreta, nesta sessão:

| grandeza | 06:45 | 07:00 | causa |
|---|---:|---:|---|
| famílias de piso do `LU_2024` | **4** | **1** | os 3 pares declarados foram removidos entre as duas medições |
| `limite_sres(LU_2024)` | 0,1361 | **0,0250** | idem |
| censo pela minha sonda | — | 146 | ⚠️ **e eu reimplementei o censo**, que o protocolo proíbe (o canônico é `_censo()`) |

Passei quase uma hora tratando como **descoberta** o que era, em parte, **a edição do outro
em andamento** — e a minha "medida contrafactual" (*"o que aconteceria se os pares fossem
invalidados"*) estava medindo a **realidade já implementada**, não uma hipótese.

**O que denunciou:** o mesmo helper devolvendo dois números em execuções consecutivas. Número
que muda sem eu mudar nada é sempre instrumento, nunca achado.

⇒ **regras que isto acrescenta:**

1. **Antes de uma campanha de medição, registre o `HEAD` E o `git status` dos módulos que a
   sonda importa.** `git log` não basta: o que a sonda executa é o **working tree**, e ele
   pode estar sujo com trabalho alheio.
2. **Números medidos sobre módulo com `M` no status são provisórios** — não viram documento
   nem proposta sem re-medir num estado limpo.
3. A regra existente *"1 escritor por recurso"* cobria **escrita**. Esta cobre **leitura**:
   *diagnóstico em paralelo* só é seguro quando o **código** está parado, não só o store.
4. **Nunca reimplementar o censo** — eu escrevi minha própria contagem e ela deu 146 contra
   147; o canônico é `_censo()` de `tests/test_meta_numeros_nao_envelhecem.py`. Esta regra já
   existia no charter e eu a violei enquanto citava outras.

## Reprodutibilidade

Vetores `metric_x`/`metric_data` do store `55273eab12b0`; pares de
`report_html._PARES_REPLICA_DECLARADOS`; `csv_x_offset` do `case_registry`. Segundos,
só-leitura.

⚠️ **Os números deste documento foram colhidos com `report_html.py` LIMPO no HEAD `a9541ec`
(medições de 06:45–06:58) — antes da edição em curso da sessão paralela aparecer.** As
trajetórias, razões 27–56× e MAEs vêm do **store**, que não mudou; a tabela de famílias e o
`limite_sres` vêm do **código**, e esses eu re-medi e corrigi acima.
