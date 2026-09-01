# D-Y ADOTADO — base da `run2p2` corrigida e o `k_ratchet` **converge** para o da `run7p1`

**2026-08-06 (noite)** · prereg `2026-08-06-karlsen-run2p2-base-prereg.md`
(gates escritos e commitados ANTES em `1a8660a`) · executor
`karlsen_run2p2_exec.py` · escrita `karlsen_run2p2_grava.py` ·
fingerprint **`5916d8be0510` → `1c118e405a42`**.

## O que era, e o que se testava

A CSV × 312 kN dava valores **redondos** — 300/250/200/150/90/38 — logo o
digitalizador leu **cruzamentos de linha de grade** e **ancorou o ciclo 1 no
F₀ nominal do registry** em vez de ler a figura. Duas extrações independentes
puseram o ciclo 1 em **332,0** (esta sessão) e **332,7 kN** (subagente D-X).

Mas a pergunta do passo **não era o dado** — era a **física**: a `run2p2`
carregava um `k_ratchet = 0,003` per-espécime, e a sonda de ontem
(`karlsen_run2p2_sonda_resultado.md`) registrou a predição de que, corrigida a
base, esse valor **subiria rumo aos 0,005 da `run7p1`**.

## Gates — 5/5

| gate | medido | veredicto |
|---|---|---|
| **G1** predição ±0,015 | **0,0315 / 0,0583 / 0,0364** contra **0,0319 / 0,0569 / 0,0364** previstos — desvio máx. **0,0014** | PASSA |
| **G2** parcimônia | passa o tripé com o `k_ratchet` **da `run7p1`** (0,005), sem valor próprio | PASSA |
| **G3** robustez de base | ótimo em 0,0045–0,0050 nas **quatro** bases 329,3–334,0 | PASSA |
| **G4** piso preservado | `limite_sres(KARLSEN)` **0,0845 → 0,0903** (107 %) e as 4 de risco seguem dentro | PASSA |
| **G5** isolamento | das **210** re-simuladas, mudou **uma**: a `run2p2` | PASSA |

Antes → depois na curva: **0,0488 / 0,0922 / 0,0548 → 0,0315 / 0,0583 / 0,0364**.
Ela passava a **0,98× no MAE**; agora passa a 0,63× · 0,58× · 0,40×.

## O ganho é PARCIMÔNIA, não censo — e isso se diz com número

**Censo permanece 139/205.** A `run2p2` já estava no tripé; o passo não
acrescenta curva. O que ele entrega:

1. **Um parâmetro a menos.** As duas entradas per-espécime do KARLSEN passam a
   carregar **o mesmo** valor (0,005): a exceção per-espécime vira exceção
   **de classe**. Adotou-se 0,005 e **não** o mínimo de MAE (0,0045) — a regra
   do D-I proíbe escolher pelo MAE; escolhe-se o que **compartilha**.
2. **Uma curva que passava pelo motivo errado passa pelo motivo certo.** O
   0,003 estava fitado contra dado com base 6,4 % deflacionada.
3. **Predição registrada antes e confirmada.** O ótimo migra de 0,003 (base
   errada, onde subir **piora monotonicamente**) para 0,0045–0,0050 em todas as
   bases corrigidas.

## O par que precisou ser declarado, e por quê

A `run2p2` era **metade do único par** que sustentava `limite_sres(KARLSEN)`:
a família `F = 124 800 N` (= 0,4 × 312 000) = `run2.2` ↔ `run7.1`, pareadas
pela chave mecânica **porque ambas carregavam o F₀ NOMINAL de 312 kN**.

Corrigida a base, o F_amp deixa de coincidir e a chave para de pareá-las. Sem
tratamento, o limite cairia a 0,025 e **quatro** curvas reprovariam por σ
(`run6p2` 0,0300 · `run7p1` 0,0504 · `M42_run21p0` 0,0337 · a própria
`run2p2`) — perda **causada pela correção**, não medida.

Tratamento: **PARES DECLARADOS** (classe de 2026-07-31, criada exatamente para
*"réplicas cujo F₀ ALCANÇADO difere e que a chave mecânica nunca casaria"*).
Isto é **mais honesto** que o estado anterior, onde o par era mantido por um F₀
nominal sabidamente errado numa das duas. Piso resultante: **0,0903**, 7 %
acima do anterior — o par verdadeiro é ligeiramente mais disperso, como se
espera de espécimes cujo aperto de fato diferiu.

## ⚠️ Erro de instrumento MEU, achado e corrigido no caminho

O executor imprimiu censo **142**. Rodando a mesma função sobre o store
**antigo** deu **142 também** ⇒ não era efeito do D-Y: eu havia reimplementado
o censo lendo `resid_std` **cru**, quando o report usa
**`rh.sres_para_censo`** — que aplica a regra `n<6` assinada em 2026-08-01
(σ com menos de 6 pontos é NÃO-JULGÁVEL). São exatamente 3 curvas
(`Yang2023 0,15/0,18 mm`, `zhang19_fig4`), e 139 + 3 = 142.

É a versão irmã da armadilha que o `CLAUDE.md` registra para `limite_sres`, um
nível adiante. **Regra que fica: o censo se pergunta ao helper, nunca se
reimplementa** — vale para `limite_sres` E para `sres_para_censo`. Corrigido no
executor, com a explicação preservada no código.

## ⚠️ Segunda lição de método, do mesmo passo

O executor foi rodado **em primeiro plano** e estourou o teto de 10 min a meio
da re-simulação. Não houve dano (nada gravado — conferido no `git status`), mas
a lição do D-Q ganha uma forma nova: **executor de adoção não vai em primeiro
plano**, porque um timeout no meio deixa o estado indeterminado. O
`karlsen_run2p2_grava.py` existe por causa disso — ele re-simula só as 11 do
KARLSEN e **re-carimba as 199** apoiado na prova do G5, em vez de repetir 50 min
de medição já feita.

## Limitação declarada da extração desta sessão

O traço da laranja é confiável **no ciclo 1** (coluna mais à esquerda, com dois
controles na mesma coluna: `run7.1` +0,4 %, `run6.2` −0,2 %; calibração y com
resíduo máx. 0,48 kN em 17 gridlines). **Não** é confiável no meio: pixels
amarelos anti-serrilhados (`run 6.2` misturado com branco) caem mais perto do
laranja que do amarelo puro e contaminam colunas inteiras (223 kN e 123 kN
juntos numa delas). Por isso a correção usa a **leitura-por-nível da CSV
original** — cujos ciclos de cruzamento não dependem do F₀ assumido —, e não
uma re-digitalização.

## O que este passo NÃO faz

Não toca `run6p2`/`run7p1`/`run14p2`: o D-X mediu as bases delas e as três estão
dentro de 1 %. **Não há dívida remanescente na Fig. 10.**
