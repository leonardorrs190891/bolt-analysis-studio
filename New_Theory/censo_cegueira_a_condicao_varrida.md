# O censo conta curvas; ele não conta **predições**. Medido: 3 curvas no tripé com resposta **ZERO** à variável varrida

**2026-08-14 (noite)** · só-leitura · **nada adotado** · store `c37618c5cc96`, censo **141/205**.

Sonda nova: `audit_cegueira.py`. Motivada por um round-trip do `QIN_2024` que validou o
dado e, de quebra, mostrou o modelo dando a **mesma** resposta às três condições.

---

## 0. A pergunta que a campanha nunca publicou

*"Passa no tripé"* e *"prevê o efeito"* são afirmações diferentes. Uma curva entra no censo
quando o erro cabe na tolerância — e o efeito que o experimento varreu **pode ser menor que
essa tolerância**. Nesse caso o modelo acerta o nível e erra a física inteira do ensaio,
sem que nenhuma métrica reclame.

**Método** (par a par, dentro da fonte, na janela comum, só entre curvas que **passam**):

```
d_dado = média |dado_i − dado_j|      d_mod = média |modelo_i − modelo_j|
razão  = d_mod / d_dado               razão ≈ 0 ⇒ o modelo não distingue as condições
```

Pares com `d_dado` abaixo do piso de digitalização (0,005) são descartados — ali o próprio
dado não separa.

## 1. ✅ A manchete honesta é boa: mediana **0,869**

**532 pares** do censo em que o dado separa as condições. **Mediana da razão = 0,869**,
p10 = 0,168, p90 = 1,672.

⇒ **tipicamente o modelo separa ~87 % do que o dado separa.** A campanha **não** é
largamente culpada de "passar pelo motivo errado". **64 pares (12 %)** ficam abaixo de 0,20.

A história está na cauda, e ela tem uma assinatura própria: **`d_mod = 0,0000 exato**"
(previsão idêntica em 60 pontos), não "pouca sensibilidade".

## 2. Os três clusters de previsão idêntica — e **um deles não é defeito**

| fonte | curvas | previsões distintas | veredito |
|---|---:|---:|---|
| `LIU_2020_WEAR` | 9 | **4** | ✅ **cegueira genuína** (§3) |
| `CACCESE_2009` | 7 | 5 | ⚠️ **NÃO é cegueira** (§4) |
| `GRZEJDA_2026` | 2 | **1** | posição do parafuso não modelada; 1 curva no censo |

## 3. ⚠️ `LIU_2020_WEAR`: resposta **exatamente zero** a uma varredura de 4× em amplitude

Varredura `fig9`, **P₀ = 18 kN fixo**, só a amplitude transversal muda:

| AF (mm) | perda do **dado** | fim do dado | **fim do modelo** | MAE | tripé |
|---:|---:|---:|---:|---:|:--:|
| 0,1 | 0,0120 | 0,9880 | **0,9650** | 0,0157 | ✅ |
| 0,2 | 0,0367 | 0,9633 | **0,9650** | 0,0050 | ✅ |
| 0,3 | 0,0665 | 0,9335 | **0,9650** | 0,0193 | ✅ |
| 0,4 | 0,1689 | 0,8311 | **0,9650** | 0,0729 | ✗ |

O dado varre **14× em perda**, de forma **monotônica e ordenada**. O modelo devolve
**0,9650 nas quatro**, ao dígito.

* sensibilidade do **dado**: `d(perda)/d(AF)` = **0,523 /mm**
* sensibilidade do **modelo**: **0,000 /mm**
* **cobertura: 0 %**

**Três dessas curvas estão no censo.** A quarta reprova **só porque o efeito finalmente
ultrapassou a tolerância** — não porque o modelo tenha começado a errar; ele errou o tempo
todo, do mesmo jeito.

### A causa está na config adotada, e é explícita

```
LIU_2020_WEAR:  K_archard = 0.0 · k_wear_spec = 0.0 · tr_loose_gain = 0.0 · C_creep = 0.0
                emb_um = 1.121 µm · N_emb
