# PREREG — a `prov` do `LIU_2025` diz que o wear está DESLIGADO, e ele carrega 0,286 da perda

## Estado

**PENDENTE — aguarda assinatura.** Nada executado. Medido em 2026-08-21 (01:5x) contra o
store **`89b1899f18c1`** (uniforme, 210 registros, zero divergentes), censo `_censo()`
tripé **166/205**.

---

## 1. A afirmação, verbatim

`New_Theory/adopted_configs.json`, `prov.k_wear_scale_tr`, **idêntica nos 3 grupos** do
`LIU_2025` (`LIU_2025`, `LIU_2025_amp0p4`, `LIU_2025_amp0p5`):

> *"**DESLIGA o canal de wear nesta fonte**: via tuner_shim o valor 0,0 leva
> `k_wear_spec` a 0 (medido na auditoria de 2026-08-12). Não é constante fitada — é a
> chave que zera o mecanismo, e **não consome DOF**."*

## 2. O que está certo nela, e o que é falso

✅ **Certo:** o shim faz o que ela descreve. Medido —
`translate_legacy_tuners({'k_wear_scale_tr': 0.0})` roteia para `k_wear_spec`, e no
material efetivo da `amp0p8` sai **`k_wear_spec = 0.0`**.

⛔ **Falso: `k_wear_spec = 0` NÃO zera o mecanismo.** É a armadilha que o `CLAUDE.md`
documenta em letra:

> *"Desligar wear transversal: `k_wear_spec=0` cai na via **LEGADA K/H** (NÃO 'sem
> wear'); precisa `k_wear_spec=0` **E** `K_archard=0`."*

No material efetivo, `K_archard` e `hardness` ficam nos **defaults** (1e-4 e 2e9)
⇒ K/H = **5e-14**, que é justamente o valor canônico. O canal roda em força plena.

**Medido na decomposição da `amp0p8`:** `wear = **0,28629**` (não zero), e **47 %** do
incremento tardio, com ABS tardio 0,217 de 0,466.

## 3. ⚠️ Não é só rótulo: o canal é LOAD-BEARING

Sonda de 2 pontos embrulhando `_effective_overrides` (só-leitura, nada escrito), pondo
`K_archard = 0` — o que "desligado" de fato exigiria:

| curva | nominal MAE/res.máx/σ | wear **realmente** off | `wear` na decomp. |
|---|---|---|---:|
| **`liu2025_M16_amp0p8`** | 0,0393 / 0,0863 / 0,0419 | **0,1496 / 0,4500 / 0,1986** | 0,286 → 0 |
| `liu2025_M16_fig2_single` | 0,0279 / 0,0579 / 0,0270 | 0,0307 / 0,0848 / 0,0311 | 0,063 → 0 |
| `liu2025_M16_amp0p6` | 0,0213 / 0,0697 / 0,0220 | **0,0153 / 0,0357 / 0,0188** *(melhora)* | 0,194 → 0 |
| `liu2025_M16_amp0p25` | 0,0359 / 0,0493 / 0,0132 | **bit-idêntico** | 0 → 0 |

⇒ remover o canal **destrói** a `amp0p8` (MAE **3,8×**, res.máx **5,2×**) ⇒ a segunda
metade da afirmação — *"não consome DOF"* — também é falsa: o canal carrega carga real.
(A `amp0p25` é bit-idêntica porque é **STICK**: lá o wear já era zero por falta de
driver, não por constante.)

⚠️ **Isto NÃO diz que o fit está errado.** K/H = 5e-14 é o valor canônico do bloco
`shared`, com procedência — não é constante solta. O que está errado é o **rótulo**, e
com ele a **contagem de DOF** que o material de artigo usa.

⚠️ **A auditoria citada (2026-08-12) está falsificada nesta parte.** Ela concluiu que o
canal estava desligado; a decomposição e a sonda dizem que não. Provavelmente ela
verificou o `k_wear_spec` e parou ali — que é exatamente a metade certa da história.

## 4. Duas rotas, e elas NÃO são equivalentes

| rota | o que faz | custo medido |
|---|---|---|
| **(A) corrigir o RÓTULO** | `prov` passa a dizer que `k_wear_spec=0` roteia para a via legada K/H = 5e-14 (canônico), que o canal está **ATIVO** e que **consome** 0 DOF novos mas carrega carga | **Δ = 0 em métrica** (metadado); fingerprint muda (o hash cobre `prov`) ⇒ re-carimbo dos 210 |
| **(B) desligar de fato** (`K_archard=0`) | cumpre o que o rótulo afirma | ⛔ **destrói a `amp0p8`** (3,8×/5,2×) e piora a `fig2_single`; melhora só a `amp0p6`. **Censo cairia.** |

