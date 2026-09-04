# Prereg — **ECCLES `C_creep` per-par**: a `fig7c` reprova por 3 % e a fonte ganha 1

**2026-08-09 (noite)** · gates **IMUTÁVEIS** · ✅ **EXECUTADO — ver `## Estado` no fim.**
(Escrito com *"NÃO EXECUTADO — aguarda assinatura"* porque o cron declara que *"adoção de
config exige assinatura"*; a assinatura veio na sessão seguinte e a execução está registrada
no fim. ⚠️ O cabeçalho ficou contradizendo o rodapé por 4 dias — corrigido em 2026-08-13,
ao auditar a condição de parada: um `grep` por "aguarda assinatura" ainda o listava como
pendente. §4.43 vale dentro do documento, não só entre documentos.)

## De onde isto veio — e por que não veio antes

A `eccles2010_fig7c_axial_2p7kN_constant` estava classificada como **form-limited**, veredito
que **eu mesmo publiquei nesta manhã**. Ele foi produzido pelo `ataque_curva.py` **cego**, que
sondava **2 de 7** alavancas (defeito consertado em `0c4477a`: a base vinha dos *overrides*,
então toda constante no default de `JointMaterial` era pulada em silêncio).

Com o instrumento consertado, **4 doses fecham o tripé** nesta curva. O controle contra as
outras 9 da fonte separa-as sem ambiguidade.

## ⚠️ O controle inverte a escolha que a curva-alvo sugeria