```

**Quatro dos cinco mecanismos de perda estão zerados.** Sobra o **embedding** — e as nove
curvas são casadas por uma exponencial de **dois parâmetros**.

⚠️ E não é cegueira global: no sweep de **pré-carga** da mesma fonte (12 / 18 / 24 kN) o
modelo **responde** (0,9475 / 0,9650 / 0,9738), porque a pré-carga entra no embedding. Ele é
cego **especificamente à amplitude transversal**, porque a config zera **exatamente** os
canais por onde a amplitude age (wear e afrouxamento rotacional são dirigidos por slip).

⇒ a varredura de amplitude desta fonte é **não-modelada por construção**, e o censo a conta
**três vezes** como acerto.

### ⚠️ O nome da fonte é `LIU_2020_**WEAR**`

É um artigo sobre desgaste, e o modelo o "valida" com o desgaste **desligado**. Isso **não é
automaticamente errado** — zerar canal que o dado não excita é a disciplina de parcimônia da
própria campanha, e o fit foi legítimo. O que não se pode fazer é somar as duas afirmações:
*"o ajuste é parcimonioso"* e *"o modelo prevê o que o experimento mediu"*. Aqui a segunda é
**falsa com número**.

Isto é `∂(perda)/∂A_F ≡ 0` — **a mesma falsificação do item 9 do roadmap**, que lá foi
re-baselinada para 77,7 % de cobertura no `LIU_2017_AXIAL`. Aqui, em amplitude
**transversal**, ela está **viva e em 0 %**.

## 4. ⚠️ `CACCESE_2009` NÃO é cegueira — e dizer o contrário seria injusto com o modelo

O cluster junta `protruding_45kN` + `tapered_45kN_rep1` + `rep2`. Tentador ler como "o
modelo não distingue a geometria que o paper existe para comparar". **Mas o dado não pede
essa distinção:**

| par | `d_dado` |
|---|---:|
| `tapered_rep1` × `tapered_rep2` (**réplicas da MESMA condição**) | **0,0549** |
| `protruding` × `tapered_rep1` | 0,0449 |
| `protruding` × `tapered_rep2` | **0,0101** |

⇒ **o scatter entre réplicas é MAIOR que o efeito da geometria.** Exigir que o modelo
separe condições cuja diferença é menor que o ruído do próprio dado seria exigir que ele
ajustasse ruído. Veredito: **inconclusivo por dado**, não defeito de modelo.

## 5. O que isto muda, e o que não muda

**Não muda** o censo (nada adotado, nada reclassificado) e **não** desmente o modelo em
geral — a mediana 0,869 é uma medição a favor dele, e é a primeira vez que essa medição
existe.

**Muda a leitura de uma fonte**: `LIU_2020_WEAR` está **8/9 no tripé**, o que se lê como
"o modelo vai bem aqui". A leitura correta é: **8 curvas, 4 predições distintas, e a
varredura de amplitude com resposta zero.**

## 5b. ✅ POR FONTE — o número que torna o item L decidível (2026-08-14, noite II)

O §1 mede **por par**; o professor decide **por fonte**. Re-medido com o piso de réplica
**da fonte** (a advertência do §6 implementada — ver a nota de erro abaixo):

| fonte | razão mediana | tripé | pares | leitura |
|---|---:|---:|---:|---|
| **`QIN_2024`** | **0,024** | **3/3** | 2 | ⚠️ **tripé cheio e cego** |
| **`LIU_2020_WEAR`** | **0,115** | **8/9** | 21 | ⚠️ **tripé cheio e cego** |
| `LI_2022_TRIBOINT` | 0,264 | 4/4 | 5 | fraco |
| `LI_2022_MARSTRUC` | 0,342 | 6/6 | 10 | fraco |
| `LIU_2025` | 0,378 | 3/7 | 3 | fraco |
| … | | | | |
| `LIU_2016` | 0,949 | 14/14 | 88 | |
| `JCSR_2023` | 0,987 | 4/5 | 6 | |
| `KARLSEN_2022` | 1,033 | 11/11 | 40 | |
| `CACCESE_2009` | 1,043 | 7/7 | 13 | |
| `YANG_2021` | 1,419 | 3/8 | 2 | |

**Mediana das medianas: 0,804** · 22 fontes julgáveis · 371 pares.

⇒ **cinco fontes têm razão < 0,40 e carregam 24 das 141 curvas do censo (17 %).** Duas
delas fecham (ou quase) o tripé com conteúdo preditivo **próximo de zero**.

### ⚠️ A advertência do §6 estava no documento e NÃO no script — e importava 30 %

A 1ª execução por fonte usava `pisos.get(src)`, mas `pisos_medidos` **não** devolve
`{fonte: valor}` — devolve `{'fam': …, 'med': …, 'por_fonte': {fonte: (mae, mx, sres)}}`.
Resultado: `None` em todas as fontes e piso global 0,005 em todo lugar. O sintoma foi a
coluna `piso` **constante**.

Com o piso certo: **532 → 371 pares** (161 caíam abaixo do scatter de réplica da própria
fonte, **30 %**) e a mediana das medianas sobe 0,755 → **0,804**. E — o que mais importa —
o **`BAUER_2024` SAI da lista**: ele era o 2º pior (0,026) com **um único** par, e esse par
está abaixo do próprio piso de réplica do BAUER (**0,0933**). **A correção removeu uma
acusação falsa.** Os dois casos graves sobrevivem inalterados.

### ⚠️ Errata do §2: contar pares cegos em VALOR ABSOLUTO inverte a ordenação

A tabela do §2 listava `LIU_2022_RETIGHT` com **17 pares cegos**, no topo — o que se lê
como "a pior fonte". Normalizado, ela é uma das **melhores**: mediana **0,847** sobre
**100** pares julgáveis. O número de pares cresce com n², então contagem absoluta pune
fonte grande e premia fonte pequena. **A estatística é a mediana por fonte, não a
contagem** — mesmo erro que o "44 % em 3 fontes" já cometeu nesta campanha.

## 6. Proposta (não executada — exige assinatura)

**Publicar a razão `d_mod/d_dado` ao lado do tripé**, por fonte, no report mestre. Não como
4ª perna (não é sobre erro, é sobre **conteúdo preditivo**) e sem mover o censo — como
**informacional**, no mesmo estatuto da deriva β. Uma fonte com mediana de razão ≈ 0 e tripé
cheio é exatamente o que hoje passa despercebido.

Duas advertências que a proposta tem de carregar:

1. **Descartar pares com `d_dado` abaixo do piso de réplica da fonte**, não do piso global —
   senão o §4 vira acusação falsa (o CACCESE seria "cego" quando o dado é que é ruidoso).
2. A razão **não é meta**: forçá-la a 1 seria pedir ao modelo que reproduzisse o scatter.

## Reprodutibilidade

`audit_cegueira.py` no scratchpad (532 pares, ~1 min, só-leitura). Os clusters de previsão
idêntica e as tabelas por curva foram medidos inline sobre o store.

## ⚠️ Nota de método: duas abordagens abandonadas antes desta

Esta sonda é a **terceira** tentativa da noite. As duas primeiras faziam **arqueologia
documental** — inferir *"alguém já conferiu esta fonte?"* de nomes de arquivo — e a
heurística errou em **três direções diferentes** em três revisões: permissiva (documento
guarda-chuva vira prova), colidente (`liu` casa **cinco** fontes distintas, e o script
"provou" o `LIU_2016` com um documento sobre o `LIU_2025`) e restritiva (o prefixo comum dos
`case_id` inclui a condição, e o `CHU_2026` apareceu como nunca conferido no mesmo dia em
que eu o conferi).

**Três correções seguidas de uma heurística não são refinamento — são o método avisando que
a pergunta está mal posta.** A pergunta certa não era *"quem conferiu?"* (inferência sobre
documentos) e sim *"está certo?"* (medição sobre o store).
