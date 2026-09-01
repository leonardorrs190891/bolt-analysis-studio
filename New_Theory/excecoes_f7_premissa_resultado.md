# Camada de exceção auditada: **0 pernas descobertas** — mas 7 provas citam números que o store não tem mais

**2026-08-07 (madrugada)** · `excecoes_f7_teste_premissa.py` (só-leitura) ·
**nada retratado** — camada de exceção é assinada.

## O resultado principal: a camada está SÃ

Das 23 exceções vivas, **7 são F7** (prova de piso, teste de três pernas) e
**16 são F5** (critério de *scatter de réplicas*, desvio-à-mediana — outro
teste). Confrontando cada prova F7 com o piso **que ela própria cita**:

**Zero pernas descobertas.** As sete continuam cobertas.

Isso fecha a pergunta que motivou o tick: os pisos mudaram esta noite (o D-Y
mexeu nos três do KARLSEN) e a `run14p2` ficou descoberta por isso — havia razão
para suspeitar de outras. Não há.

## ⚠️ A primeira versão deste script deu "8 descobertas". Era artefato duplo

Registro porque o erro é reproduzível por quem repetir a auditoria:

1. **Barra errada.** Comparei contra a **média da fonte** (`por_fonte`), quando
   as provas do LU foram assinadas contra o **piso POR CONDIÇÃO** — o
   `CLAUDE.md` é explícito: *"a barra usa o piso da MESMA condição … nunca a
   média da fonte"*. Com a média, a `T10Nm` aparecia descoberta (0,2592 >
   0,2501) quando a prova dela usa **0,613**.
2. **Categoria errada.** Apliquei o teste de três pernas às **16 exceções F5**,
   cujo critério é *scatter de réplicas* e não envolve piso por perna. Comparar
   coisas distintas produz reprovação onde não há regra violada.

Nenhum dos dois números foi publicado.

## O que de fato aparece: 7 pares valor/piso DERIVADOS

| curva | perna | prova | store | Δ |
|---|---|---:|---:|---:|
| `lu2024_M8_fig18_amp0p5` | MAE | 0,0610 | **0,1245** | **+0,0635** |
| `lu2024_M8_fig20_T10Nm` | MAE | 0,2090 | 0,2592 | +0,0502 |
| `lu2024_M8_fig20_T16Nm` | MAE | 0,1230 | 0,1672 | +0,0442 |
| `lu2024_M8_fig20_T10Nm` | σ | 0,1160 | 0,0767 | −0,0393 |
| `lu2024_M8_fig20_T10Nm` | mx | 0,2990 | 0,3310 | +0,0320 |
| `lu2024_M8_fig20_T28Nm` | MAE | 0,1190 | 0,0984 | −0,0206 |
| `lu2024_M8_fig20_T22Nm` | MAE | 0,1100 | 0,0923 | −0,0177 |

Todos no **LU_2024**, o que é coerente: a correção de *drive* de 2026-07-31 e as
re-simulações posteriores moveram aquela fonte. As duas do ECCLES derivam
**0,0000–0,0004** — provas escritas contra um store que não mudou.

⇒ é o **§4.43 dentro da camada de exceção**: a prova continua válida, mas o
texto dela descreve uma simulação que não existe mais. Candidato a **re-stamp**
de texto (contabilidade, não política) — não executado, porque reescrever
registro assinado é decisão sua mesmo quando o veredicto não muda.

## ⚠️ E uma observação que não é confortável

A `fig18_amp0p5` **dobrou** de MAE (0,061 → 0,1245) e a prova nem estremece,
porque o piso citado é **0,281** e a barra FORTE dela fica em 0,199. Na
`T16Nm` a folga é maior ainda: piso **0,613**, barra FORTE **0,433**, modelo
**0,167** — **2,6× de margem**.

**Uma prova que absorve o dobro do erro sem se abalar não está discriminando
muito.** Isso não invalida nada — os pisos do LU são grandes porque o *scatter*
entre réplicas daquela fonte é grande, e isso foi medido. Mas registra-se que a
força dessas cinco exceções vem do **tamanho do piso**, não da proximidade do
modelo.

⚠️ **Interage com P-8:** se as CSVs do LU forem corrigidas, o piso da fonte
**sobe 32 %** — e a folga dessas provas sobe com ele. Corrigir o dado tornaria
essas exceções *ainda menos* discriminantes, o que é um custo que a P-8 não
listava.

## Reprodutibilidade

```bash
py -3.12 New_Theory/excecoes_f7_teste_premissa.py --json New_Theory/excecoes_f7_teste_premissa.json
py -3.12 New_Theory/declaracoes_teste_premissa.py --json New_Theory/declaracoes_teste_premissa.json
```

## Estado das três camadas, auditadas na mesma madrugada

| camada | n | premissa se sustenta? |
|---|---:|---|
| exceções F7 | 7 | **7/7** (0 pernas descobertas) |
| exceções F5 | 16 | critério distinto, não testado aqui |
| declarações — colapso | 3 | **3/3** (res.máx a 0–1 índice do penhasco) |
| declarações — `n<6` | 3 | **3/3** (mae/mx passam com folga) |
| declarações — resolução | 6 | **3/6** ⇒ **P-10** |
| declarações — escopo | 4 | sem premissa numérica |