**Recomendo (A).** A (B) seria fazer a física obedecer ao rótulo em vez de o rótulo
descrever a física — e o dado diz que a fonte **precisa** do canal.

## 5. Gates CONGELADOS (para a rota A)

| # | gate | critério |
|---|---|---|
| **G1** | métrica intocada | `Δ = 0,0000` nas **210** curvas — `prov` é metadado |
| **G2** | censo intacto | `_censo()` bit-idêntico: tripé **166** · resolvidos **188** · declarado_total **200** |
| **G3** | o rótulo não mente | o texto novo tem de dizer **as três** coisas medidas: rota legada K/H, valor 5e-14 canônico, canal **ativo** com 0,286 de carga na `amp0p8` |
| **G4** | escopo | só os **3** grupos do `LIU_2025` que usam o idioma (varredura do config: nenhuma outra fonte usa `k_wear_scale_tr=0.0`) |
| **G5** | fingerprint uniforme | 210/210 depois do re-carimbo, zero divergentes; `exemplo_m12_sintetico` por re-sim direta (fica fora do `parallel_batch`) |
| **G6** | formato | `git diff --numstat` do config coerente com "3 strings"; round-trip de formato conferido antes de escrever |
| **G7** | suíte | **idêntica ao baseline** (precedente R2: o gate é de não-regressão) |

**Ramos:** `EXECUTA (A)` · `EXECUTA (B)` (decisão do professor, com o custo de censo na
mesa) · `RECUSA` (o rótulo fica, com a ressalva registrada aqui) · `INCONCLUSIVO`.

## 5b. ⚠️ AMPLIAÇÃO (2026-08-21, 02:5x) — há um SEGUNDO rótulo falso, e o defeito é de INFERÊNCIA

Contei a população em vez de generalizar do caso vistoso. Varrendo **todo** o
`adopted_configs.json` por `prov` que afirma desligamento/inércia, o template
*"canal DESLIGADO nesta fonte (valor 0) … **zera o mecanismo**"* tem **5 instâncias**, e
elas **não** são todas iguais:

| grupo | campo | irmãos no `cfg` | veredito |
|---|---|---|---|
| `CHU_2026_test1` | `C_creep` | nenhum | ✅ claim **certa** |
| **`LU_2024`** | `emb_um` | **`emb_depth` = 8e-06** + `per_case.fig20_t16nm.emb_depth` = 4e-06 | ⛔ **FALSA** |
| `ANCORA_INTERNA` ×3 | `c_D` | `k_dmg_mu`=1 · `k_dmg_wear`=4 · `W_ref`=1e4 | ✅ claim **certa** |

**Por que as do `c_D` são certas apesar dos irmãos:** `c_D` é o **driver** do crescimento
de `D` (o dano só cresce da dissipação por slip via `c_D`); com `c_D = 0`, `D` fica em 0 e
os multiplicadores `k_dmg_*` multiplicam zero. ⇒ zerar o driver zera o canal. *(Raciocínio
do desenho do engine, **não** medido aqui — as 3 são `ANCORA_INTERNA`, fora do censo por decisão
do professor, sem páginas de report; não afetam número publicado.)*

**Por que a do `LU_2024` é falsa:** o campo `emb_um` é 0 — verdade —, mas o **irmão
`emb_depth` está setado no mesmo `cfg`** (8 µm, e 4 µm no `per_case` da T16 adotada em
2026-08-20). Medido no material efetivo da `lu2024_M8_fig20_T16Nm`:
`emb_depth = 4e-06` e o canal **`embedding` carrega 0,38084** — o maior valor de canal que
medi nesta varredura. A frase *"zera o mecanismo de ASSENTAMENTO (embedding)"* é falsa, e
o *"não consome DOF"* também: a T16 fechou **por causa** desse embedding ancorado.

### O defeito comum aos DOIS casos

| caso | por que o rótulo erra |
|---|---|
| `LIU_2025::k_wear_scale_tr` | o **roteamento**: `k_wear_spec=0` cai na via legada K/H, que roda nos defaults |
| `LU_2024::emb_um` | o **irmão**: `emb_depth` dirige o mesmo mecanismo, no mesmo `cfg` |