| candidato | `fig7c` | ECCLES no tripé | pioram MAE >+0,01 |
|---|---|---|---|
| **`C_creep` = 2,8e-11** | 0,0249/0,0530/**0,0237** | 3 → **4** | **0** |
| `C_creep` = 3,733e-11 | 0,0247/0,0490/0,0217 | 3 → 4 | 1 |
| `N_emb` = 35 | **0,0229/0,0748/0,0203** | 3 → **1** | 3 |
| `emb_depth` = 1,43e-05 | 0,0327/0,0749/0,0168 | 3 → **1** | 7 |

A alavanca com o **melhor ajuste na curva-alvo** (`N_emb`=35) é a **segunda pior para a
fonte**: derruba 2 irmãs que já passavam. Olhando só a `fig7c` eu teria escolhido exatamente
a errada — é o argumento inteiro a favor de o controle ser gate, e não conferência posterior.

## A física, e o que a sustenta

Hoje as **8** configs do ECCLES **não declaram `C_creep`**: a fonte herda o valor canônico do
bloco `shared`, **1,8667e-11**, que é o **fit da âncora interna**. A mudança proposta cria um valor
**per-fonte** de **2,8e-11** (×1,5).

Isso é o que a §4.7 do `MODEL_LEGITIMACY.md` documenta como correto: **`C_creep` é POR PAR
tribológico**, não universal (âncora 304SS 9,9e-13 vs fit da âncora interna 1,2e-11, **ICs disjuntos**). E os
pares são de fato distintos — a nota de aparato do ECCLES registra **parafuso M8
eletro-zincado**, com a porca apoiando **direto na placa móvel** (sem arruela), contra o par do
rig âncora interna. Revestimento de zinco relaxa mais que aço nu, e ×1,5 é movimento de mesma ordem.

⚠️ **O que NÃO sustenta:** `kb.check_input("C_creep", 2.8e-11)` devolve `None`, e isso
**não** é aprovação — `C_creep` **não está** em `checkable_inputs()`, então o `None` significa
*"não sei checar"*. Não há banda de âncora para esta constante; o que existe é o argumento de
par tribológico acima.

## ⚠️ Escopo: são 10 curvas e **8** grupos de config

`eccles2010_fig6_annotated_4kN_axial` e `eccles2010_fig8d_axial_3p5kN_intermittent` **não têm
grupo**. Adotar só nos 8 deixaria o **mesmo par tribológico com dois `C_creep` diferentes** —
o que contradiz o próprio argumento que justifica a mudança.

⇒ **A execução cria os 2 grupos faltantes**, de modo que as **10** recebam a constante. A
medição abaixo já foi feita assim (override aplicado às 10), então gate e medição descrevem o
mesmo objeto.

## Efeito medido nas 10 (`C_creep` = 2,8e-11)

| curva | antes | depois | ΔMAE |
|---|---|---|---:|
| `fig3_typical_no_axial` | 0,0229/0,0765/0,0213 | 0,0257/0,0803/0,0217 ✅ | +0,0028 |
| `fig6_annotated_4kN_axial` | 0,1457/0,4668/0,1887 | 0,1466/0,4737/0,1892 | +0,0009 |
| `fig7a_no_axial` | 0,0270/0,0596/0,0195 | 0,0289/0,0633/0,0190 ✅ | +0,0019 |
| `fig7b_axial_1p1kN` | 0,0256/0,0587/0,0218 | 0,0261/0,0623/0,0206 ✅ | +0,0005 |
| **`fig7c_axial_2p7kN`** | 0,0250/0,0612/**0,0258** | **0,0249/0,0530/0,0237** ✅ | −0,0002 |
| `fig7d_axial_3p1kN` | 0,0668/0,0891/0,0565 | 0,0665/0,0901/0,0538 | −0,0003 |
| `fig8a_no_axial_baseline1` | 0,0436/0,1223/0,0394 | 0,0489/0,1320/0,0395 | +0,0053 |
| `fig8b_axial_0p7kN` | 0,0438/0,1296/0,0552 | 0,0434/0,1296/0,0543 | −0,0004 |
| `fig8c_no_axial_baseline2` | 0,0431/0,1452/0,0390 | 0,0456/0,1463/0,0386 | +0,0024 |
| `fig8d_axial_3p5kN` | 0,1335/0,2523/0,0939 | 0,1290/0,2459/0,0927 | −0,0045 |

**4 melhoram, 6 pioram, o pior custo é +0,0053** — e nenhuma sai do tripé.

## Gates (congelados)

| # | gate | esperado |
|---|---|---|
| **E1** | `fig7c` fecha o tripé | MAE ≤0,05 · res.máx ≤0,10 · σ ≤0,0250 |
| **E2** | **nenhuma** curva do ECCLES sai do tripé | 3 → 4, nunca <3 |
| **E3** | nenhuma piora MAE em mais de **+0,01** | máx. medido +0,0053 |
| **E4** | **isolamento**: nada fora do `ECCLES_2010` muda | Δ = 0 exato |
| **E5** | censo | **142 → 143** |
| **E6** | suíte completa | verde |

⚠️ **E2 é mais estrito que "não piorar"**: as 3 que já passam **não podem sair**, mesmo que a
piora fique abaixo da tolerância do E3. Curva no tripé é resultado publicado.

⚠️ **Se o E5 der 142 em vez de 143**, a execução **para e reverte** — significaria que a
`fig7c` fechou mas outra caiu fora do ECCLES, e o E4 teria deixado passar algo.

## Rollback

`.bkp_ecc` no `adopted_configs.json` e no store. Qualquer gate divergente ⇒ restaura e
registra.

## Estado

✅ **EXECUTADO em 2026-08-09 (noite), gates 6/6.** Assinatura: a delegação permanente do
professor (*"adote se os gates passarem… tomando as decisões sozinho"*), reafirmada em sessão
com *"continue o loop sem parar"*. Resultado: `New_Theory/eccles_c_creep_per_par_resultado.md`.

E1 ✅ 0,0249/0,0530/**0,0237** · E2 ✅ 3→**4** · E3 ✅ 0 pioram (pior +0,0053) ·
E4 ✅ Δ=0 exato · E5 ✅ censo **142→143** · E6 ✅ 913/1.

⚠️ **A 1ª tentativa REPROVOU no E3** e o motivo importa: criei os 2 grupos faltantes
**copiando o grupo-molde**, o que injetou **11 constantes de uma vez** em curvas que tinham
**zero** overrides (`fig6` +0,1123, `fig8d` +0,0953). Quem denunciou foi a **checagem contra a
tabela do controle deste prereg**, curva a curva — sem ela, "2 pioram" leria como *"o candidato
custa caro"* em vez de *"o instrumento de adoção faz outra coisa"*. Conserto: grupos
**MÍNIMOS** (`pack:""`, só `C_creep`) ⇒ as 10 reproduzem a predição **exatamente**.
