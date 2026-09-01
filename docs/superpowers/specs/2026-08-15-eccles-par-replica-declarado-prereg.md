# PREREG — declarar `fig8a`×`fig8c` como par de réplica do `ECCLES_2010` (item O, opção **a**)

**Data:** 2026-08-15 (19:xx) · **Autorização:** professor, *"assine e continue"* (19:14),
sobre as duas opções postas em `item_O_nao_executar_o_veredito_depende_do_par.md` ·
**Store de partida:** `20be19aabe11`, censo **143/205**, exceções **23**,
`limite_sres(ECCLES_2010)` = **0,0250** (piso da fonte = `None`).

⚠️ **Gates IMUTÁVEIS depois de escritos.** Nada abaixo pode mudar após a primeira medição.

---

## 1. O que se declara, e por quê

Acrescentar **uma** entrada a `_PARES_REPLICA_DECLARADOS`:

```python
('eccles2010_fig8a_no_axial_baseline1',
 'eccles2010_fig8c_no_axial_baseline2',
 'no axial — baseline1/baseline2 da MESMA condição, rótulo DO AUTOR (Fig. 8a×8c)')
```

**Procedência:** o paper nomeia as duas curvas **`baseline1`** e **`baseline2`** — declaração
de réplica **pelo autor**, o mesmo estatuto dos 4 pares já declarados (`rep1/rep2` do CACCESE,
`run1/run2` do LIU_2016, Fig. 8c×8a do LI_2022, `run2p2/run7p1` do KARLSEN).

**Por que não desbloquear a fonte:** as 10 curvas do ECCLES estão em `_SEM_FAMILIA_MECANICA`
por *"carga axial ≠ (variável varrida)"*, e o bloqueio está **certo** para os 6 pares que
cruzam cargas axiais. O que ele é, é **largo demais**: as 4 `no_axial` têm axial = 0. O
docstring de `_pisos_medidos` prevê exatamente esta saída — *"pares declarados continuam
possíveis"*. Declarar **um** par é cirúrgico; desbloquear a fonte reabriria os 6 pares
inválidos.

**Por que este par e não outro dos 6:** medido, os 6 dão **3 vereditos** diferentes
(`item_O_…md` §3). `fig3_typical` é curva **ilustrativa** e `fig7a` é baseline de **outra
série** — pareá-las é afirmação mais fraca que a do autor. A escolha é de **procedência**, e
está declarada aqui **antes** de medir o efeito.

## 2. Efeito esperado no piso (já medido no diagnóstico)

| | hoje | com o par |
|---|---:|---:|
| piso `ECCLES_2010` (MAE · res.máx · σ) | `None` | 0,0541 · 0,1866 · **0,0698** |
| `limite_sres(ECCLES_2010)` | 0,0250 | **0,0698** |

## 3. Predições registradas ANTES de medir o efeito

1. **As 2 exceções NÃO entram no tripé.** `fig8a` tem res.máx **0,1320** e `fig8c` **0,1463**,
   ambas > `META_MAX` = 0,10 — e o par **não mexe** em `META_MAX`. Elas seguem exceções,
   agora com **denominador válido**. Se alguma entrar no tripé, o teste está inválido.
2. **O censo sobe em 0, 1 ou 2** — e só pode subir por curva do `ECCLES_2010` que já passe
   MAE ≤ 0,05 **e** res.máx ≤ 0,10 e que hoje reprove **só** no σ, com σ ∈ (0,0250 ; 0,0698].
3. **Δ = 0,0000 exato fora do `ECCLES_2010`.** O par é por fonte; nenhuma outra fonte pode
   mover.
4. **Nenhuma curva SAI do tripé.** O limite da fonte só **sobe** (`max(0,025 ; piso)`), logo é
   monotônico — saída seria bug.

## 4. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | isolamento | Δ = **0,0000 exato** em toda curva fora do `ECCLES_2010` (tripé e as 3 pernas) |
| **G2** | monotonia | **nenhuma** curva sai do tripé, em fonte nenhuma |
| **G3** | as 2 exceções seguem exceções | `fig8a` e `fig8c` **não** entram no tripé (predição 1; se entrarem, teste inválido) |
| **G4** | o piso é o medido | `piso_da_fonte(ECCLES_2010)` = σ **0,0698 ± 0,0002** e `limite_sres` = o mesmo |
| **G5** | prova re-escrita | as provas gravadas das 2 exceções passam a citar o denominador **VÁLIDO** (0,1866 / 0,0698), não o inválido (0,257 / 0,083) — senão a retratação da P-15 continua valendo contra elas |
| **G6** | catraca | `test_excecao_catraca_auditavel` segue verde: as 2 mantêm o **trio conferível** |
| **G7** | suíte | suíte completa verde antes do commit |
| **G8** | documentos vivos | censo re-medido e **todos** os documentos sob guarda re-sincronizados no MESMO commit (`test_meta_numeros_nao_envelhecem` verde) |

## 5. Ramos do veredito

- **ADOTA** — G1–G8 passam.
- **REVERTE** — qualquer gate falha ⇒ desfaz a declaração e registra o motivo.
- **INCONCLUSIVO** — o teste não testou (par não casou, piso não mudou, Δ = 0 em tudo). ⚠️
  Ramo incluído de propósito: sem ele o script escolhe entre PASSA e FALSIFICADO sobre teste
  vazio (2× em 2026-07-30).
- **PARCIAL** — G1–G4 passam e G5 exige reescrever prova: ⇒ **executar a reescrita no mesmo
  commit**, nunca deixar prova com denominador inválido no repositório.

## 6. ⚠️ Ressalva que NÃO se resolve aqui

Com o par do artigo, `fig8a` fica a **1,6 × 10⁻⁵** da barra FORTE (`res.máx` 0,131955 contra
0,131939). O **grau** da prova (FORTE × PROVA) é numericamente instável nessa casa; o
**veredito** (passa PROVA) não é. ⇒ **a prova reescrita deve dizer PROVA, não FORTE**, mesmo
que a comparação em precisão cheia dê FORTE — publicar o grau mais forte com margem de 10⁻⁵
seria precisão falsa.

## 7. Rollback

Backup de `report_html.py` antes de tocar; a mudança é **uma entrada de lista**. Reverter =
remover a entrada e re-medir. O store **não** precisa de re-carimbo: o par declarado entra no
cálculo de **piso**, que é recomputado na geração — **não** no `engine_fingerprint`.
⚠️ **Verificar essa última afirmação como parte do G1**, não assumi-la.
