# Chave de pareamento ESTENDIDA — ITEM X executado, 2026-08-23

**Assinado pelo professor** ("assinado", sobre o ITEM X). Prereg:
`docs/superpowers/specs/2026-08-23-chave-estendida-pareamento-prereg.md` —
**8 gates verdes, G6 reprova como escrito** (o gate estava mal especificado; §5 explica).

**Nada de engine, config, store ou fingerprint.** O piso é recomputado na geração do
report a partir dos vetores que o store já tem — zero re-simulação, zero re-carimbo.

---

## 1. O que mudou, em duas linhas

A chave de família de réplicas passou de `(fonte, δ, F_amp, mode)` para incluir os **8
campos de input** que os papers varrem (`_CAMPOS_VARRIDOS`). E as **67 de 81** curvas da
lista manual `_SEM_FAMILIA_MECANICA` cujas fontes a chave já distingue deixaram de ser
bloqueadas — o bloqueio virou **supersedido por mecanismo**, não apagado.

## 2. O número que justifica tudo

Antes deste trabalho o `ECCLES_2010` rodava com barra de σ_res **0,0698**. Medido agora, em
três estados:

| estado da chave | piso σ do ECCLES | barra `limite_sres` |
|---|---:|---:|
| **cega** (só δ/F_amp/mode, sem lista) | **0,0852** | 0,0852 |
| lista manual + par declarado (até hoje) | 0,0698 | 0,0698 |
| **chave estendida** (agora) | **0,0565** | **0,0565** |

⇒ **a cegueira à variável varrida INFLAVA a barra em 51 %** (0,0565 → 0,0852). E barra
inflada não reprova nada: ela **aprova**. É por isso que o teste central desta entrega não
conta famílias — ele proíbe qualquer piso de subir (`test_nenhum_limite_afrouxa`).

O caminho é o mesmo dos sete casos de retratação: um piso que mede *dispersão entre
condições diferentes* é grande, e quanto maior o piso, mais fácil passar. O defeito
premiava a si mesmo.

## 3. Resultado dos gates

| gate | veredito |
|---|---|
| **G1** nenhuma exceção perde estatuto | ✅ as **21** seguem; as 2 provas de piso do ECCLES sobrevivem, ambas **PROVA** |
| **G2** censo | ✅ **tripé 169/205**, `declarado_total` **201** — idêntico ao baseline |
| **G3** nenhum limite afrouxa | ✅ zero sobem; ECCLES **aperta** 0,0698 → 0,0565 |
| **G4** pares declarados | ✅ **5 de 5** seguem formando família |
| **G5** pareamentos corretos | ✅ **6 de 6** |
| **G5b** variável varrida separada | ✅ **5 de 5** |
| **G6** isolamento | ❌ **reprova como escrito** — §5 |
| **G7** provas re-sincronizadas | ✅ `test_provas_de_excecao_nao_envelhecem` verde |
| **G8** suíte | ✅ **1129 passed / 1 skipped** (1112 do baseline + 17 da guarda nova) |
| **G9** tickets bloqueados | ✅ **14** curvas permanecem |

**As 4 predições registradas antes de executar bateram ao 4º decimal**, inclusive as duas
que previam *ausência* de piso. A sonda de monkeypatch e a implementação real concordam ⇒
o instrumento estava medindo o que dizia medir.

## 4. A margem de 4e-6 que foi consumida — e por que a exceção sobreviveu

A prova de piso da `eccles fig8a` passava a barra **FORTE** do res.máx **por 4e-6**, e a
própria prova, escrita em 2026-08-15, declarava: *"margem que não sobrevive a
arredondamento — o veredito é estável, o grau não."*

Com o piso apertado a barra FORTE caiu de 0,1320 para **0,1091**, e 0,1320 > 0,1091 ⇒ a
perna do res.máx **caiu de FORTE para PROVA**. A exceção **sobrevive** porque o veredito
já era PROVA: a perna mais fraca governa.

