# `emb_pressure_exp` no `LU_2024` — a lei está CERTA, faz exatamente o que prometeu, e **não basta**

**2026-08-16** · prereg
`docs/superpowers/specs/2026-08-16-lu2024-embedding-dirigido-por-pressao-prereg.md`
(gates congelados antes de medir) · store `20be19aabe11` · **NADA ADOTADO**;
capacidade fica no engine **default-inerte**, no precedente do
`loose_arrest_residual`.

## 1. Veredicto dos gates

| # | gate | resultado |
|---|---|---|
| **G0** | inércia bit-a-bit com `emb_pressure_exp=0` | **OK** — **210 curvas, pior |Δ| = 0,000e+00**; trajetória de 300 ciclos também bit-idêntica (`np.array_equal`) |
| **G1** | a alvo fecha o tripé | ❌ **FALHOU** — melhor MAE **0,1599** = **3,2×** o limite |
| **G2** | controle da fonte | **OK** — pior variação numa irmã: **+0,0000** |
| **G3** | isolamento fora do `LU_2024` | **OK** — por construção (`min(1,·)`) |
| **G4** | procedência | **OK** — 1 número; `p_ref_emb` no default 1,5e8 |
| **G5** | regra de escolha | n/a (nenhuma célula aprovada) |
| **G6** | fronteira de grade | **OK** — grade estendida a n=12; mínimo de MAE **interior** em n=4,0 |
| **G7** | guardas de campo novo | **OK** — `VarSpec` + **11** testes de contrato |
| **G8** | falsificação honesta | **ACIONADO** — o candidato declarado **não fecha a alvo**; ver §4 |

## 2. A lei faz exatamente o que foi projetada para fazer

| n_p | MAE | res.máx | σ_res | viés | ρ(res, N) |
|---:|---:|---:|---:|---:|---:|
| 0,0 | 0,2514 | 0,3146 | 0,0749 | −0,2514 | +0,41 |
| 3,0 | 0,1694 | 0,2760 | 0,1039 | −0,1694 | −0,64 |
| **4,0** | **0,1599** | 0,2668 | 0,1188 | −0,1498 | −0,66 |
| 8,0 | 0,1660 | 0,2605 | 0,1540 | −0,1039 | −0,76 |
| 12,0 | 0,1694 | 0,2568 | 0,1665 | −0,0873 | −0,79 |

- **Isolamento estrutural CONFIRMADO**: as 12 irmãs movem **+0,0000** em toda a
  grade — o `min(1,·)` põe as curvas com p ≥ p_ref em S = 1 exato, e 5 das 7 da
  varredura (incluindo **as 3 do tripé**) estão lá. Isso era predição registrada
  nº 4 e bateu.
- **Direção certa**: MAE cai **36 %**, res.máx cai 18 %.
- ⚠️ **Minha predição nº 2 estava certa no alvo e errada no mecanismo.** Eu
  previa que o σ_res seria a perna de risco *por ser insensível a nível*.
  Medido: ele **piora** (0,0749 → 0,1188 no ótimo de MAE), e o `ρ(res, N)` vira
  de +0,41 para **−0,79** — a correção troca erro de **nível** por erro de
  **forma**.

## 3. O perfil ponto a ponto mostra POR QUE — e revela um SEGUNDO defeito

| N | dado | n=0 | resíduo | n=4 | resíduo |
|---:|---:|---:|---:|---:|---:|
| 1 | 0,638 | 0,373 | **−0,265** | 0,656 | **+0,018** |
| 6 | 0,474 | 0,189 | −0,285 | 0,493 | +0,019 |
| 17 | 0,420 | 0,105 | −0,315 | 0,271 | −0,149 |
| 37 | 0,368 | 0,098 | −0,269 | 0,101 | −0,267 |
| 99 | 0,310 | 0,092 | −0,219 | 0,094 | −0,217 |

**Queda no 1º ciclo:** dado **0,362** · modelo n=0 **0,627** · modelo n=4
**0,344**. Ou seja: **a lei de pressão conserta o 1º ciclo quase
perfeitamente** — o defeito que o diagnóstico nomeou era real e esta é a
alavanca dele.

**O que sobra é outro defeito, e ele estava escondido atrás do primeiro:** de
N=1 até o fim o dado cai 0,328 e o modelo (n=4) cai **0,562**, colapsando até
um piso de **~0,095** já em N≈29 e ficando lá, enquanto o dado desce suave até
**0,310**. Esse piso é o `loose_arrest_floor` = **0,10** adotado na fonte: o
modelo trava em 10 % da pré-carga inicial e o dado retém **31 %**.

