# Prereg — re-fit do grupo HDPE do ROUSSEAU (o dado mudou)

**2026-08-02** · decisão D-D (por delegação). Gates antes de medir.

## Por que o re-fit tem procedência

A `hdpe_t10` foi **re-digitalizada** contra alvo do próprio paper (Fig. 7)
e mudou de forma material: 16 → 165 pontos, retenção em N=100 de 67,2 →
62,8 %. O cfg vigente (`ROUSSEAU_HDPE`: `c_bend=0,5`, `emb_depth=5e-7`,
`GA_member=20000`, `loose_arrest_floor=0,2`) foi ajustado **contra a
versão errada**. Regra que já valeu para o aço após o erratum do drive:
**quando o dado muda, o fit feito contra o dado velho perde procedência**.

## Escopo e limites declarados

- Fitar **≤2 números** do grupo HDPE. Candidatos, em ordem de
  legitimidade: `GA_member` (rigidez de cisalhamento do membro — a que o
  PR-14 introduziu e a única com significado direto para HDPE) e
  `c_bend`. `emb_depth`/`floor` ficam **congelados** (o floor do HDPE tem
  procedência de aparato desde hoje: os roletes valem para o rig inteiro).
- **`k_j` NÃO entra**: medido hoje, 293× errado e ~1 % de efeito em modo
  deslocamento. Corrigi-lo é higiene de procedência, não alavanca — e
  mexer nele aqui confundiria as duas coisas.

## Gates (imutáveis)

- **G1 (ganho)**: soma dos MAE das 3 HDPE cai **≥15 %**.
- **G2 (nenhuma pior)**: nenhuma das 3 piora >+0,01 em qualquer perna;
  e as 3 do **aço** ficam **bit-idênticas** (grupo de cfg diferente — se
  mudarem, o override vazou).
- **G3 (held-out)**: a `hdpe_t10_amp0p2` (Fig. 6, condição inédita,
  **hoje no tripé por predição zero-refit**) **não pode sair do tripé**.
  Este é o gate duro: ela é a melhor evidência preditiva da campanha e
  não pode ser sacrificada por ganho de ajuste.
- **G4 (procedência)**: o valor adotado declarado por origem; se ficar
  longe da ordem física do HDPE (G·A ~ 0,4 GPa × área do membro), dizer.
- **G5 (sincronia)**: adoção ⇒ fingerprint muda ⇒ re-stamp uniforme +
  censo/docs/páginas/testes no mesmo commit.
- **INCONCLUSIVO**: se o ganho só vier às custas do held-out, **não
  adotar** e registrar — o fit que quebra a predição não é melhoria.

## Previsão registrada

A t10 nova perde mais (retém 62,8 contra 67,2) ⇒ o fit deve pedir **mais
perda**, o que no HDPE significa `GA_member` **menor** (membro mais
complacente ⇒ mais curso absorvido... ou o contrário, se o slip resolvido
subir). **Não sei o sinal** — por isso o G0 implícito é a sonda de 2
pontos antes de qualquer bisseção, como manda a regra do repo.
