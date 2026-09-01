# PREREG — `lu2024_fig20_T10Nm`: a lei de pressão (medida NESTA fonte) + o piso LIDO do terminal publicado

**2026-08-19 (17:2x)** · **gates congelados neste commit** · store em re-stamp
da adoção SUN (146 será conferido sobre o carimbo final) · mandato das 17:18:
*"trabalhe em …lu2024_M8_fig20_T10Nm.html"*.

## 1. Por que agora — o que mudou desde a falsificação de 16/08

No dia 16 o par (emb_pressure × floor) **fechava com folga** e foi recusado
porque o floor 0,34 era **fit por curva sem procedência**. Dois fatos novos:

1. **O precedente de hoje** (adoção SUN standard): floor **lido pelo leitor
   canônico com `plateau=False` declarado como LIMITE INFERIOR** é procedência
   aceita — foi exatamente assim que o 0,0284 da SUN entrou.
2. **O leitor, rodado na T10, dá 0,3195** — e o terminal dela é **PUBLICADO**
   (Tabela 9: retenção 0,309 em c100; o texto da p.19 dá 1845 N). O piso lido e
   o número do paper coincidem a 3 %.

## 2. O pacote

| peça | valor | procedência |
|---|---|---|
| `emb_pressure_exp` (**nível de GRUPO**) | 3,0 | capacidade construída em 16/08 **com a lei medida NESTA fonte** (excesso de 1º ciclo ∝ 1/F₀, r=+0,995; controle negativo no CACCESE passa). 1 fitado. Isolamento **estrutural**: só T4 e T10 têm p < p_ref; as outras 11 ficam em S=1 exato |
| `loose_arrest_floor` (**per_case T10**) | 0,3195 | **LIDO** (`arrest_floor_from_curve`, plateau=False ⇒ limite inferior declarado — estatuto do precedente SUN) e ancorado no **terminal publicado** (Tabela 9: 0,309) |
| `arrest_approach_exp` | 1,0 (default) | — |

O floor 0,10 do grupo (*"PR-15 re-fit COMPARTILHADO"* = **fitado**) permanece
para as irmãs; a T10 passa a usar o lido dela. Não-monotonia dos terminais da
fonte (0,037…0,309): é exatamente por isso que o piso é **por curva lida**, não
lei de F₀ — a rota de lei foi falsificada em 16/08 e continua falsificada.

## 3. Medições pré-gate (sandbox, já feitas)

- Grade (n_p × floor × aexp): **4 células fecham** (0,70×–0,89×), interior;
  melhor = (3,0 · 0,3195 · 1,0) → **0,0198 / 0,0344 / 0,0176**.
- As 13 do LU com o pacote: **11 IDÊNTICAS bit-a-bit** · T10 **fecha** (MAE
  −0,2316) · T4 (declarada por escopo) **melhora** −0,1857. Nenhuma piora.

## 4. GATES — congelados

| # | gate | critério |
|---|---|---|
| **G1** | alvo fecha o tripé | 0,0198 / 0,0344 / 0,0176 ao dígito pelo caminho canônico |
| **G2** | fonte | nenhuma das 12 piora > +0,01; as 3 do tripé (fig18_amp0p25, amp2p0, T22Nm) seguem; T4 pode melhorar (declarada — não conta como ganho) |
| **G3** | isolamento | Δ=0 exato fora do LU_2024 no re-stamp |
| **G4** | re-stamp íntegro | fingerprint único nos 210 (com o gotcha do sintético) |
| **G5** | censo | **+1 pela T10** sobre o carimbo que incluir a adoção SUN (145→146; conferido no store final) |
| **G6** | sincronização | triagem/forma nomeada/docs vivos/aging; HTML completo |

## 5. Predições registradas

1. G1 ao dígito. 2. T10 **sai das abertas** — a fila form-limited volta a
**ZERO**, agora por mérito e não por artefato. 3. T4 melhora mas **continua
declarada por escopo** (o paper a exclui: *"does not reach the tightening
effect"*) — melhoria de brinde não muda estatuto. 4. As duas primeiras curvas a
fechar por trabalho de modelo no mesmo dia (SUN standard e T10) usam a mesma
estrutura: forma certa + constante com procedência de leitura.


## Estado

EXECUTADO 2026-08-19 (17:3x-18:0x): G1 ao digito (0,0198/0,0344/0,0176 — FECHA), 11 irmas bit-identicas, T4 melhora de brinde; censo 145->146 no re-stamp 4c14f69f1d81. Fila form-limited a ZERO por merito.