## 4. VEREDITO do candidato declarado, e a hipótese NOVA que ele revelou

⚠️ **Primeiro o que os gates dizem, sem atenuante:** o candidato **declarado no
prereg** era `emb_pressure_exp` **sozinho**, com todo o resto congelado. Ele
**REPROVOU no G1** — não fecha em nenhuma célula, nem na grade estendida. O G8
está acionado e o registro é esse. O que vem abaixo é **hipótese nova**,
descoberta *depois* de medir, e não resgata o candidato: ela terá de ser
gateada num prereg próprio, se algum dia tiver procedência (§5 mostra que hoje
não tem).

Precedente D-Z (varredura marginal encontra ótimo **condicional**): antes de
fechar o registro, varri o par.

| n_p | floor | MAE | res.máx | σ_res | final |
|---:|---:|---:|---:|---:|---:|
| 0,0 | 0,10 | 0,2514 | 0,3146 | 0,0749 | 0,092 |
| 2,0 | 0,34 | 0,0256 | 0,0807 | 0,0233 | 0,320 |
| **3,0** | **0,34** | **0,0112** | **0,0284** | **0,0138** | **0,323** |
| 4,0 | 0,34 | 0,0205 | 0,0741 | 0,0259 | 0,325 |

**A alvo fecha com folga** — as três pernas em ~metade do limite (pior perna
**0,55×**). E fecha porque as duas correções tratam **defeitos diferentes**: a
de pressão põe o 1º ciclo no lugar, a do piso põe o terminal.

⚠️ **Isto valida a disciplina D-Z contra mim mesmo:** a varredura marginal do
`emb_pressure_exp` dizia "3,2× o limite, não fecha, e ainda piora o σ". A
conclusão correta não era *"a lei está errada"*, era *"a lei está incompleta"*.

## 5. Mesmo assim: **NADA É ADOTADO**, e o motivo é medido

`loose_arrest_floor` é constante **por fonte**, e as irmãs a contradizem. A
retenção terminal do próprio dado, na varredura de torque:

> ⚠️ **ERRATA 2026-08-16 (manhã) — a tabela abaixo media a coisa ERRADA.** Eu li
> o último ponto de `metric_data`, que é o último ponto **acima do `FLOOR_TRIM`
> de 0,10**, e não o terminal do ensaio. Publiquei
> `0,142 / 0,310 / 0,190 / 0,102 / 0,233`; os terminais **reais**, lidos da
> Tabela 9 do próprio paper, são `0,037 / 0,309 / 0,187 / 0,064 / 0,234`. É o
> gotcha que o `CLAUDE.md` documenta, e eu caí nele. **A conclusão sobrevive e
> fica mais forte** — ver `lu2024_fig20_nao_monotonia_e_fisica.md`. Tabela já
> corrigida:

| curva | F₀ (N) | retenção final (Tab. 9 do paper) | núcleo travado absoluto |
|---|---:|---:|---:|
| `T4Nm` | 2 105 | **0,037** | 78 N |
| `T10Nm` | 5 963 | **0,309** | 1 843 N |
| `T16Nm` | 8 402 | 0,187 | 1 571 N |
| `T22Nm` | 11 567 | **0,064** | 740 N |
| `T28Nm` | 15 027 | 0,234 | 3 516 N |

- `corr(retenção, 1/F₀)` = **−0,511** ⇒ **não há lei de pré-carga** para o piso,
  ao contrário do que há para o 1º ciclo (r = +0,995).
- O núcleo travado **absoluto** varia **45×** (78 N a 3 516 N). Longe de constante.
- A retenção é **não-monótona** no torque, e o paper **publica e explica** isso
  (Tabela 9 + p.19): há um torque de perda mínima em ~10 N·m. ⇒ um piso
  **fracionário único** não pode gerar esse terminal, o que fecha a rota por
  argumento **estrutural**, e não só por ausência de correlação.

⚠️ **A sessão A mediu, no mesmo dia, a face COMPLEMENTAR disto**
(`lu2024_fig20_v_centrado_na_ancora.md`), e as duas leituras precisam ser lidas
juntas para não parecerem opostas. Aqui eu meço a **retenção do DADO** e a acho
**sem lei** de pré-carga. Lá se mede o **viés do MODELO** e ele é **monótono** em
torque (ρ = **+0,900**), com o mínimo caindo **exatamente na `T22Nm`** — a curva
contra a qual a fonte foi calibrada. **Dado sem lei + erro do modelo com lei e
mínimo na âncora = a dependência de torque é DO MODELO.** Isso reforça, e não
enfraquece, o diagnóstico de encaixe cego à pré-carga; e explica por que a
correção de 1º ciclo funciona tão bem sem fechar a curva.

