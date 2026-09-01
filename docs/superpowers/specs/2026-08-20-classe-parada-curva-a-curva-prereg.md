# ✅ EXECUTADO — a `classe_parada` escondia **1 falso positivo**, e ele é a fila form-limited inteira

## Estado

**EXECUTADO em 2026-08-20 (23:0x)** sob assinatura do professor (*"assinado, execute
o W"*). Ramo: **`EXECUTA`**. Gates **6/6**.

| gate | resultado |
|---|---|
| **G1** censo intacto | ✅ `_censo()` **bit-idêntico** por `diff` do JSON completo (20 chaves) |
| **G2** isolamento | ✅ exatamente 2 linhas mudam: `classe_parada` 5→**4**, `form_limited` 0→**1**; as outras 6 camadas idênticas |
| **G3** discriminante estável | ✅ saída de `classe_parada_discriminante.py` **bit-idêntica**; `amp0p8` segue `ESPELHADO` (−0,0192 / −0,0192), não `AMBIGUO` |
| **G4** guarda re-sincronizada | ✅ `test_classe_parada_nao_cresce_calada` atualizado no mesmo commit, e **validado por perturbação**: morde tanto entrada quanto saída |
| **G5** G5 do charter | ✅ o cabeçalho de estado do `DECISOES_PENDENTES` re-sincronizado; as **duas** claims guardadas (`camada_classe_parada`, `camada_form_limited`) verdes |
| **G6** suíte | ⚠️ **1052 passed · 1 skipped · 1 FAILED** em 17m32 — a falha **não é desta execução**, e a prova está abaixo |

⚠️ **O G1 cita "tripé 165 / resolvidos 187" porque foi escrito às 16:5x, quando o censo
era 165.** Às 23:0x é **166 / 188**, movido por `ba3d847` (adoção `yang2023ame` da sessão
paralela) e **não** por esta execução. Gate é imutável: **não** reescrevi o G1 — verifiquei
o **invariante que ele testa** (censo idêntico antes e depois) contra o baseline capturado
imediatamente antes da mudança, e declaro as duas leituras aqui. Substituir 165 por 166 em
silêncio seria mover a trave; declarar não é.

⚠️ **Correção registrada:** este prereg nasceu dizendo *"bloqueado pelo item U (critério
(c))"*. **Falso** — o (c) foi FECHADO em 2026-08-14 (`regra_de_parada_proposta.md`
§FECHO). Eu havia lido um **comentário de código** em vez de conferir se o motivo estava
vivo; o comentário foi corrigido em `a39d47f` e o item ficou decidível.

### ✅ RE-VERIFICADO em 2026-08-20 (23:5x) sob fingerprint NOVO — o risco era real e não se materializou

Os gates foram medidos contra o store **`245dc93087d1`**. A linha do tempo mostra que a
sessão paralela commitou **`ae4b5aa` às 23:32** — *correção de input no BAUER fig8
(155 → 150 µm) com `per_case` re-lidos* —, que **move o fingerprint**, e o meu baseline
foi capturado às ~23:0x. ⇒ **não posso afirmar por timestamp que a config ficou parada
entre o baseline e a medição pós-mudança.**

Em vez de assumir, re-medi. Sob **`89b1899f18c1`** (uniforme, 210 registros, zero
divergentes):

| | baseline (`245dc…`) | agora (`89b18…`) |
|---|---:|---:|
| tripé · fora | 166 · 39 | **166 · 39** |
| `classe_parada` | 4 *(pós-W)* | **4** |
| `form_limited` | 1 *(pós-W)* | **1** |
| demais 6 camadas | 0 | **0** |
| fila: `amp0p8` MAE/mx/σ | 0,0393 / 0,0863 / 0,0419 | **idênticos** |

⇒ **o efeito do W reproduz exatamente** num store que já inclui a correção de input
deles, o que torna a verificação **mais forte** que a original, não mais fraca. E a
correção deles também foi **censo-neutra**.

⚠️ **Lição que fica:** gate medido enquanto outra sessão está no meio de uma adoção
precisa de **re-verificação**, não de confiança no relógio. A regra 1 do cron (*não meça
sob `M`*) existe para isto, e ela não me protegeu porque no meu `git status` das 23:0x o
`adopted_configs.json` ainda estava limpo — a janela de risco abre **depois** da
checagem, não antes. O que fecha a janela é medir de novo no fim.

### ⚠️ O G6 fechou VERMELHO, e a falha é DÍVIDA ALHEIA — atribuída por medição

