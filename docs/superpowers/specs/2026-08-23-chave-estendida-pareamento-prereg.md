# PREREG — chave de pareamento ESTENDIDA pelos inputs (ITEM X)

> ## ✅ EXECUTADO em 2026-08-23 — **8 gates verdes, G6 REPROVA COMO ESCRITO**
>
> | gate | resultado |
> |---|---|
> | **G1** exceções | ✅ as 21 seguem ativas; as 2 provas de piso do ECCLES sobrevivem, ambas **PROVA** |
> | **G2** censo | ✅ `_censo()` = **tripé 169/205**, `declarado_total` **201** — idêntico |
> | **G3** nenhum limite afrouxa | ✅ zero limites sobem; ECCLES **0,0698 → 0,0565 (APERTA)** |
> | **G4** pares declarados | ✅ **5 de 5** seguem formando família |
> | **G5** pareamentos corretos | ✅ **6 de 6** (CACCESE rep1×rep2 · YANG_2021 r1..r3 · ECCLES fig8a×fig8c · CHU test5×test6_repeat · LU amp1p0×T22Nm · LIU_2016 1e6×5e6) |
> | **G5b** (extra, não previsto) | ✅ **5 de 5** pares de variável varrida corretamente SEPARADOS |
> | **G6** isolamento | ❌ **REPROVA** — ver abaixo |
> | **G7** provas re-sincronizadas | ✅ 74 testes, incl. `test_provas_de_excecao_nao_envelhecem` |
> | **G8** suíte | ✅ **1129 passed / 1 skipped** (= 1112 do baseline + os 17 da guarda nova) |
> | **G9** tickets bloqueados | ✅ **14** curvas permanecem |
>
> **P1–P4 todas EXATAS**: os pisos medidos pela implementação real reproduzem ao 4º
> decimal os previstos pela sonda de monkeypatch, incluindo os dois `--`.
>
> ### ⚠️ G6 reprova, e o gate estava MAL ESPECIFICADO — não a mudança
>
> G6 exigia piso **bit-idêntico** em fontes sem curva no bloqueio. Violam-no
> `GRZEJDA_2026` e `SUN_2025_REASSY` — exatamente as duas que **P1 e P2 previram**. O
> problema é que G6, como escrito, proíbe a chave de agir fora da lista de bloqueio, o que
> **contradiz o §1(a) deste mesmo prereg**: a chave é global por construção. Eu escrevi um
> gate que testa o oposto do que o documento declara mudar.
>
> **Não reescrevi o gate** — mover a trave depois de ver o resultado é o que a disciplina
> proíbe. Fica vermelho, com o escopo exato do dano medido: as duas fontes **perdem o piso
> inteiro** porque suas "famílias" nunca foram famílias (`bolt1_base`×`bolt6_central` é
> **posição no flange**; `reassy02..10` é **número de remontagens**), **nenhuma exceção
> assinada** vive nelas, e os dois pisos já estavam **abaixo** de `META_SRES` ⇒ o `max()` os
> ignorava e o limite segue **0,0250** nas duas. Efeito real na régua: **zero**.
>
> **O gate que eu deveria ter escrito** — e que fica proposto, não retroativo — é
> *"nenhuma fonte muda de piso **sem** que a mudança seja atribuível a um campo de
> `_CAMPOS_VARRIDOS` que a fonte de fato varre"*. As duas violações passariam por ele com
> atribuição nomeada.


**Assinado pelo professor em 2026-08-23** ("assinado", sobre o ITEM X de
`DECISOES_PENDENTES.md`). Gates **IMUTÁVEIS** a partir desta linha.

**Baseline congelado:** `git HEAD 49e66c6` · store `Models/CALIBRATION_AND_VALIDATION/`
com 210 registros · censo canônico `_censo()` = **tripé 169/205**, `declarado_total` 201 ·
suíte **1112 passed / 1 skipped**.

---

## 1. O que muda

**(a)** A chave de família de réplicas em `report_html._pisos_medidos` passa de

```python
k = (src, delta_mm, F_amp_N, mode)
```

para incluir os campos de input que distinguem a curva:

```python
k = (src, delta_mm, F_amp_N, mode,
     axial_force_amplitude_N, roughness_Ra_um, grip_length_mm,
     member_thickness_mm, reassembly_count, specimen_label,
     external_axial_N, external_axial_mode)
```

**(b)** As curvas de `_SEM_FAMILIA_MECANICA` cujas fontes a chave estendida **já resolve**
saem da lista (**67 de 81**). Ficam as **14** das três fontes com ticket aberto —
`KARLSEN_2022`, `LI_2022_MARSTRUC`, `LI_2022_TRIBOINT` —, cuja variável varrida
(dispositivo de travamento, pré-carga, frequência) o registry **tem** mas a chave ainda
não lê.

**Por que não incluir esses três campos agora:** `frequency_Hz` e `initial_preload_N`
entram na chave de **toda** fonte, não só das três — logo mudam pareamento onde hoje ele
está certo. É passo separado, com o seu próprio gate de isolamento.

## 2. Por que isto NÃO é cosmético

O piso alimenta `limite_sres(fonte) = max(0,025; piso_σ)`, e o piso assina as exceções F7.
Mexer no pareamento pode **(a)** derrubar o denominador de uma prova assinada ou **(b)**
**afrouxar** um limite e aprovar curva hoje reprovada. A régua não pode ficar mais frouxa
como efeito colateral de organizar inputs.

