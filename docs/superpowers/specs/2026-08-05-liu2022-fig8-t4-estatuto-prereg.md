# Prereg — estatuto da `liu2022_fig8_multi_t4` (fratura por fadiga)

**2026-08-05** · decisão D-M (por delegação, MANDATO PERMANENTE) · gates
escritos **antes** de conhecer o resultado do D-L. Fingerprint de partida:
`98fd6c462968`.

## Declaração de ordem (a razão de este prereg existir separado)

O mandato permanente diz: *"Estatuto de curva decide-se pelos méritos dela,
ANTES e independentemente de qualquer gate que ele desbloqueie."*

Esta curva **bloqueia o G4 do D-L**. Por isso este documento foi escrito
**enquanto o D-L ainda rodava**, sem saber qual parametrização vence nem
quanto exatamente o `t4` piora nela. O argumento abaixo não usa nenhum número
do D-L, e a decisão vale **com ou sem** ele.

**Teste de independência que eu me imponho:** se o D-L terminasse
FALSIFICADO por outro motivo, eu proporia esta declaração do mesmo jeito? A
resposta tem de ser sim — e é, porque a procedência é anterior a toda esta
linha de trabalho.

## Procedência, toda anterior a esta sessão

1. **`core/validation_cases.py`**, nota do próprio caso:
   *"4th retightening — ends in **FATIGUE FRACTURE** at ~1500 cyc (trim)"*.
2. **Nota de aparato** (`liu2022_istruc_retightening.md`):
   *"fig8_multi_t4 ends at the **fracture dive** (~78 % at 1,500 cycles),
   **not a loosening endpoint**"*.
3. **`CLAUDE.md`**, seção de gotchas, nomeia `liu2022_fig8_t4` explicitamente
   entre as *"finais de curva com fratura por fadiga (…) out-of-model → trim"*.
4. **O cfg do grupo `LIU_2022_RETIGHT_fig8` não tem canal de fadiga**
   (`fatigue_enabled` ausente) ⇒ o mergulho terminal é **inproduzível por
   construção**, não mal-ajustado.

## Por que NÃO a rota por mérito (fadiga ligada)

Avaliada e recusada em 2026-08-04, com número: a rampa adotada usa
`fat_ramp_D_on=0,75` e `fat_ramp_q=8` — `A_eff/A_s = 1−((D−0,75)/0,25)^8` é uma
navalha que não faz nada até D≈1 e então leva F₀ a zero. O dado do `t4` pede
mergulho **parcial** (para 0,845, não para 0). Com `N_f=1500` exato o modelo vai
a ~0 (pior que hoje); com `N_f=1700` o efeito é 0,5 % (invisível). Produzir
mergulho parcial exigiria afrouxar `q` **e** ajustar `C1` = **2 números livres
numa curva de 7 pontos**, mais ~6 constantes transplantadas de outro paper
(M10/M16 → M12). Isso é fit com aparência de mecanismo.

## Gates (IMUTÁVEIS a partir daqui)

- **G1 (procedência anterior):** a documentação da fratura tem de ser
  **anterior** a esta linha de trabalho, em ≥2 lugares independentes.
  Verificável por `git log`/`git blame`. **Se a procedência fosse desta
  sessão, o ramo é NÃO DECLARAR** — seria racionalização.
- **G2 (inproduzibilidade estrutural):** o cfg do grupo tem de **não** ter
  canal de fadiga. Se tiver, a curva é julgável e o ramo é NÃO DECLARAR.
- **G3 (precedente):** a classe *declarada por escopo* já tem de existir com
  critério equivalente. Precedentes citados: `lu2024_fig20_T4Nm` (o paper diz
  que o ensaio *"does not reach the tightening effect"*) e
  `yang2023ame_axial` (CFRP, fora de escopo de material).
- **G4 (o teste de independência):** a declaração tem de se sustentar sem
  citar o D-L. Nenhum número do D-L pode aparecer na justificativa gravada.
- **G5 (custo declarado):** a declaração **não** conta como acerto do modelo.
  Publicar as duas leituras, como sempre.

  ⚠️ **ERRO ARITMÉTICO MEU, corrigido na execução e mantido aqui à vista:**
  esta linha dizia *"a leitura estrita cai de 131 para 130/205"*. Está
  **errado** — o `t4` **nunca estava no tripé** (reprovava por σ), logo
  declará-lo não reduz a leitura estrita. Medido: estrita **131 inalterada**,
  resolvida/declarada **171 → 172/205**, declaradas 15 → 16. Declarar curva
  que já estava fora custa **zero** na estrita; só a leitura dupla se move.
  O gate pedia o custo DECLARADO, e ele está — o número que eu estimei é que
  estava errado, e a correção fica registrada em vez de ajustada em silêncio.
- **G6 (sincronia):** `_DECLARADAS` + censo + docs + páginas + testes no MESMO
  commit; o `test_meta_numeros_nao_envelhecem` tem de ficar verde.

### Ramos

- **DECLARA (escopo: fratura fora do modelo)** — G1..G4 cumpridos.
- **NÃO DECLARA** — qualquer um de G1/G2/G4 falha.

## O que a declaração NÃO autoriza

Não autoriza re-rodar o D-L e apresentar o resultado como se o `t4` nunca
tivesse existido. Se o D-L for re-executado depois desta decisão, o texto de
adoção tem de dizer, com o número: *"o `t4` piora em X, e ele está fora do
censo por escopo desde D-M, decidido antes de conhecer o resultado"*. A ordem
da prova fica registrada, não apagada.
