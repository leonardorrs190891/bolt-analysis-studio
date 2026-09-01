# LIU_2016 — re-atribuição da cauda ADOTADA: fretting L1 no lugar de "creep alto" — 14/14 no tripé

**2026-07-30 (noite)** · prereg `2026-07-30-liu2016-fretting-flank-prereg.md`
· execução `liu2016_fretting_exec.{py,json}` · **gates 5/5, adotado por
delegação (mandato 2026-07-30)**.

## O que foi adotado (entry `LIU_2016`; `LIU_2016_mos2` intocada)

| campo | valor | procedência |
|---|--:|---|
| `flank_wear_on` | 1.0 | canal L1 existente (força-modo; li2022ti/Liu2020) |
| `flank_amp_exp` | 1.5 | âncora KB (Liu 2020: 1,5–1,6; mesmo valor do li2022ti) |
| `k_wear_flank` | **4.325e-14** | mapa linear B↔K (G1, 2 sims, ±9,8 %); B=6,0e-8 lido do resíduo (L24) |
| `trim_n_max` | `{"run2": 2.2e6}` | recuperação por debris (Fig. 7 inset, +0,7 pt, terceiro corpo — out-of-model documentado) |

⚠️ **Errata de plumbing na mesma noite**: a 1ª escrita da adoção pôs o trim
em `per_case.run2.trim_n_max` — chave que o runner **não lê** (`_trim_n_for`
consome só `cfg.trim_n_max`, escalar ou `{token:N}`). O 1º restamp devolveu o
run2 à janela cheia e a triagem denunciou (`LIU_2016 ×1` na fila). Corrigido
para `cfg.trim_n_max={"run2":2.2e6}` + 2º restamp. O prereg §1 carregava a
chave errada — o erro era meu, mecânico, e o trim declarado é o mesmo; gates
não foram re-litigados. Gotcha gêmeo registrado no CLAUDE.md.

`C_creep=1.901e-11` **fica** (λ=0 no ótimo): a re-atribuição é ADITIVA — o
canal certo entra, o nível que o creep carregava não é demolido.

## Por que é legítimo

1. **O dado manda**: os AUTORES atribuem a cauda lenta a fretting nos
   filetes (SEM/EDX, delaminação no 1º filete) e o paper não contém a
   palavra creep. O modelo carregava a cauda com a lei errada — e era ISSO
   que o F1 do creep-compartilhado tinha detectado de manhã (a lei log não
   tem dependência de amplitude; o fretting tem, de graça).
2. **Forma já existente + âncora**: nada novo no engine; o expoente 1,5 não
   foi fitado aqui (KB). Só K per-par foi calibrado (2 sims) do B lido.
3. **Held-out generaliza**: m40nm e run2@trim fora do fit E da restrição —
   mediana 0,0303→0,0223, zero pioras (G3).
4. **Superposição exata**: 13 sims vs previsão analítica, desvio máx
   **0,0004** (G2: 0 fora de ±0,005).
5. **Acervo limpo**: nenhuma curva piora >+0,01; controle mos2 Δσ=0,0000
   exato (config separada não foi tocada — G4).

## Números (sim real, store-comparável)

Fila (4): m30nm 0,0281→**0,0227** · run1 0,0281→**0,0225** · m40nm (held)
0,0269→**0,0223** · run2@trim (held) 0,0303→**0,0192**. Acervo: m35
0,0164 · m45 0,0145 · m50 0,0133 · af7p5 0,0092 · af8p75 0,0083 · af10
0,0102 · af11p25 0,0115 · af12p5 0,0150 · dry 0,0179. **13/13 da config no
tripé** (MAE máx 0,0477; mx máx 0,0740) ⇒ fonte **14/14** com a mos2.

## O trim do run2 (declaração permanente)

A janela pontuada termina em 2,2×10⁶ ciclos porque dali em diante o dado
RECUPERA pré-carga (+0,7 pt até ~4×10⁶): debris de wear abrasivo empilhando
e escorando a junta (atribuição dos próprios autores). O engine é
monotônico por construção — nenhum mecanismo devolve F₀ — logo a feição é
out-of-model documentada, classe dos trims de fratura. Robustez: cortes em
2,0/2,2/2,5×10⁶ dão o mesmo veredicto. **Publicar sempre as duas janelas**:
cheia (sd 0,0328, fora) e trimada (0,0192, dentro). E a separabilidade
ficou provada: família sem trim NÃO fecha run2; trim sem família também
NÃO (sd 0,0303).

## Instrumentos que ficam

O crash da 1ª execução foi um `Δ` (U+0394) num print — cp1252 não tem o
char; as 13 sims já tinham batido ao 4º decimal quando o processo morreu no
print do controle. Regra ASCII reafirmada + `PYTHONIOENCODING=utf-8` de
cinto. E o `trim_n_max` NÃO passa pelos overrides do runner — a sonda
embrulha `rn._trim_n_for` (gotcha novo no CLAUDE.md).

## Efeito esperado no censo (conferir pós-restamp)

Fila 23 → **19** (−4). Tripé 127 → **≈133** (fila-4 + m45nm/dry e afins que
violavam MAE fora da fila). Números finais na triagem do restamp.
