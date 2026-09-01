# Adoção ASSINADA — `fret_freq_exp` = 1,0 per-fonte no LI_2022_TRIBOINT (P-1)

**2026-08-06 (tarde)** · **ASSINATURA DO PROFESSOR em sessão**, com as opções e
os custos na mesa: *"Assinar com valor 1,0"* — contra a alternativa 0,92
(centro da janela, margem ~1,7 %) e contra manter na fila. Decisão **D-V**.
Fingerprint de partida `b70276f2fa43` (pós-D-U).

## O que a assinatura declara (e que a campanha NÃO podia declarar sozinha)

1. **`fret_freq_exp` é constante PER-FONTE, sem held-out na biblioteca.** O
   único outro grupo com canal de flanco (LIU_2016) é de frequência ÚNICA —
   medido em 2026-08-05: aplicar a lei lá testaria rescale uniforme, não a lei.
   A regra de transferência ("o valor do candidato está na transferência") fica
   **conscientemente relaxada para este caso**, por assinatura — era o P-1 da
   fila, e é exatamente o tipo de decisão que o mandato reserva ao professor.
2. **Valor 1,0 pela âncora física dupla**, aceitando a margem fina: taxa de
   fretting ∝ 1/f (desgaste por unidade de TEMPO, não por ciclo — ejeção de
   detritos e oxidação são processos temporais), e é o expoente que o DADO pede
   independentemente (`a` = 1,006 no par 10–20 Hz; 0,978 global; banda
   [0,603 · 1,415] exclui zero). Margem declarada e aceita: σ da `full` fica a
   **0,4 %** do limite (0,0249 vs 0,025).

## Procedência da medição (nada novo é fitado aqui)

Janela medida em 2026-08-05 (`li2022_fret_freq_exp_resultado.md`, commits
`4df3161`+`da5a93a`): [0,85 · 1,02] fecha a fonte em **4/4**; o valor derivado
3,57 foi FALSIFICADO por gate (G2: a `full` saía); 1,0 está dentro da janela.

## Predições registradas (da varredura, célula exp = 1,00; rota override ≡ config verificada no D-Q)

| curva | hoje (mae/mx/σ) | PREVISTO |
|---|---|---|
| `axial_10Hz_full` | 0,0227/0,0534/0,0214 | 0,0217/mx<0,10/**0,0249** |
| `axialmin_10Hz` | 0,0589/0,0802/0,0226 | **0,0481**/mx<0,10/0,0215 — **ENTRA** |
| `axialmin_15Hz` | 0,0323/0,0497/0,0166 | **inalterada** (pivô da lei em ~15 Hz) |
| `axialmin_20Hz` | 0,0146/0,0431/0,0179 | 0,0110/mx<0,10/0,0140 |

**Efeito previsto: fonte 4/4 · censo estrito 137→138 · fila form-limited 1→0.**

## Gates da execução (IMUTÁVEIS)

- **G1 (predições):** as 4 curvas dentro de ±0,02/perna do previsto. Fora ⇒
  INCONCLUSIVO, investigar sem re-stampar.
- **G2 (isolamento estrutural):** `fret_freq_exp` entra SÓ no grupo
  `LI_2022_TRIBOINT`; o LIU_2016 (o outro grupo com canal de flanco) fica
  intocado e isso é verificado por re-sim (bit-idêntico).
- **G3 (re-stamp uniforme):** adoção muda o fingerprint ⇒ batch dos 202 +
  re-sim direta do `exemplo_m12_sintetico` ⇒ fingerprint único nos 210; as
  curvas fora de LI_2022 saem **bit-idênticas** (só o carimbo muda).
- **G4 (sincronia):** censo + docs vivos + reports + suíte no MESMO commit;
  P-1 → DECIDIDA em `DECISOES_PENDENTES.md`; charter MARGENS junto.

### Ramos

**ADOTA** (G1–G3) · **INCONCLUSIVO** (G1 falha — nada escrito além do rollback
do config pelo backup) · a reprovação por margem NÃO é ramo: a margem de 0,4 %
foi posta na mesa e assinada.