⇒ a causa é a mesma e é de **inferência**: o rótulo raciocina de *"este campo é 0"* para
*"o mecanismo está desligado"* **sem verificar o que mais dirige o mecanismo**. É a irmã
exata da regra que o `CLAUDE.md` já registra para leitura de decomposição — *"canal em
ZERO tem TRÊS causas: driver zerado, constante zerada, gate fechado"* — só que aplicada ao
lado da **escrita**: campo em zero tem várias leituras, e só uma delas é "mecanismo off".

**Escopo final da rota A:** 3 grupos do `LIU_2025` (`k_wear_scale_tr`) **+ 1** do
`LU_2024` (`emb_um`) = **4 strings**. As de `c_D` e `C_creep` ficam como estão.

⚠️ **Contagem honesta:** de 5 instâncias do template, **1** é falsa; somada à do shim, são
**2 rótulos falsos no config inteiro**. Não é epidemia — e dizer "2" em vez de "o template
é podre" é a diferença entre achado e alarme.

## 5c. ⚠️ CONFUNDIMENTO DECLARADO ANTES DO RESULTADO (execução, 2026-08-21 07:5x)

Rota **A ASSINADA** (*"assinado, execute os 4 rótulos"*) e em execução. Registro um
confundimento **antes** de ver o Δ, porque declarar depois não vale nada.

**Cronologia medida:**

| hora | evento |
|---|---|
| 07:41:40 | a sessão paralela modifica o **ENGINE** (`dynamic_stiffness_analyzer.py`, +30 linhas: `onset_burst_frac`/`onset_burst_rate`, o *burst de ruptura*) |
| ~07:45 | eu capturo o baseline **lendo o store** (210 tríades) — store carimbado com o engine **ANTIGO** |
| 07:50:47 | eu lanço o re-carimbo, que roda com o engine **NOVO** |

⇒ o **G1** (`Δ = 0 nas 210`) passa a medir **duas mudanças somadas**: os meus 4 rótulos de
`prov` (que não tocam física) **e** a capacidade nova do engine. O fingerprint **não cobre
o código** (`CLAUDE.md`: *"hasheia o bloco `shared` + configs adotadas, NÃO o código"*),
então nada denunciaria a mistura sozinho.

**Por que não parei o batch:** ele escreve o store **incrementalmente**. Abortar em 10/209
deixaria um **mosaico** de duas versões — pior que o confundimento, e sem o benefício de
ser detectável pelo hash.

**Leitura pré-registrada do resultado, nos dois ramos:**

* **Δ = 0 nas 210** ⇒ as duas mudanças são metric-neutras; o G1 fica satisfeito **com a
  ambiguidade declarada** (não posso creditar a neutralidade só à minha edição, e não
  preciso: o que o gate protege é que o store não mude de física).
* **Δ ≠ 0 em alguma** ⇒ **não commito**. Separo as causas antes, porque atribuir à minha
  edição de `prov` uma mudança vinda do engine seria exatamente o erro que este prereg
  documenta na §2 (raciocinar de um campo para um mecanismo sem verificar o que mais o
  dirige).

**O que sustenta a expectativa de Δ = 0 do lado deles:** o campo novo é
`onset_burst_frac: float = 0.0` com guarda `if (frac > 0.0 and rate > 0.0 …)` ⇒ o ramo
**não computa** no default, e há `tests/test_onset_burst.py` novo cobrindo. É o padrão
default-inerte da campanha — mas isso é **leitura do fonte**, não medição, e a medição é o
próprio G1.

⚠️ **Regra que este episódio paga:** *"1 escritor por recurso"* precisa incluir o **engine**
na lista de recursos de uma adoção de store, não só o config e o store. Um re-carimbo herda
o código vigente, e o hash não o vê.

## 5d. ⛔ DESFECHO (08:2x): o ramo `Δ ≠ 0` DISPAROU — colisão de escritores, nada commitado

O confundimento da §5c virou colisão. O re-carimbo terminou (exit 0, 2418 s, 209
resultados) e os gates deram:

