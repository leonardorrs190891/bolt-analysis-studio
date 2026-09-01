# Prereg — `k_emb_renew` por PROTOCOLO (soltar vs não soltar)

**2026-08-04** · decisão D-F (por delegação, mandato 2026-07-30) · gates
escritos **antes** de medir a resposta do held-out. Fingerprint de partida:
`63722b266dc0`. Antecedente obrigatório: `liu2022_fig8_cadeia_resultado.md`
(a TENDÊNCIA foi falsificada; isto aqui é uma hipótese **diferente**, sobre
NÍVEL, e não recicla o mesmo teste).

## A hipótese, e a procedência é do paper

A nota de aparato registra os dois protocolos de reaperto do Liu 2022, com
as palavras do artigo: **(i) direto ao torque alvo** — restaura só **88–90 %**
de F0; **(ii) soltar 30°–60° e reapertar** — restaura **~100 %** (método
recomendado). A mesma nota deixa a pergunta em aberto: *"retightening curves
show whether δ_emb should reset on retighten"*.

Medido no dado, perda **no 1º reaperto**:

| | release (solta) | direto/multi (não solta) | razão |
|---|---:|---:|---:|
| dry | 6,86 % | **2,22 %** | 3,1× menos |
| oil | 4,85 % | **2,78 %** | 1,7× menos |

**Reaperto sem soltar perde menos, nas duas lubrificações.** Leitura física:
soltar 30–60° separa as superfícies ⇒ elas re-assentam ⇒ o assentamento
(δ_emb) **renova**; apertar direto mantém a interface engajada e conformada
⇒ δ_emb **não renova**. O modelo hoje usa `k_emb_renew = 1,0` (renovação
TOTAL) nas quatro cadeias, inclusive nas que não soltam.

**Claim:** `k_emb_renew < 1` nos protocolos que **não soltam**
(`fig7a_oil_direct`, `fig8_multi`); `= 1,0` nos que soltam (`fig6a`, `fig6b`)
e no aperto virgem (`fig5`).

## Escopo: UM número, dois protocolos, held-out de outra lubrificação

| grupo | curvas | protocolo | `k_emb_renew` |
|---|---:|---|---|
| `LIU_2022_RETIGHT_fig8` | 5 | dry, multi (não solta) | **X** (alvo) |
| `LIU_2022_RETIGHT_direct` *(chave nova)* | 4 | oil, direto (não solta) | **X** (held-out) |
| `LIU_2022_RETIGHT_dry` | 6 | dry release + virgem | 1,0 (controle) |
| `LIU_2022_RET` | 6 | oil release + virgem | 1,0 (controle) |

A chave nova é nomeada pelo **protocolo** (`direct`), não pela figura — é a
diferença entre uma constante com significado e um número por gráfico. O
token `direct` só ocorre nos 4 cids do fig7a; o prefixo `LIU_2022_RETIGHT`
é mais longo que `LIU_2022_RET`, logo vence sem empate (a armadilha de
score empatado que já matou uma config em silêncio no YANG_2019).

## Gates (IMUTÁVEIS a partir daqui)

- **G0 (escolha do valor — procedência, não minimização):** adotar o
  **MAIOR X** (o mais brando, mais próximo de 1,0) que feche `t1` **e**
  `t2`. Varredura declarada: `X ∈ {0,9 · 0,8 · 0,7 · 0,6 · 0,5 · 0,3}`.
  Explicitamente **proibido** escolher o X de menor MAE: o `t1` precisa de
  −0,0033 de MAE e a dose de 0,3 entrega −0,0274 (8× o necessário), que é
  minimização disfarçada. Mesma disciplina da adoção do `GA_member`
  (2026-08-02), onde o limite foi fixado pelo regime.
- **G1 (HELD-OUT — o gate que decide):** as **4** curvas do
  `fig7a_oil_direct` estão **todas no tripé** hoje (MAE 0,0069–0,0149).
  Nenhuma pode **sair**, e a soma dos 4 MAE não pode piorar mais de
  **+0,010**. Este é o gate de mecanismo: se X ajuda a fig8 e atrapalha a
  fig7a, a claim "é o protocolo" está **falsificada** e o número é fit da
  fig8.
- **G1b (predição registrada, para poder errar por escrito):** se o
  mecanismo for real, a fig7a deve **melhorar**, porque ela sofre do mesmo
  defeito na mesma direção (t1: dado perde 2,78 %, modelo 5,76 % — o modelo
  perde 2,1× demais). Registro: **espero melhora**, não só ausência de
  piora. Se der ausência-de-piora-sem-melhora, dizer isso e não vender como
  confirmação.
- **G2 (controle de isolamento):** as **12** curvas de `fig5`/`fig6a`/`fig6b`
  ficam **bit-idênticas**. Qualquer mudança = a chave nova vazou de grupo.
- **G3 (nenhum caso pior):** nenhuma das 9 curvas dos grupos alterados
  piora > **+0,010** em qualquer perna. **Inclui o `t4`.** Declarado agora,
  antes de medir: o `t4` é a curva de **fratura por fadiga** (documentada
  no registry, na nota e no `CLAUDE.md` desde antes desta sessão) e a dose
  de 0,3 do G0 anterior a piorava **+0,0337**. **Não vou declarar o `t4`
  fora do censo para desbloquear este gate** — se o X mais brando que
  fecha t1/t2 estourar o +0,010 no t4, o ramo é NÃO ADOTA, e o estatuto do
  t4 vira decisão separada com prereg próprio. Declarar por conveniência
  inverteria a ordem da prova.
- **G4 (ganho):** `t1` **e** `t2` entram no tripé. Uma só ⇒ adoção
  **parcial declarada**. Nenhuma ⇒ não adota.
- **G5 (procedência escrita):** o `prov` do cfg cita o protocolo do paper
  (i)/(ii) e diz que X é **fit de 1 número** sob esse protocolo — sem
  fingir que veio de handbook.
- **G6 (sincronia):** adoção ⇒ fingerprint muda ⇒ re-stamp uniforme dos
  210 + censo/docs/páginas/testes no MESMO commit.

### Ramos do veredicto

- **ADOTA** — G0 ∧ G1 ∧ G2 ∧ G3 ∧ G4.
- **FALSIFICADO (é fit da fig8, não protocolo)** — G1 falha: X ajuda a fig8
  e tira curva da fig7a do tripé.
- **NÃO ADOTA (t4 bloqueia)** — G4 passaria mas G3 estoura no t4; registrar
  e mandar o estatuto do t4 para decisão própria.
- **INCONCLUSIVO** — a chave nova não resolve (empate/prefixo), ou
  `k_emb_renew` sai inerte na fig7a por companheiro desligado. Ramo
  obrigatório: sem ele o script escolhe entre PASSA e FALSIFICADO e
  escreve veredicto sobre teste vazio.

## O que este prereg NÃO afirma

Não afirma a tendência. O dobramento da perda por reaperto
(1,78×/1,99× na fig8) segue **não modelado** e falsificado para a família de
constantes — ver `liu2022_fig8_cadeia_resultado.md`. Fechar t1/t2 por nível
não fecha a forma, e o texto de adoção (se houver) tem de dizer isso.
