# Prereg — execução da **P-7** (opção mínima) e da **P-15**

**2026-08-08** · assinatura do professor: *"assine a P-7 e a P-15, e execute"* ·
gates **IMUTÁVEIS** a partir daqui.

## Escopo, e por que dois passos

São **duas mudanças de estatuto independentes**, e serão **dois commits
separados**, seguindo o precedente D-H/D-I (*"passos separados com re-stamp e
commit próprios para que se saiba qual mudou o quê"*):

| | camada tocada | muda o censo? |
|---|---|---|
| **P-15** | `report_html._SEM_FAMILIA_MECANICA` | **sim** (−1) |
| **P-7** | `regra_de_parada_triagem._FONTES_CLASSE_PARADA` | **não** (só triagem) |

⚠️ **Qual opção da P-7.** A proposta oferecia três; a assinatura não nomeou uma.
Executo a **mínima**, que é a marcada *"(recomendada)"* no próprio texto da P-7 e
a única cujo custo foi medido e dissolvido (`p7_orfas_resultado.md`: as 2 órfãs
são artefato de um corte arbitrário de 70 %). A opção 2 (marcador por curva)
**não** é executada porque ela obriga a **re-derivar o critério (c) da regra de
parada** — isso é decisão nova, não execução desta assinatura.

---

## P-15 — bloquear a família de piso do ECCLES

**Ação:** acrescentar a `_SEM_FAMILIA_MECANICA` as **10** curvas do
`ECCLES_2010` que a chave mecânica agrupa em `δ=0,65 / F_amp=6000 / disp`:

```
eccles2010_fig3_typical_no_axial          eccles2010_fig7d_axial_3p1kN_constant
eccles2010_fig6_annotated_4kN_axial       eccles2010_fig8a_no_axial_baseline1
eccles2010_fig7a_no_axial                 eccles2010_fig8b_axial_0p7kN_intermittent
eccles2010_fig7b_axial_1p1kN_constant     eccles2010_fig8c_no_axial_baseline2
eccles2010_fig7c_axial_2p7kN_constant     eccles2010_fig8d_axial_3p5kN_intermittent
```

**Razão:** a chave é cega à **carga axial**, que é a variável varrida do paper.
Os σ da família vão de 0,0195 (sem axial) a 0,1887 (4 kN) — **quase 10×**, e
**monotônicos com a carga axial**. Não é dispersão de réplica.

### Gates (congelados)

| # | gate | valor esperado |
|---|---|---|
| **G1** | `limite_sres("ECCLES_2010")` | **0,0828 → 0,0250** |
| **G2** | censo | **140 → 139** |
| **G3** | curva que sai — **exatamente uma**, e é ela | `eccles2010_fig7c_axial_2p7kN_constant` (σ 0,0258) |
| **G4** | isolamento: nenhuma curva **fora** do `ECCLES_2010` muda de veredito | 0 |
| **G5** | `test_pares_piso_familia` acusa a lista desatualizada | falha em `test_declaracao_nao_vira_ficcao` **e** em `test_a_unica_com_efeito…` |
| **G6** | suíte completa | verde |

⚠️ **G5 é gate de sucesso, não de falha.** Os dois testes que escrevi ontem
**devem** quebrar: a entrada `("ECCLES_2010", 10)` deixa de existir e nenhuma
família passa a morder. Se eles **não** quebrarem, a execução não fez efeito e o
resultado é INCONCLUSIVO.

---

## P-7 — opção mínima: tirar `LU_2024` e `SUN_2025_CRIMP` da classe parada

**Ação:** `_FONTES_CLASSE_PARADA` de
`{CHU_2026, JCSR_2023, LIU_2025, LU_2024, SUN_2025_CRIMP, YANG_2019, YANG_2021}`
para `{CHU_2026, JCSR_2023, LIU_2025, YANG_2019, YANG_2021}`.

**Razão:** as duas são **falsos positivos puros** — 0 curvas com o defeito da
classe, 2 com o defeito **oposto** (o modelo desaba cedo, e "acelerar mais"
piora). Evidência independente: o `SUN` tem r = −0,74/−0,78 contra a forma do
grupo A e o remédio falsificado em 4 doses; o `LU_2024` entrou por decisão
documentada como **frouxa**.

### Gates (congelados)

| # | gate | valor esperado |
|---|---|---|
| **H1** | censo | **inalterado** (a triagem não toca `limite_sres`) |
| **H2** | as 4 curvas saem de `classe_parada` | `lu2024` ×2 · `sun2025efa109235` ×2 |
| **H3** | cada uma cai numa camada **nomeada** (não em "?") | 4/4 |
| **H4** | fila form-limited | reportada, seja qual for — **não** é gate de valor |

⚠️ **H4 não fixa número.** A P-7 previa *"fila 1→5"*, medido quando a fila era 1;
hoje ela é **0** (fechada por mérito no D-Z). Prever 5 seria citar número de
memória — §4.43. Mede-se e publica-se o que der.

---

## Ordem, e o que interrompe

1. P-15 → gates G1–G4 → sincronizar docs vivos → G5/G6 → **commit 1**
2. P-7 → gates H1–H4 → sincronizar docs vivos → suíte → **commit 2**

**Interrompe e reverte** (backups `.bkp_p7p15`): qualquer gate divergir do
esperado acima. G3 é o mais estrito — se sair curva **diferente** da `fig7c`, ou
mais de uma, a premissa da auditoria estava errada e a execução para.

⚠️ **§4.43 obriga:** todo documento vivo que cita 140/205 ou o split 34/31 tem de
ser re-sincronizado **no mesmo commit** — o `test_meta_numeros_nao_envelhecem` o
exige, e é ele que define quais são.