## 3. Gates — congelados

| # | gate | reprova se |
|---|---|---|
| **G1** | **Nenhuma exceção assinada perde estatuto.** As 21 ativas seguem ativas; nenhuma cai para FALHA em todas as pernas. | qualquer uma perde a prova |
| **G2** | **Censo: zero entradas e zero saídas.** `_censo()` devolve tripé **169**/205 antes e depois. | qualquer curva entra ou sai |
| **G3** | **Nenhum `limite_sres` AFROUXA.** Para toda fonte, `limite_novo ≤ limite_base`. | algum limite sobe |
| **G4** | **Pares declarados seguem pareando** (`_PARES_REPLICA_DECLARADOS`). | algum par declarado deixa de formar família |
| **G5** | **Os 15 pareamentos corretos seguem** — `CACCESE rep1×rep2` · `YANG_2021 r1..r3` · `CHU test5×test6_repeat` · `LU amp1p0×T22Nm` · `LIU_2016 1e6×5e6` · `ECCLES` ×4 sem axial | algum deles se desfaz |
| **G6** | **Isolamento:** fontes sem curva no bloqueio têm piso **bit-idêntico**. | alguma muda |
| **G7** | **Provas re-sincronizadas:** os 2 textos de prova-de-piso do ECCLES passam a citar o denominador novo, e `test_provas_de_excecao_nao_envelhecem` fica **verde**. | fica vermelho, ou um número citado segue vencido |
| **G8** | **Suíte completa sem regressão** (≥ 1112 passed, 0 failed). | falha nova |
| **G9** | **Os 3 tickets seguem bloqueados** — 14 curvas permanecem em `_SEM_FAMILIA_MECANICA`. | alguma sai |

**Ramo `INCONCLUSIVO`:** se a medição não puder separar efeito da chave de efeito do
desbloqueio (por exemplo, se um piso mudar em fonte que não deveria ser tocada), o
resultado é **INCONCLUSIVO** e nada é adotado — teste inválido não falsifica nem aprova.

## 4. Predições REGISTRADAS antes de executar

Medidas em sonda só-leitura (`sim_chave.py`, `sim_provas.py`, monkeypatch em processo).
Se a execução divergir de qualquer uma, o instrumento estava errado e o resultado é
**INCONCLUSIVO**.

**P1 — três fontes mudam de piso, e só três:**

| fonte | piso (MAE, res.máx, σ) base → novo | efeito no limite |
|---|---|---|
| `ECCLES_2010` | (0,0541 · 0,1866 · 0,0698) → (**0,0507 · 0,1543 · 0,0565**) | 0,0698 → **0,0565** (APERTA) |
| `GRZEJDA_2026` | (0,0017 · 0,0030 · 0,0009) → **nenhum** | 0,0250 → 0,0250 (piso já era < META) |
| `SUN_2025_REASSY` | (0,0342 · 0,0557 · 0,0120) → **nenhum** | 0,0250 → 0,0250 (idem) |

**P2 — `GRZEJDA` e `SUN_REASSY` perdem o piso porque suas "famílias" nunca foram
famílias** (`bolt1_base`×`bolt6_central` = posição no flange; `reassy02..10` = número de
remontagens). **Nenhuma exceção assinada nessas duas fontes** ⇒ perder o piso não fere
prova nenhuma.

**P3 — as 2 provas de piso do ECCLES SOBREVIVEM, e o grau NÃO muda.** As duas eram
**PROVA** (a perna mais fraca governa) e seguem PROVA:

| curva | perna | base | novo |
|---|---|---|---|
| `fig8a` | MAE 0,0489 | PROVA | PROVA |
| | res.máx 0,1320 | **FORTE** (barra 0,1320) | **PROVA** (barra 0,1091) |
| | σ 0,0395 | FORTE | FORTE (barra 0,0399) |
| `fig8c` | MAE 0,0456 · mx 0,1463 · σ 0,0386 | PROVA · PROVA · FORTE | PROVA · PROVA · FORTE |

⚠️ **A margem de 4e-6 da `fig8a` é consumida** — era exatamente o que a própria prova
declarava (*"passa a barra FORTE por 4e-6, margem que não sobrevive a arredondamento"*).
Ela sobrevive porque o **veredito** já era PROVA; se alguém tivesse assinado FORTE ali, esta
mudança a derrubaria. **A prudência de 2026-08-15 é o que salva a adoção de hoje.**

**P4 — censo: 0 entram, 0 saem, tripé 169/205 igual.**

## 5. O que este prereg NÃO afirma

- **Não** afirma que a lista manual pode ser aposentada por inteiro: 14 curvas ficam, e a
  §1(b) diz por quê.
- **Não** toca `frequency_Hz` / `initial_preload_N` / `locking_device_type` — passo
  separado.
- **Não** mexe em engine, config adotado, store ou fingerprint. Nenhuma re-simulação: o
  piso é recomputado na **geração do report**, a partir dos vetores que o store já tem.

## 6. Rollback

Um `git revert` do commit basta — a mudança é (i) a chave em `_pisos_medidos`, (ii) a lista
`_SEM_FAMILIA_MECANICA`, (iii) dois textos de prova. Sem artefato re-carimbado.
