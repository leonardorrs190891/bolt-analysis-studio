# PRÉ-REGISTRO — 3ª perna com piso POR FONTE

**Escrito em 2026-07-29, ANTES de medir o resultado.** Gates IMUTÁVEIS a partir
daqui (regra do repo). Store de base: `3546e6745448`.

## 1. A proposta, em uma linha

Trocar a 3ª perna do tripé de

```
σ_res ≤ 0,025                              (global, hoje)
```

para

```
σ_res ≤ max(0,025 ; piso_σ da fonte)       (por fonte)
```

O `max` é a parte essencial: a regra **nunca aperta** em relação a hoje. Ela
apenas deixa de exigir, de uma fonte ruidosa, concordância melhor do que a que a
fonte tem **consigo mesma**.

## 2. Por que — o argumento, não o número

O piso de repetibilidade é medido **por fonte** (`_pisos_medidos`, pares
dado-contra-dado na janela de x comum). Ele varia em quase uma ordem de
grandeza:

| fonte | piso σ medido | em múltiplos do limite global |
|---|---:|---:|
| JCSR_2023 | 0,2214 | **8,9×** |
| ROUSSEAU_2025 | 0,1859 | 7,4× |
| KARLSEN_2022 | 0,1742 | 7,0× |
| BAUER_2024 | 0,0900 | 3,6× |
| ECCLES_2010 | 0,0828 | 3,3× |
| CHU_2026 | 0,0507 | 2,0× |

Exigir `σ_res ≤ 0,025` do JCSR_2023 é exigir do modelo **9× mais concordância
com o dado do que o dado tem consigo mesmo**. Reprovar ali não mede o modelo —
mede o experimento, que é a definição operacional de perseguir ruído.

Isto **já é aceito pelo projeto**: as **38 exceções "por prova de piso"** da F7
usam exatamente este raciocínio, curva por curva, com assinatura humana. A
proposta é torná-lo **regra derivável** em vez de 44 assinaturas.

## 3. O que a proposta NÃO é

* **Não é afrouxamento de meta para melhorar o número-manchete.** O ganho
  numérico é ~1 curva (ver gate G2): 19 das 20 que passam a entrar **já eram
  exceção assinada**. O valor é de método, não de contagem.
* **Não** substitui o limite global: onde o piso é baixo, vale 0,025 (o `max`).
* **Não** re-julga as outras duas pernas.

## 4. GATES (imutáveis)

**G1 — MONOTONIA (bloqueante).** Nenhuma curva que está no tripé hoje pode sair.
Formalmente: `{aprovadas com a regra} ⊇ {aprovadas hoje}`. Uma única saída
reprova a adoção inteira.

**G2 — MÉRITO DECLARADO (bloqueante).** Medir e **publicar**: de quantas curvas
que entram, quantas já eram exceção assinada. Se a proposta for apresentada como
ganho de contagem em vez de ganho de método, reprova. O número honesto tem de
constar do commit e do `MODEL_LEGITIMACY.md`.

**G3 — COBERTURA DECLARADA (bloqueante).** As fontes **sem** piso medido (sem
réplica em condição repetida) têm de ser (a) contadas, (b) nomeadas, e (c)
tratadas pelo limite global — nunca por piso estimado, interpolado ou herdado de
outra fonte. Estimar piso onde não há réplica reprova a adoção.

**G4 — EXCEÇÕES QUE VIRAM MÉRITO (informacional, não bloqueante).** Contar
quantas das 44 exceções assinadas a regra passa a cobrir por mérito. Não retirar
nenhuma assinatura neste passo: a retirada é decisão do professor, em commit
separado.

**G5 — SUÍTE (bloqueante).** Suíte completa verde. Os números publicados no
report e nos documentos vivos re-medidos e re-sincronizados no MESMO commit
(o teste `test_meta_numeros_nao_envelhecem.py` faz cumprir).

## 5. Falsificadores declarados

A proposta **deve ser abandonada** se:

* **F1** — alguma curva sair do tripé (viola G1) ⇒ o `max` está mal implementado
  ou o piso foi medido com outra convenção;
* **F2** — o piso por fonte mudar de valor ao ser recomputado numa geração
  diferente do store por causa da **regra de família** (o piso é lido do
  `config_used`, não do nome do arquivo): se o piso não for estável, ele não pode
  ser limite;
* **F3** — a regra passar a aprovar curva cujo σ_res exceda o piso da própria
  fonte (bug de sinal/`min` em vez de `max`).

## 6. O que fica FORA deste passo, explicitamente

* Retirar assinaturas de exceção (G4 é só contagem).
* Mexer no `META_SRES` global — ele **permanece 0,025**.
* Re-julgar a classificação form-limited/exceção sob a régua nova (dívida
  registrada no `MODEL_LEGITIMACY.md` §8).
* Propagar a perna por fonte ao `_tripe_ok` do runner/GUI — este passo é do
  **report e do censo**; a propagação é follow-up com prereg próprio.

## 7. Decisão

⛔ **NÃO ASSINADO** no momento da escrita. A execução abaixo mede os gates; a
adoção no canônico é do professor.
