# `s1_amp_gate` no YANG_2019 — **NÃO ADOTADO**, e a falsificação nomeia a forma que falta

**2026-08-07 (madrugada)** · `yang2019_s1gate_premeasure.py` + duas varreduras ·
só-leitura · autorização do professor era *"adote se os gates passarem"* — **eles
não passam**, então nada foi adotado.

## Autoridade: PLENA (e é o oposto do canal de frequência)

O gate multiplica o `d_delta` de **Embedding e Creep**. Como é multiplicador de
canal e não troca de lei, a decomposição decide se ele alcança o defeito.
Medida **no cruzamento de 90 %**, que é onde o defeito está:

| curva | N@90 mod | N@90 dado | **emb+creep @90 %** | emb+creep @fim |
|---|---:|---:|---:|---:|
| `amp0p4_5Hz` | 767 | 9015 | **100,0 %** | 93,7 % |
| `amp0p6_10Hz` | 175 | 4263 | **100,0 %** | 59,1 % |
| `amp0p6_5Hz` | 160 | 1900 | **100,0 %** | 55,1 % |
| `varamp_large_to_small` | 113 | — | **100,0 %** | 82,7 % |
| `varamp_small_to_large` | 175 | — | **100,0 %** | 86,9 % |

⚠️ **Ler a decomposição no FIM daria a conclusão errada** (55–94 % ⇒
"autoridade parcial"). No ponto onde o defeito vive ela é **100 %**. O reflexo
natural — olhar o acumulado final — subestimaria o candidato.

## Os gates: reprovado, e por trade-off estrutural

| célula | pior Δ (qualquer perna) | ganho de MAE (mediana) |
|---|---:|---:|
| dref 0,10 / 0,20 / 0,30 · floor 0 | +0,0000 … +0,0008 | **+0,0000 … +0,0001** |
| dref 0,40 · floor 0 | +0,0098 | +0,0003 |
| dref 0,50 · floor 0 | +0,0294 | +0,0005 |
| dref 0,60 · floor 0,85 | +0,0039 | +0,0003 |
| dref 0,60 · floor 0 | **+0,0374** | — |
| dref 0,70 · p 8 · floor 0 | **+0,0512** | — |
| dref 0,70 · p 12 · floor 0 | **+0,1115** | — |

**Toda parametrização forte o bastante para mover a métrica viola o gate de
+0,010; toda parametrização fraca o bastante para passar é inerte.** E em
**nenhuma** célula da grade fina (15 combinações) alguma curva entra no tripé
(`tripé 0 → 0` em todas).

### O que o gate faz, medido por perna

`dref 0,70 · p 8 · floor 0` (a de maior ganho de MAE):

| curva | Δ MAE | Δ res.máx | Δ σ |
|---|---:|---:|---:|
| `amp0p4_5Hz` | **−0,0497** | **+0,0512** | −0,0086 |
| `amp0p6_10Hz` | **−0,0207** | **−0,0292** | −0,0010 |
| `amp0p6_5Hz` | +0,0025 | **+0,0418** | +0,0015 |
| `varamp_large_to_small` | +0,0028 | +0,0152 | +0,0016 |
| `varamp_small_to_large` | +0,0001 | **+0,0416** | +0,0013 |

O gate **acerta o nível e estraga a forma**: suprimir o Estágio I mantém o
modelo alto no início, o que reduz o erro médio e cria um pico novo onde o dado
cai cedo.

## ⚠️ O diagnóstico fino — e é ele que vale o passo

A **`amp0p6_10Hz` melhora nas TRÊS pernas** (−0,021 / −0,029 / −0,001) enquanto
a **`amp0p6_5Hz` piora no res.máx** (+0,042). As duas têm a **MESMA amplitude**
(0,6 mm) e diferem **só na frequência**.

O gate depende **apenas de amplitude** ⇒ ele **não consegue distinguir as
duas**, e por isso não existe célula que sirva às duas. Não é questão de
calibrar melhor: é **incompatibilidade estrutural** entre a forma do candidato e
a do defeito.

### A forma que falta, dita com precisão

O relógio de Estágio I precisa de dependência de **FREQUÊNCIA**, e nenhum
mecanismo existente a oferece onde há autoridade:

| mecanismo | autoridade sobre a perda @90 % | depende de frequência? |
|---|---|---|
| `s1_amp_gate` (Embedding/Creep) | **100 %** | **não** (só amplitude) |
| `dmg_dwell_exp` (dano) | **teto** (razão 1,10 para expoente 0…8) | sim |

⇒ o candidato correto é **frequência nos relógios de Estágio I** — a
combinação que nenhum dos dois entrega. Isso é forma nova no engine, não
calibração, e portanto **fora do mandato de execução**: precisa de decisão sobre
implementar.

## O que a fonte oferece a quem for implementar

O YANG_2019 é o rig com melhor instrumentação para esse candidato:

* **dado auditado e BOM** — a `amp0p4_5Hz` bate a lei D-N impressa em 1,05/0,90
  (`yang2019_dn_auditoria_resultado.md`), sem erro de digitalização;
* **âncora independente para o relógio** — `d^m·N = C` da Tabela 5, publicada
  pelos autores, dá N previsto em 90/80/70 % por amplitude;
* **par de frequência controlado** — 0,6 mm a 5 e 10 Hz, tudo mais igual;
* **consistência interna**, que é justamente o que travou a adoção do
  `s1_amp_gate` no LIU_2025 (lá a Fig. 4 e as curvas discordam em 3–5×).

## Reprodutibilidade

```bash
py -3.12 New_Theory/yang2019_s1gate_premeasure.py --json New_Theory/yang2019_s1gate_premeasure.json
```