| gate | resultado |
|---|---|
| **G3** o rótulo não mente | ✅ os 4 textos escritos e **relidos do disco** conferem |
| **G4** escopo | ✅ 4 campos, nenhuma outra fonte usa os idiomas |
| **G6** formato | ✅ 4 inserções / 4 deleções minhas, formato preservado |
| **G1** Δ = 0 nas 210 | ⛔ **1 curva com Δ = 0,5196** (`lu2024_M8_fig14_amp1p0_long`) |
| **G2** censo intacto | ⛔ `declarado_total` 200→199 · `fora_aberta` 5→6 · `fora_estatuto` 34→33 |
| **G5** fingerprint uniforme | ⛔ **mosaico de TRÊS**: `964964e28323` ×188 · `242b00777523` ×21 · `89b1899f18c1` ×1 |

**A causa está medida, e não é minha.** Durante os 40 min do re-carimbo a sessão paralela
**adotou o burst de ruptura**: o diff do config tem **21 linhas adicionadas, das quais só 4
são minhas** — as outras 17 são `onset_burst_frac: 0.62`, `onset_burst_rate`,
`k_loose_graded`, `loose_F_exp: 1.24`, `s_crit_loose`, `loose_rate_mode`,
`loose_arrest_floor`, `slip_onset_sharpness`. Isso explica **os três** gates: o Δ de 0,52 é
a `fig14_amp1p0_long` passando a modelar o burst, a mudança de censo é ela saindo das
declaradas, e o mosaico é o batch tendo carimbado 21 curvas com o meu fingerprint antes de
o config deles mudá-lo para `964964e28323`.

✅ **As minhas 4 strings SOBREVIVERAM** — verificadas uma a uma no disco depois da escrita
deles (a releitura que pegou a perda por chave duplicada em 08-15 foi o que deu essa
garantia aqui também).

### Por que NÃO commitei nem o config

`git commit -- New_Theory/adopted_configs.json` commita o **arquivo inteiro**, e ele agora
carrega **17 linhas deles**. Seria o hazard do `CLAUDE.md` invertido: em vez de as minhas
edições serem varridas para o commit alheio, o trabalho **em vôo** deles entraria no meu,
atribuído a mim e fora dos gates deles. ⇒ **nada compartilhado commitado**: config, store,
engine e `report_html.py` ficam como estão, para quem está adotando fechar com os próprios
gates. Este prereg é a única coisa que commito.

⚠️ **O erro é meu e tem nome exato.** Conferi o `git status` às 07:38 (limpo) e lancei o
re-carimbo às **07:50:47**; o engine deles mudou às **07:41:40** — dentro da janela de 9
minutos entre a minha checagem e o meu lançamento. **Eu documentei essa exata armadilha
ontem**, no desfecho do item W: *"a regra 1 do cron não me protegeu porque no meu git
status das 23:0x o config ainda estava limpo — a janela de risco abre DEPOIS da checagem"*.
Escrevi a lição e caí nela no dia seguinte, porque não re-conferi **imediatamente antes**
de um executor de 40 minutos.

**Regra que fica, agora operacional e não só descritiva:** antes de lançar executor longo
sobre recurso compartilhado, (a) re-conferir `git status` **na mesma chamada** que o
lançamento, e (b) preferir re-carimbo em **duas fases** — medir, e só então escrever —
porque um batch de 40 min é uma janela larga demais para uma checagem pontual.

**Estado para retomada:** os 4 rótulos estão **escritos e corretos no disco**; falta apenas
um re-carimbo limpo sob o config final (o deles + os meus 4), que pode sair de graça no
próximo `parallel_batch --store` de quem fechar a adoção do burst.

## 5e. ✅ ROTA A COMPLETA (10:1x) — os gates fecham, e a colisão se resolveu sozinha

A sessão paralela fechou as próprias adoções (`d0d09b4` burst + `57edf6f` `prov` do AME com
re-carimbo) e **carregou as minhas 4 strings junto** — verificado no `HEAD`, as quatro
presentes com o marcador `CORRIGIDO 2026-08-21`. Aconteceu exatamente o que o §5d previu:
*"falta um re-carimbo limpo sob o config final, que sai de graça no próximo
`parallel_batch --store` de quem fechar a adoção do burst"*.

⚠️ **E a separação que o §5d exigia ficou possível por construção**, porque o burst é
`per_case` e alcança **uma** curva:

