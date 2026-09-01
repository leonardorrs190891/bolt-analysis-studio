# Prereg — LIU_2022_RETIGHT: re-atribuição da cauda para FRETTING DE ROSCA (mecanismo dos autores)

**2026-08-01** · receita do Rousseau/LIU_2016 aplicada à fonte mais
próxima do tripé na fila (3 curvas a 1,07–1,16×). Gates antes de medir.

## O desacordo, medido (fingerprint `a410d6537c83`)

**Os autores** (Structures 44:1303, seção de mecanismos) atribuem
explicitamente: *"the decrease of clamping force in the initial stage is
mainly caused by plastic deformation of threads"* e *"the **fretting wear
between threads** is the main reason for reduction of clamping force in
later stage"*.

**O modelo** hoje, nas 3 curvas da fila (decomposição do store):

| curva | embedding | wear (bearing) | rot. | creep |
|---|---:|---:|---:|---:|
| fig8_multi_t1 | 42 % | **49 %** | 5 % | 4 % |
| fig8_multi_t2 | 50 % | **42 %** | 5 % | 2 % |
| fig8_multi_t4 | 80 % | 18 % | 1 % | 1 % |

O estágio inicial bate (embedding = deformação plástica ✓). **A cauda
NÃO**: o modelo a põe em wear de **bearing** (Archard na face de apoio),
os autores em fretting entre **flancos de rosca**. Creep é 1–4 % ⇒ a
re-atribuição do LIU_2016 (creep→flanco) **não** é a daqui; esta é
bearing→flanco.

## Candidato (mesma maquinaria adotada no LIU_2016, per-rig)

Ligar o canal de flanco (`flank_wear_on=1`, `flank_amp_exp=1.5` — KB) e
transferir a intensidade do canal de bearing para ele: `k_wear_flank`
lido do resíduo, com `k_wear_scale_tr` reduzido na mesma medida. **≤2
números**, nenhum deles inventado: o expoente vem da KB (LIU_2016) e a
intensidade é leitura de resíduo (rota `provenance.floor_from_curve`).

## Gates (imutáveis)

- **G0 (direção)**: sonda de 2 pontos ANTES de qualquer bisseção — se
  ligar o flanco não move as 3 na direção certa, PARA (canal inerte
  nesta fonte; registrar e encerrar).
- **G1 (as 3 da fila)**: as três fecham as pernas que hoje violam
  (`t1` MAE+σ, `t2` MAE, `t4` σ) **ou** a soma dos MAE das 3 cai ≥20 %.
- **G2 (nenhum caso pior — a fonte tem 21 curvas)**: **nenhuma** das 21
  piora >+0,01 em qualquer perna. Esta é a barra dura: 18 passam hoje.
- **G3 (procedência)**: `flank_amp_exp` da KB; `k_wear_flank` lido do
  resíduo; a re-atribuição citada ao texto dos autores no `prov`.
- **G4 (sincronia)**: adoção ⇒ fingerprint muda ⇒ re-stamp uniforme +
  `exemplo_m12_sintetico` direto + censo/_VIVAS/docs/páginas/suíte no
  mesmo commit.
- Ramo INCONCLUSIVO: G0 falha ⇒ nenhuma adoção; a fonte fica na fila com
  o desacordo modelo-vs-autores documentado (que já é resultado).

## Previsão registrada

O flanco escala com amplitude (`flank_amp_exp`=1,5) e a fonte roda
amplitude ÚNICA (0,3 mm) ⇒ **o expoente não é discriminável aqui**; o que
pode mudar a FORMA é a dependência do flanco com F₀/slip ao longo da
cadeia de reapertos. Risco declarado: se o flanco for apenas um wear
renomeado nesta condição, o G0 dá Δ≈0 e o candidato morre barato — que é
o resultado esperado se a distinção bearing-vs-flanco não for observável
com uma amplitude só.
