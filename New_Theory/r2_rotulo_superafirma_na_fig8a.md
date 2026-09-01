# O rótulo que EU adotei há 3 h super-afirma na `fig8a` — e é o defeito que o R2 existia para matar

**2026-08-16 (21:0x)** · só-leitura · **nada executado** · store `7a60cacb72de`, censo
**144/205** · **correção proposta, aguarda assinatura**.

---

## 1. O que eu gravei no config às 17:2x

A adoção **R2** (item R, gates 6/6) trocou o `prov.loose_arrest_floor` de **dois** grupos do
`ECCLES_2010` — `fig7d` e `fig8a` — por **um mesmo texto**:

```
proxy-de-desaceleracao-de-cauda (fitado-this-rig; NAO e leitura do dado: a leitura
L24 do CSV cru da 0.0000 na fig7d e 0.0122 na fig8a, com plateau=True. O valor
aqui imita a desaceleracao MEDIDA da cauda -- dado leva 1643 ciclos de 0.25 a
0.10 e o modelo 16 -- porque loose_arrest_floor e' a unica alavanca anti-runaway
do engine. ...)
```

⚠️ Os números da justificativa (**1643 contra 16**) são da **`fig7d`**. Eu os apliquei à
`fig8a` **por analogia**, nunca por medição. Foi o que este documento foi testar.

## 2. Medido: a `fig8a` NÃO tem desaceleração de cauda

Ciclos em que o **dado cru** cruza cada nível:

| curva | 0,40 | 0,25 | 0,15 | 0,10 | razão do trecho final |
|---|---:|---:|---:|---:|---:|
| **`fig7d`** | 100 | 153 | **1626** | 1643 | **10,6×** (0,25→0,15) |
| **`fig8a`** | 124 | 166 | 203 | 226 | 1,34 · 1,22 · **1,11** |

⇒ na `fig7d` o dado **trava**: gasta 10,6× mais ciclos para descer o mesmo degrau. Na
`fig8a` ele desce **suavemente até o fim** — os intervalos encurtam, não alongam.

**E o piso age de forma coerente com isso:**

| curva | nível | modelo c/ piso | modelo s/ piso |
|---|---:|---:|---:|
| `fig7d` | 0,15 | 186 | 125 |
| `fig7d` | **0,10** | **nunca** | 130 |
| `fig8a` | 0,15 | 163 | 145 |
| `fig8a` | 0,10 | 173 | 150 |

Na `fig7d` o piso **arresta** (o modelo nunca chega a 0,10, como o dado quase não chega).
Na `fig8a` ele só **atrasa uniformemente** ~12 % em todos os níveis — o modelo continua
chegando ao fim.

*(Nota de engine: o piso age acima do próprio valor porque `self_locking_gate` é
**S-curve suave**, não clamp — está no `CLAUDE.md`. Não é anomalia.)*

## 3. ⇒ O rótulo da `fig8a` está errado, e o erro é do tipo que o R2 combatia

| grupo | o rótulo afirma | o dado mostra | veredito |
|---|---|---|---|
| `fig7d` | imita desaceleração de cauda medida | 10,6× de travamento | ✅ **verdadeiro** |
| `fig8a` | idem (com os números da `fig7d`) | decaimento **suave**, sem travamento | ⛔ **super-afirma** |

O que a `fig8a` de fato tem é **erro de TAXA uniforme**: o modelo é ~12–25 % rápido em todo
o percurso, e o piso compensa isso **atrasando parelho**. Isso é uma coisa legítima para uma
constante fazer — só não é o que o rótulo diz.

⚠️ **A ironia é o ponto:** o R2 existiu para corrigir um rótulo que afirmava mais do que a
medição sustentava, e eu **cometi o mesmo erro dentro do conserto**, ao reusar um texto
justificado numa curva para uma segunda que não o fora. **Rótulo compartilhado herda a
justificativa da curva onde ela foi medida** — e ninguém percebe, porque o texto é idêntico.

⚠️ **A guarda S1 NÃO pega isto**, e a limitação é estrutural: ela checa se um rótulo
`lido-do-dado` bate com o dado. Aqui o rótulo **não** diz `lido-do-dado` (diz
`fitado-this-rig`), então está fora do escopo dela **por construção**. ⇒ o item S media
"85 % das afirmações são infalsificáveis"; esta é uma delas, e caiu por medição manual —
exatamente como as duas do R2.

## 4. Proposta — **aguarda assinatura** (mexe em config adotada)

| # | ação | efeito |
|---|---|---|
| **T1** (recomendada) | **separar os dois rótulos**: `fig7d` mantém o texto atual (é verdadeiro lá); `fig8a` recebe texto próprio — *"compensa erro de TAXA uniforme (~12 % de atraso parelho); a cauda desta curva NÃO desacelera: dado gasta 124/166/203/226 ciclos para 0,40/0,25/0,15/0,10"* | censo **0** |
| **T2** | generalizar o texto atual para cobrir os dois sem citar números de nenhum | censo 0, mas **perde** a procedência específica — pior |
| **T3** | não mexer | ⛔ deixa no config uma afirmação que a medição contradiz, três horas depois de eu ter adotado um item **contra** isso |

**Recomendo T1.** ⚠️ E ela **muda o fingerprint** e obriga re-carimbo dos 210, pelo mesmo
motivo do R2 (o hash cobre a entry inteira, incl. `prov`) — não é edição cosmética.

⛔ **Não executo** — mudança de config adotada exige assinatura (protocolo do cron, passo 4).

## 5. Regra que isto sugere para o futuro

**Rótulo de procedência não deve ser copiado entre grupos sem re-medir a justificativa
naquele grupo.** O texto idêntico é o que torna o defeito invisível: dois grupos, uma
medição, e nada no arquivo denuncia qual das duas curvas foi de fato medida.

## Reprodutibilidade

Sonda inline no corpo do commit: `load_full_curve` (CSV **cru**, nunca `metric_data`),
`runner.simulate_case` com `_prefit_overrides={'loose_arrest_floor': 0.0}` para o contraste,
e cruzamento por interpolação linear no 1º ponto abaixo de cada nível.