```
tests/test_procedencia_catraca.py::test_passivo_de_procedencia_nao_cresce
   2 constante(s) NOVA(s) adotada(s) sem entrada em prov:
       YANG_2023_AME::N_emb
       YANG_2023_AME::emb_um
```

**Não é desta execução, e a atribuição é medida, não presumida:**

1. `git log -S "YANG_2023_AME" -- New_Theory/adopted_configs.json` aponta **`ba3d847`**
   (adoção `yang2023ame_axial` da sessão paralela, 22:0x).
2. Lendo o arquivo **direto do HEAD** (`git show HEAD:…`, portanto **sem nenhuma edição
   minha na árvore**), os dois campos estão em `cfg` e **ausentes de `prov`** ⇒ a falha
   **pré-existe** a esta execução.
3. Esta execução tocou **4 arquivos** e **nenhum é config**: o script de triagem, o teste
   de composição e dois documentos. Nenhuma constante foi adotada.

⛔ **Não escrevi a `prov` faltante.** Seria redigir procedência de constante que **eu não
medi** — exatamente o que este teste existe para impedir (*"escreva de onde veio o
número: paper, tabela, âncora, ou 'fitado-this-rig' com o gate que a justificou"*). A
dívida é de quem adotou, e o próprio teste oferece a saída honesta (`_SEM_PROV_BASELINE`
com o motivo) se a ausência for deliberada.

**Leitura do gate:** o G6 pede *"suíte completa antes do commit"*, e o que ele protege é
*"a minha mudança não quebra a suíte"*. Isso está **verificado** — a única falha é
anterior e ortogonal. Registro o vermelho em vez de anunciar 6/6, porque suíte vermelha
declarada é informação e suíte vermelha silenciada é o começo de um passivo.

---

## (registro) A proposta, como submetida

**2026-08-20 (16:5x)** · só-leitura · **nada executado** · store `4d1211958122`
(**uniforme, 210 registros, zero divergentes**) · censo canônico `_censo()`:
tripé **165/205**, fora **40** = 22 exceção + 13 declarada + **5 abertas**.

---

## 1. O achado, em uma linha

A camada `classe_parada(aceleracao tardia)` é atribuída **por FONTE**
(`_FONTES_CLASSE_PARADA = {CHU_2026, LIU_2025, JCSR_2023, YANG_2021}`). Rodando o
discriminante **já assinado** (`classe_parada_discriminante.py`, o instrumento da
P-7) contra o store de hoje:

| fonte | curva | viés 1/3 | viés 1/4 | veredicto |
|---|---|---:|---:|---|
| LIU_2025 | `liu2025_M16_amp0p8` | **−0,0192** | **−0,0192** | ⛔ **ESPELHADO (desabou cedo)** |
| LIU_2025 | `liu2025_M16_fig2_single` | +0,0542 | +0,0562 | classe (retém demais) |
| YANG_2021 | `yang2021_amp0p5mm_ax8kN` | +0,0703 | +0,0703 | classe |
| YANG_2021 | `yang2021_amp0p6mm_ax8kN_r1` | +0,0347 | +0,0347 | classe |
| YANG_2021 | `yang2021_amp1p0mm_ax2kN` | +0,0632 | +0,0632 | classe |

⇒ `LIU_2025` **MISTA** (1 classe + 1 espelhado) · `YANG_2021` **COERENTE** (3/3).
Sinal **estável nas duas janelas** ⇒ nenhuma curva é `AMBIGUO`.

**A `amp0p8` carrega o defeito ESPELHADO**: o modelo está **abaixo** do dado no
fim, então o remédio da classe — *acelerar mais* — a **piora**. É exatamente a
assinatura que tirou `LU_2024` e `SUN_2025_CRIMP` (P-7, 2026-08-08) e `YANG_2019`
(N-linha, 2026-08-15) da classe.

## 2. Por que o precedente **não** resolve sozinho

Aquelas três saíram como **falsos positivos PUROS** — fonte inteira sem nenhum
membro genuíno —, e a *opção mínima* da P-7 remove a **fonte**. Aqui a fonte é
**MISTA**: remover `LIU_2025` levaria embora a `fig2_single`, que é membro
**genuíno** (+0,0542).

O que o caso pede é a **opção 2 da P-7 — decidir curva a curva**, e o próprio
comentário do classificador registra por que ela **não foi executada**:

> *"Decidir curva a curva era a opção 2 da P-7, **não executada** porque obriga a
> re-derivar o critério (c) da regra de parada — decisão nova."*

⇒ **Este item está bloqueado pelo item U da mesa** (o critério (c) não distingue
`INCONCLUSIVO`). Não é bloqueio de medição: é a mesma decisão, chegando por outro
caminho.

## 3. O que muda — e o que **não** muda

Medido rodando a triagem com a curva fora da classe (monkeypatch em subprocesso;
**o arquivo não foi escrito**):

| | hoje | com a `amp0p8` fora da classe |
|---|---:|---:|
| tripé (leitura estrita) | **165** | **165** — *inalterado* |
| resolvidos | 187 | 187 — *inalterado* |
| declarado_total | 200 | 200 — *inalterado* |
| `classe_parada` | 5 | 4 |
| **fila form-limited** | **0** | **1** |

**Nada de censo se move.** O marcador vive só na triagem — o próprio código diz
*"não toca `limite_sres` nem o tripé; muda o que a fila **publica**, não o que o
modelo acerta."*

**O perfil da curva na fila:**

| perna | valor | ×limite | veredito |
|---|---:|---:|---|
| MAE | 0,0393 | **0,79×** | dentro |
| res.máx | 0,0863 | **0,86×** | dentro |
| **σ_res** | **0,0419** | **1,68×** | **única violada** |

Redução necessária: **40 %** em σ_res. Piso da fonte = **0,0250** = o global ⇒
`LIU_2025` **não tem piso medido acima do global**, logo **não há rota F7 por
piso**.

## 4. ⚠️ Por que isto importa para a REGRA DE PARADA

Publicar `form_limited = 0` lê-se como *"não sobrou trabalho legítimo"*. A medição
diz que sobrou **1**, e que a etiqueta que o esconde está **errada pelo próprio
discriminante da campanha**. Ou seja: a condição de parada do projeto está sendo
lida como atendida **em parte por atribuição indevida** — 1 de 5 membros da classe
que a sustenta.

Isto **não** é acusação de que o modelo acerta menos: os números do modelo não
mudam. É que a **fila publicada** deixa de ser honesta.

⚠️ **Contra-argumento que fica registrado:** o doc da curva
(`liu2025_par_de_taxas_opostas.md`) mede *"8 alavancas varridas, **nenhuma
fecha**"*. Alguém pode dizer que ela está fechada de todo modo. A diferença é de
**estatuto**: *"encerrada por uma classe cujo remédio a piora"* ≠ *"problema de
forma aberto, com 8 alavancas falsificadas"*. A segunda é a frase verdadeira, e é
para ela que existe a máquina de declaração.

## 5. Gates CONGELADOS (se assinado)

| # | gate | critério |
|---|---|---|
| **G1** | censo intacto | `_censo()`: tripé **165**, resolvidos **187**, declarado_total **200** — os três **bit-idênticos** |
| **G2** | isolamento | `classe_parada` 5→4 e `form_limited` 0→1; **nenhuma outra camada muda** |
| **G3** | discriminante estável | re-rodar `classe_parada_discriminante.py`: a `amp0p8` segue `ESPELHADO` nas **duas** janelas (não `AMBIGUO`) |
| **G4** | guarda re-sincronizada | `test_classe_parada_nao_cresce_calada` fixa a **composição** — tem de ser atualizado **no mesmo commit**, e falhar se a composição mudar de novo |
| **G5** | G5 do charter | todo documento vivo que publica `form_limited = 0` re-sincronizado no **mesmo commit** (`CLAUDE.md`, `DECISOES_PENDENTES.md`, `regra_de_parada_proposta.md`) |
| **G6** | suíte | completa, antes do commit |

**Ramos admitidos:** `EXECUTA` · `RECUSA` (o professor decide manter a atribuição
por fonte) · **`INCONCLUSIVO`** (o critério (c) não se re-deriva sem o item U ⇒ o
item volta para a mesa junto com ele).

## 6. O que **não** proponho

- **Não** proponho remover `LIU_2025` da classe (levaria a `fig2_single`, genuína).
- **Não** proponho declarar a `amp0p8` — ela **não** tem rota F7 (piso = global) e
  declarar sem procedência infla o resolvido com fracasso, contra o charter.
- **Não** proponho forma nova de engine. A curva precisa de **40 % de σ_res** e as
  8 alavancas conhecidas já foram varridas; forma nova é outra assinatura.

## Reprodutibilidade

```bash
PYTHONPATH=src py -3.12 New_Theory/classe_parada_discriminante.py
PYTHONPATH=src py -3.12 New_Theory/regra_de_parada_triagem.py
PYTHONPATH=src py -3.12 -c "import sys;sys.path.insert(0,'tests');\
import test_meta_numeros_nao_envelhecem as T;print(T._censo())"
```

⚠️ O efeito da §3 foi medido por **monkeypatch de `classificar` em subprocesso**;
`regra_de_parada_triagem.py` **não foi escrito**.