⚠️ **Se alguém tivesse assinado FORTE ali, esta re-medição a derrubaria.** A prudência de
08-15 — recusar o grau que os números permitiam, por causa de uma margem de 4e-6 — é o que
salva a adoção de hoje. Vale registrar como precedente: **grau conservador não é
timidez, é o que permite apertar o denominador depois.**

A folga da perna que decide, na `fig8c`, caiu de 0,0403 para **0,0080**. As duas provas
seguem válidas, e mais apertadas.

## 5. O gate que reprovou — e o que ele ensina

**G6** exigia piso **bit-idêntico** em fontes sem curva no bloqueio. Violam-no
`GRZEJDA_2026` e `SUN_2025_REASSY`.

**O gate estava mal especificado, não a mudança.** Ele proíbe a chave de agir fora da
lista de bloqueio — o que **contradiz o §1(a) do próprio prereg**, onde a chave é global
por construção. Eu escrevi um gate que testa o oposto do que o documento declara mudar.

**Não reescrevi o gate.** Mover a trave depois de ver o resultado é o que a disciplina
proíbe. O dano medido:

- as duas fontes **perdem o piso inteiro** porque suas "famílias" nunca foram famílias —
  `bolt1_base`×`bolt6_central` é **posição no flange**, `reassy02..10` é **número de
  remontagens**;
- **nenhuma exceção assinada** vive nelas;
- os dois pisos já estavam **abaixo** de `META_SRES` ⇒ o `max()` os ignorava, e o limite
  segue **0,0250** nas duas.

**Efeito real na régua: zero.** O gate certo — proposto, não retroativo — é *"nenhuma
fonte muda de piso sem que a mudança seja atribuível a um campo de `_CAMPOS_VARRIDOS` que
a fonte de fato varre"*. As duas violações passariam por ele **com atribuição nomeada**.

## 6. O que NÃO foi feito, e por quê

**14 curvas seguem bloqueadas à mão** — `KARLSEN_2022` (dispositivo de travamento),
`LI_2022_MARSTRUC` (pré-carga) e `LI_2022_TRIBOINT` (frequência). O registry **tem** os
três campos; a chave ainda não os lê. Não é esquecimento: `frequency_Hz` e
`initial_preload_N` entrariam na chave de **toda** fonte, não só destas três, e mudariam
pareamento onde ele hoje está **certo**. É passo separado, com gate de isolamento próprio.

## 7. A guarda, validada por perturbação

`tests/test_chave_estendida_pareamento.py` — **17 testes**. Não basta que passem; foram
validados quebrando o mecanismo de propósito:

| perturbação | o que a guarda fez |
|---|---|
| tirar `grip_length_mm` da chave | ICMEZ 13,8 × 19,8 mm volta a **parear** ⇒ reprova |
| tirar `external_axial_N` da chave | ECCLES 1,1 × 2,7 kN volta a parear **e o piso sobe a 0,0852** ⇒ reprovam dois testes |
| `grip_lenght_mm` (typo) | nomeado no assert — sem isso o `getattr(..., None)` devolveria `None` para toda curva e a chave voltaria a ser cega **em silêncio**, mesmo modo de falha do `t_0_creep` e do `\b` que virou `0x08` |

Também travado: os **81 motivos** do bloqueio não podem ser apagados (são procedência), os
3 tickets não podem entrar em `_FONTES_RESOLVIDAS_POR_CHAVE`, e a partição usada pelo
teste tem de casar com a do report — senão os testes de pareamento medem uma partição que
o report não usa e passam verdes dizendo nada.

## 8. Reprodutibilidade

```bash
py -3.12 -m pytest tests/test_chave_estendida_pareamento.py \
                   tests/test_provas_de_excecao_nao_envelhecem.py \
                   tests/test_meta_numeros_nao_envelhecem.py -q
```

Rollback: `git revert` do commit. A mudança é (i) a chave em `_pisos_medidos`, (ii) as duas
constantes novas, (iii) dois textos de prova. Sem artefato re-carimbado.