⇒ o par que fecha a alvo é **fit por curva sem procedência**, que é exatamente
o que o item D da doutrina proíbe. Adotar `floor`=0,34 na fonte destruiria a
`T22Nm` (dado 0,102) — que acabou de entrar no tripé.

## 6. O que fica

1. **Capacidade `emb_pressure_exp` no engine, DEFAULT-INERTE** (G0 bit-a-bit,
   11 testes de contrato — incluindo o G0 de TRAJETÓRIA e o **espelho** dele, que
   prova que a capacidade não é um no-op silencioso —, `VarSpec` na página do
   explorador). Precedente:
   `loose_arrest_residual` — mecanismo validado, adoção não gateada.
2. **A `lu2024_M8_fig20_T10Nm` segue form-limited**, agora com caracterização
   muito mais fina: **dois** defeitos, não um. O de 1º ciclo **tem lei e tem
   alavanca**; o terminal **não tem lei nesta fonte**.
3. ~~**Pergunta nova para a fila do professor:** a retenção terminal
   não-monótona da `fig20` é física ou é a mesma mistura de protocolos das
   "órfãs de protocolo"?~~ ✅ **RESPONDIDA no mesmo dia, lendo o PDF**
   (`lu2024_fig20_nao_monotonia_e_fisica.md`): é **FÍSICA e PUBLICADA** — a
   Tabela 9 traz os terminais e a p.19 os explica (4 N·m *"não atinge o efeito
   de aperto"*; 10 N·m é o ótimo; de 10 a 22 N·m *"a velocidade de atenuação
   aumenta com o torque"*; 28 N·m recupera). A mistura de protocolos está
   **refutada** para a fig20: um protocolo, uma amplitude (1,0 mm), uma máquina.
   **Nenhum estatuto muda.**

   ⛔ **E o subproduto NÃO é positivo — retratação minha, 40 min depois.** Eu
   escrevi aqui que *"o modelo reproduz a não-monotonicidade (Spearman +0,700)"*.
   Falso: com `FLOOR_TRIM` ligado a simulação é **truncada**, e comparei o modelo
   em N=54 contra o dado em N=99 (o `np.interp` grampeia). Sem piso, o terminal
   do modelo é **plano** — 0,000 na `T4` e **0,092/0,094/0,095/0,097** nas
   outras, faixa de 0,005 contra os 0,272 do dado; Spearman **+0,300**. O
   terminal é fixado pelo `loose_arrest_floor`, fração única de F₀, que por
   construção **não espalha**. Isso **reforça** o §5: a rota do piso fecha por
   dois argumentos independentes (o dado não tem lei; o modelo não tem
   espalhamento).

## 7. Sobre o G0 — o que está medido, e por que basta

O gate pede bit-a-bit. Três camadas, em ordem de força:

1. **Argumento** (não é prova suficiente sozinho, mas é exato): o fator devolve
   `1.0` **exato** no caminho desligado, e em IEEE754 `x * 1.0 == x` bit-a-bit
   — inclusive preservando o agrupamento à esquerda da cadeia de produtos em
   que ele foi inserido. Logo a inércia é estrutural, não estatística.
2. **Medido em trajetória**: `test_g0_default_off_e_bit_identico_na_trajetoria`
   compara 300 ciclos com `np.array_equal` (igualdade exata, não tolerância).
   O **espelho** — `test_ligado_a_trajetoria_muda_so_abaixo_da_referencia` —
   existe porque "passa no G0" também é o que um `return 1.0` mal colocado faz;
   sem ele, uma capacidade morta passaria por inerte-por-projeto.
3. **Medido no lote — CONCLUÍDO**: re-simulação das **210** curvas do store com
   o campo no default, comparando MAE, res.máx e σ_res curva a curva. Resultado:
   **pior |Δ| = 0,000e+00**. ⚠️ **Custa ~30 min** — uma das curvas tem 5 × 10⁶ ciclos. A 1ª
   tentativa foi ainda pior, por defeito meu: cada tarefa do pool reconstruía o
   registry inteiro (210 leituras de CSV, ~26 min só nisso). Quem repetir:
   **cacheie `all_records()` num global por worker**, não por tarefa. As 13 do
   `LU_2024` já estão conferidas ao dígito — a linha `n_p = 0,0` das grades
   acima **é** o store.

## 8. Reprodutibilidade

Sondas de sessão sobre `runner._effective_overrides` (sandbox, nada escrito no
store). Contrato do campo: `py -3.12 -m pytest tests/test_embedding_pressure_factor.py`.