| escopo | curvas | Δ contra o baseline |
|---|---:|---|
| `LIU_2025` *(3 grupos cujo `prov` eu editei; **sem** burst)* | 7 | **Δ = 0,0 EXATO em 7 de 7** |
| `LU_2024` *(grupo cujo `prov` eu editei)* | 13 | **Δ = 0,0 EXATO em 12 de 13** |
| a única que move | 1 | `fig14_amp1p0_long`, Δ = 0,767 — **a única com `onset_burst_frac > 0`** |

⇒ **G1 satisfeito com o confundimento separado por MEDIÇÃO, não por argumento**: 19 das 20
curvas dos grupos que editei estão bit-idênticas, e a exceção é nomeadamente a portadora da
constante deles. A `prov` é metadado e não é lida pelo engine — mas agora isso está
**medido**, não deduzido.

| gate | resultado final |
|---|---|
| **G1** métrica intocada | ✅ Δ = 0 exato em 19/20 das curvas dos grupos editados; a 20ª é a portadora do burst |
| **G2** censo intacto | ✅ tripé **167** (o +1 é da adoção deles) · `declarado_total` **200** |
| **G3** o rótulo não mente | ✅ os 4 textos no `HEAD`, com as três coisas medidas |
| **G4** escopo | ✅ 4 campos, nenhuma outra fonte usa os idiomas |
| **G5** fingerprint uniforme | ✅ **`2b862e94aaec` nos 210**, zero divergentes, config casa |
| **G6** formato | ✅ 4 inserções / 4 deleções, formato preservado |
| **G7** suíte | ⚠️ **1056 passed · 1 skipped · 2 failed** em 27m26 — as **duas** atribuídas por medição a trabalho em vôo deles (tabela abaixo). A catraca de procedência, que era **a** falha pendente, **fechou** (4 passed): a dívida do `YANG_2023_AME` que eu havia preregado foi paga por eles no idioma composto `emb_um/N_emb` |

**Detalhe do G7, com a atribuição medida:**

| falha | causa |
|---|---|
| `test_store_fingerprint_uniforme::test_store_reflete_a_config_vigente` | **eles** editaram o config *depois* do re-carimbo — o diff em vôo traz `slip_onset_W`, `c_D`, `k_dmg_all`, `W_ref`, `slip_onset_sharpness` (adoção nova de dano/incubação). Fingerprint fora de sincronia é o estado **esperado** no meio de uma adoção |
| `test_scatter3_panel::test_href_do_ponto_segue_a_convencao_de_quem_escreve` | `report_html.py` está `M` — edição deles no escritor de reports |

⇒ **nenhuma toca arquivo que esta execução editou**, e o diff do config em vôo tem **0**
linhas minhas (as 4 estão no `HEAD`, conferidas uma a uma). Os gates G1–G6 foram medidos
contra o estado **commitado e limpo** (`2b862e94aaec`, uniforme nos 210), que é o que a
rota A tinha de provar.

⚠️ **NÃO declaro o G7 "verde".** Pelo precedente R2 o gate é de **não-regressão contra o
baseline**, e o baseline de 10 h atrás tinha 1 falha (a dívida do AME, hoje paga) enquanto
agora há 2 de outra origem — **os dois lados se moveram**, então a comparação não é
maçã-com-maçã e chamar de verde seria conveniência. O que se afirma é o verificável: as
duas falhas são de trabalho alheio em vôo, sobre arquivos que esta execução não tocou.

⚠️ **O que fica de método, e é o oposto de auto-elogio:** o desfecho bom **não** valida a
minha execução. Eu lancei um executor de 40 min sobre recurso compartilhado sem re-conferir
o `git status` na mesma chamada, e o que salvou o resultado foi (a) a outra sessão ter
fechado a própria adoção com re-carimbo completo e (b) o burst ser `per_case`. Nenhuma das
duas era garantia minha. A regra do §5d — **re-conferir na mesma chamada; re-carimbo em duas
fases** — continua valendo com a mesma força.

## 6. O que este item NÃO afirma

- **Não** afirma que a `amp0p8` fecharia sem o canal — mede o contrário.
- **Não** propõe mexer em `cfg` na rota A: nenhuma curva se move.
- **Não** julga a auditoria de 08-12 como um todo — só a conclusão sobre este canal.

## Reprodutibilidade

```bash
PYTHONPATH=src py -3.12 New_Theory/ataque_curva.py liu2025_M16_amp0p8
```
mais sonda de 2 pontos embrulhando `rn._effective_overrides` com `{'K_archard': 0.0}`
(idioma de sonda da campanha; nada escrito no store nem no config).
