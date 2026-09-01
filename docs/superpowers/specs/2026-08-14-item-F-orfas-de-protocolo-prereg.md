# Prereg — **item F**: declarar as 8 órfãs de protocolo do `LU_2024`

**2026-08-14** · assinatura em bloco do professor (*"assine tudo e continue"*) · gates
**IMUTÁVEIS** depois desta linha.

## Estado

⏳ **PENDENTE** — escrito antes de executar.

## O que se declara, e com que prova

As **8** curvas que hoje formam **a fila form-limited inteira do projeto** passam a
`_DECLARADAS` com o estatuto **"órfã de protocolo"**:

```
lu2024_M8_fig14_amp0p25_long   lu2024_M8_fig18_amp0p5    lu2024_M8_fig20_T16Nm
lu2024_M8_fig14_amp0p5_long    lu2024_M8_fig18_amp1p5    lu2024_M8_fig20_T22Nm
lu2024_M8_fig14_amp1p0_long                              lu2024_M8_fig20_T28Nm
```

**Prova, em quatro instrumentos independentes** — nenhum deles opinião:

1. **O paper separa os protocolos.** §3.1.3 = half-sine de **máquina** a 1 Hz (as corridas
   longas `fig14_*_long`); §3.2 = controle **manual**, que o texto diz *"eliminar os efeitos
   da half-sine"* (p. 15). ⇒ os pares que davam piso cruzavam **ensaios diferentes**, e as 5
   exceções F7 que repousavam neles foram **retratadas** (`_EXCECOES_RETIRADAS_...`).
2. **O dado confirma sem o paper**: o platô até F/F₀ = 0,90 dura **27–56 ciclos** na `fig14` e
   **1** nas `fig18/20`, **3 pares em 3**, sempre na mesma direção; e as janelas diferem
   (N = 1040 × 99).
3. **O modelo separa as duas famílias**: MAE 3–9× melhor nas `fig18/20`, com um caso em que a
   `fig18_amp0p25` **passa o tripé** e a "réplica" `fig14_amp0p25_long` reprova em 2–5×.
4. **Rota de modelo falsificada por medição** (`lu2024_halfsine_forma_onda_falsificada.md`):
   a hipótese "half-sine = metade do curso" melhora 42 % a `amp1p0` **em 0,50× exato**, mas
   **piora** a irmã de **mesma classe mecânica** — um fato físico não pode valer numa e não na
   outra. Falsificada como mudança de protocolo.

⇒ **sem rota de modelo, sem rota de piso, sem rota de dado** (fonte fechada).

## ⚠️ O que "declarada" significa aqui — e o que NÃO significa

**Declarada ≠ acerto do modelo.** A leitura estrita **continua 140/205** e é assim que deve
ser publicada. O que muda é a **leitura resolvida/declarada**, que passa a dizer: *estas 8 têm
procedência de por que não são trabalháveis*.

⚠️ **Custo de honestidade que fica escrito:** o modelo **erra** nestas 8, e erra feio em
algumas (`fig14_amp1p0_long` a **9,6×** o limite de MAE). Declará-las **não conserta nada** —
retira-as da fila de trabalho porque o instrumento de validação não as resolve, não porque o
modelo as acerte.

## Gates (congelados)

| # | gate | esperado |
|---|---|---|
| **F1** | as 8 entram em `_DECLARADAS` | 8/8 |
| **F2** | tripé **inalterado** | **140/205** |
| **F3** | `declarado_total` | 172 → **180** |
| **F4** | `fora_aberta` | 33 → **25** |
| **F5** | fila form-limited | 8 → **0** |
| **F6** | isolamento | nenhuma curva fora do `LU_2024` muda de camada |
| **F7** | as 4 guardas de hoje seguem verdes | pares declarados · piso de fonte · classe encerrada · `_VIVAS` |
| **F8** | suíte completa | verde |
| **F9** | docs vivos re-sincronizados **no mesmo commit** | `CLAUDE.md` e a fila com `declarado_total` = 180 |

⚠️ **F7 tem uma interação verificada e nula**: `LU_2024` **não** está em
`_FONTES_CLASSE_PARADA` (que é `CHU`, `JCSR`, `LIU_2025`, `YANG_2019`, `YANG_2021`), logo a
guarda da classe encerrada não pode se mover com isto. Se ela se mover, algo mais aconteceu.

## Rollback

`.bkp_F` em `report_html.py`. Qualquer gate divergente ⇒ restaura e registra.
