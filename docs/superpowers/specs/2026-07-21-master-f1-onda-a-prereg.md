# Pré-registro — F1 Onda A (adoções risco-zero, prompt-mestre 2026-07-17)

**Data:** 2026-07-21 · **Executor:** sessão mestre (ledger `.superpowers/master-0p1-progress.md`)
· **Autorização:** standing do prompt-mestre ("Executar preregs e ADOTAR sempre que o gate passar
no tripé contra o baseline vigente"); F1 é a onda de risco-zero — **gate = paridade exata**
(nada muda por construção). Sucessor de `2026-07-11-mem-iter4-preregistrations.md`.

Escrito ANTES de qualquer mudança de código/config da F1 (gates imutáveis a partir daqui).
Baseline vigente = re-pin F0.4 (store `report --all` pós-merge 166a761, 202 casos).

## Item 1 — `kj_mode="pedersen"` como proveniência de geometria

**O que muda:** `adopted_configs.json` → `sources.ROUSSEAU_2025.cfg` e `sources.ZHANG_2006.cfg`
ganham `kj_mode: "pedersen"` + `d_hole_mm`/`d_washer_mm` com bloco `prov`:
- ROUSSEAU_2025: `d_hole_mm=13.6` (prov **paper**: nota de aparato, "hole diameter 13.6 mm");
  `d_washer_mm=24.0` (prov **iso**: ISO 7089 OD normal-series M12; a nota só dá espessura 2,4 mm).
- ZHANG_2006: `d_hole_mm=13.5` (prov **assumed**: ISO 273 ajuste médio M12; banda 13,5–14 do
  controlador T6); `d_washer_mm=24.0` (prov **iso**).
E o runner (`validation/runner.py`) passa a aplicar `d_hole/d_washer` do cfg adotado à geometria
(mesmo precedente do `GA_member`: "lido do cfg cru"), convertendo mm→m; `material_kwargs_for`
já repassa `kj_mode` (string) via cfg.

**Gate (imutável):**
- G1a. Paridade exata da população: para TODOS os 202 casos, `MAE` e `maxerr` idênticos ao
  baseline F0.4 (Δ=0.0 bit-a-bit, mesma tolerância do gate T6: `all_delta_mae_exactly_zero`).
  Fundamento: T6 mediu Δ MAE = 0,0 exato em 8/8 (trajetória transversal k_j-cega no PACK).
- G1b. Engate correto: `kj_mode_engaged=True` **somente** nos 8 casos com geometria fornecida
  (rousseau2025 ×6, zhang2006 ×2); False (fallback silencioso p/ `k_j_init`) em todos os demais.
- G1c. Suíte-alvo verde (incl. `test_l2_kj_law.py`).
- FAIL de qualquer sub-gate → reverter config+código, documentar no ledger, NÃO adotar.

## Item 2 — Check L7 (bound de energia de remoção) default-on informacional

**O que muda:** o runner/report passa a chamar `analyzer.removal_energy_check()` ao fim de cada
simulação e anexa o dict informacional ao caso (report HTML §6/caveats + campo no store). NÃO
altera trajetória (é pós-processamento read-only do run).

**Gate (imutável):**
- G2a. Paridade exata da população (mesmo critério G1a) — o check não pode tocar em nenhum número
  de simulação.
- G2b. O report exibe o aviso "par não-casado" quando `implied` sai da banda
  `removal_energy_bound()` (1,8–10,5 kJ/mm³) — verificável no caso já conhecido (µ default ×
  k_wear_spec Zhang ⇒ 1,71× acima do teto, achado T8).
- G2c. Suíte-alvo verde (incl. `test_l7_removal_bound_and_viscous.py`).

## Item 3 — Bandas do KB (R5) no `check_input`

**O que muda:** `parameter_registry.check_input_provenance` passa a cobrir, além das 4 âncoras
§4.26 (`priors_ancoras`), as âncoras R5 (`r5_anchors.json`): `k_wear_spec` (banda por
interface|par via `wear_spec_anchor`) e `mu_thread` por revestimento (`mu_thread_anchor`),
citando fonte/proveniência na mensagem. Consumo: calibração/GUI (aviso), nunca bloqueio.

**Gate (imutável):**
- G3a. Zero efeito de engine (função só de aviso; nenhum caminho de simulação a chama) —
  paridade exata garantida por construção; confirmar com a suíte.
- G3b. Testes unitários novos: valor dentro da banda → None; fora → mensagem com fonte; par/
  revestimento desconhecido → None (sem KeyError vazando pro chamador do check_input).
- G3c. Suíte-alvo verde (incl. `test_knowledge_base_r5.py`).

## Adoção e registro (se TODOS os gates passarem)

`adopted_configs.json` atualizado com `prov` por constante; linha no ledger mestre; commit(s)
com arquivos explícitos; re-run parcial de verificação (paridade) já embutido nos gates.
Classe de procedência: item 1 = forma adotada como **proveniência** (Pedersen 2008, rank
Rousseau 2024 +24%) + inputs de paper/iso/assumed etiquetados; itens 2–3 = wiring informacional
(0 DOF).

## Rollback

Qualquer FAIL: `git revert` do(s) commit(s) da F1 (ou reset do cfg no JSON), registro do
impasse no ledger, e a execução segue para F2 apenas se o FAIL for do item isolado (itens são
independentes; FAIL de um não bloqueia os outros dois — cada um adota/reverte sozinho).
