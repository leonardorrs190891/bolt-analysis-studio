# Prereg — `CHU_2026`: par **nível×forma** do embedding leva a `test5` (e a irmã) ao tripé

**2026-08-14** · assinatura em bloco (*"assine tudo e continue"*) + pedido explícito
(*"esse resultado ainda deve ser melhorado para o tripé; `chu2026ti_D1p0mm_F0_49kN_test5`"*) ·
gates **IMUTÁVEIS** depois desta linha.

## Estado

✅ **EXECUTADO em 2026-08-14 ~16:00 — gates 9/9.**

| gate | resultado |
|---|---|
| **C1** `test5` fecha | 0,0402/0,0880/**0,0436** → 0,0208/0,0395/**0,0183** ✅ |
| **C2** irmã não é trocada | ✅ e **melhora**: σ 0,0285 → **0,0122** |
| **C3** `test1` intocada | ✅ **bit-idêntica** (o grupo não a cobre — verificado no matcher) |
| **C4** censo | **140 → 141** ✅ |
| **C5** zero saem | ✅ |
| **C6** isolamento | ✅ **0** curvas fora do `CHU_2026` mudaram |
| **C7** guardas | 26 ✅ (2 baselines atualizados — ver abaixo) |
| **C8** suíte | **933 passed / 1 skipped** ✅ |
| **C9** docs vivos | **9 números** em 6 documentos + HTML regenerado ✅ |

Fingerprint `cb019d75c6c2` → **`c37618c5cc96`**, uniforme nos 210.

⚠️ **As 2 guardas que dispararam contaram a história certa**, e uma delas fecha um arco:

* **`test5` saiu da `_CLASSE_PARADA`** — o que **vindica** a análise de 4 h antes
  (`classe_parada_atribui_por_fonte.md`), que dizia que o rótulo *"aceleração tardia, classe
  encerrada"* dela estava errado: ela entrou na camada **por pertencer à fonte**, e tinha a
  assinatura de resíduo da própria réplica, que passa. **Curva de classe genuinamente
  encerrada não se resolve com 2 constantes de assentamento.**
* **`test6_repeat` saiu de `_DEPENDEM_DE_PISO_DE_FONTE`** — σ 0,0285 → 0,0122 ⇒ ela deixou de
  **depender do piso** e passa por **mérito**. A guarda denunciou a MELHORA com o mesmo
  barulho de uma piora, e isso está certo: mudança de conjunto tem de ser audível
  **independentemente do sinal**.

## O que se adota

Grupo **NOVO e MÍNIMO** `CHU_2026_D1p0` (regra da D-AB: *grupo nasce mínimo, com o `pack` que
a curva já tinha* — `pack:""`, só as 2 constantes), cobrindo as duas curvas de δ=1,0 mm:

```
emb_depth = 3.0e-05      (nível  — hoje vem da tabela VDI por Rz10-40)
N_emb     = 400.0        (forma  — hoje o default do engine, 50)
```

⚠️ **A `test1` NÃO é tocada.** Ela é a única curva do CHU com config adotada (PR-38) e fixa
`emb_um = 1,6 µm`; o grupo novo cobre só o token `D1p0`.

## Por que estas duas, e não outra coisa

* **Diagnóstico**: ρ(resíduo, N) = **+0,94** ⇒ defeito de **TAXA**; sub-classe **A** (rápido
  cedo, devagar tarde); o instrumento aponta *"erro se forma CEDO"* — e **cedo é embedding**.
* **A rota óbvia foi FALSIFICADA primeiro**: corrigir a rugosidade (item B) para `Rz<4` **piora**
  a `test5` (σ 0,0436 → 0,0546) e derruba a `test6_repeat`. Registrado em
  `chu_test5_rota_encontrada.md`.
* **Varredura CONJUNTA** (lição D-AA — marginal acha ótimo condicional): grade 4×5, **6 células
  fecham**, com crista `mais nível ⇒ mais relógio`. **Região, não fio de navalha.**
* **Alvo comprovadamente alcançável**: a réplica `test6_repeat` **já passa** — mesmo rig, mesma
  condição.

## ⚠️ A fraqueza, escrita ANTES do resultado

As duas constantes **isoladas não ajudam, e uma piora**: só `N_emb`=400 leva σ de 0,0436 a
**0,0449**. Só a **combinação** funciona.

Isso é o que **acoplamento nível×forma** produz — **e o que compensação entre parâmetros
também produz**. As duas leituras dão o mesmo gráfico. **Não há âncora no artigo**: adotar
afirma que um MJ10 aeroespacial de superliga assenta **~4× mais** que a tabela VDI dá para
superfície rugosa, e **8× mais devagar**.

⇒ classe declarada: **`fitado-this-rig`, 2 números**. A ressalva vai **dentro do `prov`**, não
só neste prereg — é onde a próxima auditoria vai olhar.

## Gates (congelados)

| # | gate | esperado |
|---|---|---|
| **C1** | `test5` fecha as 3 pernas | MAE ≤0,05 · mx ≤0,10 · σ ≤ **0,0296** |
| **C2** | `test6_repeat` **continua** passando | não pode ser trocada por ela |
| **C3** | `test1` **bit-idêntica** | Δ = 0 exato (o grupo não a cobre) |
| **C4** | censo | **140 → 141** |
| **C5** | **zero curvas saem** do tripé, dentro e fora do CHU | 0 |
| **C6** | isolamento | nenhuma curva fora do `CHU_2026` muda (Δ = 0) |
| **C7** | as 5 guardas | verdes |
| **C8** | suíte completa | verde |
| **C9** | docs vivos re-sincronizados **no mesmo commit** | censo e `declarado_total` |

⚠️ **C2 e C3 são os que matam a adoção se falharem.** Ganhar a `test5` trocando-a pela irmã,
ou quebrando a única curva quase-perfeita da fonte, não é ganho — é realocação. O gate justo
de fonte já mediu **3/9 com zero saídas**; se a execução divergir disso, algo mudou.

## Rollback

`.bkp_chu5` em `adopted_configs.json` e cópia do store. Qualquer gate divergente ⇒ restaura.
