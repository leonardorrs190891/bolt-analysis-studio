# Prereg — `LIU_2020_WEAR`: canal de **flanco** ligado, o mecanismo que o artigo atribui

**2026-08-14 (noite VI)** · assinatura em bloco do professor (*"continue o loop, eu assino
tudo"*) · gates **IMUTÁVEIS** depois desta linha.

---

## ✅ ESTADO: **EXECUTADO em 2026-08-15 (madrugada) — gates 9/9**

A janela liberou (sessão B commitou o B/H-raiz em `42580a4`; `adopted_configs.json` e
`inputs.py` saíram do status; store escrito às 23:05 e quieto por 46 min).

⚠️ **A linha de base do prereg foi RE-VERIFICADA contra o store novo antes de executar** —
o re-stamp deles moveu o fingerprint `c37618c5cc96` → `c9f028b015c0`, e as **9 curvas do
`LIU_2020_WEAR` ficaram bit-idênticas** (0 de 9 mudaram), como o diff CHU-only previa. Os
gates congelados seguiam válidos.

| gate | resultado |
|---|---|
| **G1** DLC bit-idênticas | ✅ **Δ = 0,0e+00** nas 3 pernas, nas 2 curvas |
| **G2** zero saem | ✅ 8/9 → 8/9 |
| **G3** pior piora ≤ +0,010 | ✅ **+0,0096** (`fig9_AF0,2`) |
| **G4** censo não decresce | ✅ **141/205** inalterado |
| **G5** isolamento | ✅ **7 curvas mudaram, TODAS do `LIU_2020_WEAR`, zero fora** |
| **G6** conteúdo preditivo | ✅ espalhamento **0,0000 → 0,0777** (dado 0,1569) |
| **G7** guardas | ✅ |
| **G8** suíte completa | ✅ |
| **G9** docs vivos no mesmo commit | ✅ |

Fingerprint `c9f028b015c0` → **`85e8104420b0`**, uniforme nos 210 (o
`exemplo_m12_sintetico` fica fora do batch — re-simulado direto, gotcha conhecido).

**A `AF0,4mm` melhora forte sem entrar:** 0,0729/0,1339/0,0345 →
**0,0526/0,0766/0,0227** — `res.máx` e σ **passam**, só o MAE bloqueia, por **0,0026**.

⚠️ **Dois acidentes evitados por `assert`, ambos registrados:**

1. A âncora textual do `prov` (`'   "prov": {\n    "tr_loose_gain": "lido-do-dado…'`)
   aparece **3 vezes** — o mesmo texto é compartilhado por `LIU_2020_WEAR`, `ZHANG_2018` e
   uma terceira fonte. Sem o `assert count == 1`, o `replace` teria escrito a procedência do
   flanco nas **três**. Re-ancorado no bloco `dlc`, que só esta fonte tem.
2. Edição **textual cirúrgica** em vez de round-trip de JSON: **10 inserções / 4 deleções**,
   contra as 1838/1820 da tentativa abortada.

### (registro) ⛔ A 1ª tentativa: ABORTADA — sessão paralela escrevendo no mesmo arquivo

A adoção foi **escrita e revertida** sem chegar aos gates. Motivo: ao conferir o formato do
`adopted_configs.json` depois de gravar, o `git status` **completo** (sem filtro) revelou
que a sessão paralela estava ativa **naquele momento**:

* `New_Theory/adopted_configs.json` **M**, com uma fonte **`CHU_2026`** que existe só na
  cópia de trabalho (`per_case: {test9: {emb_um: 9.5}}`) — eles estão adotando no CHU;
* `src/bolt_analysis_studio/validation/inputs.py` **M** (mtime 22:37) — módulo que a minha
  própria sonda importou nesta sessão (`load_full_curve`);
* `run_app.py` **M**.

**Disciplina de escritor único ⇒ aborto.** Estado verificado após o restauro: a minha
edição de flanco **não está** no arquivo; o grupo `CHU_2026` deles está **intacto**; a
`CHU_2026_D1p0` de hoje está intacta. O backup `.bkp_flanco` foi **removido** (byte-idêntico
ao arquivo) para não sinalizar "execução a meio" ao próximo ciclo.

### ⚠️ Ressalva que não consigo eliminar

Entre o meu backup (**22:43**) e o meu restauro (**22:44:04**) há uma janela de ~90 s em que
uma escrita concorrente teria sido **sobrescrita**. Não posso verificar: o meu próprio
`touch` destruiu o `mtime` que serviria de evidência.

### O que falhou no meu método

1. **Verifiquei escritor único no INÍCIO do ciclo, não imediatamente antes de ESCREVER.**
   Às 21:14 o arquivo estava limpo; a atividade deles começou depois. A checagem tem de
   colar na escrita.
2. **O meu `git status` estava filtrado por diretórios e por `grep "^ ?M"`**, o que me deu
   sensação de cobertura total e escondeu `run_app.py` — e teria escondido qualquer coisa
   fora da lista. Para decidir escrita, o status vai **inteiro**.
3. **Gravei o JSON com um serializador diferente** (`indent=1`), reformatando o arquivo
   inteiro: **1838 inserções / 1820 deleções** para uma mudança de 3 campos. Mesmo sem a
   colisão, esse diff seria irrevisável. Reescrever config exige casar o formato original.

**A medição do §"Por que vale adotar" continua válida** — foi feita por override em
memória, sem tocar o arquivo. A adoção fica pronta para execução quando o arquivo estiver
livre.

---

## ⚠️ Isto NÃO é o item M como ele estava escrito — a prova gravada mudou a rota

O item **M** propunha religar **`k_wear_spec`** (desgaste no **bearing**): 7/7 na fonte,
+1 no censo, mas exigindo emenda de tolerância (+0,0125 numa curva).

**Ao ler o `prov` da config adotada, essa rota caiu:**

```
K_archard  : "paper-attribution (SEM/EDX: desgaste no FLANCO da rosca, não no
              bearing; liu2020: rollers isolam placa-placa) — wear transversal
              OFF por leitura"
k_wear_spec: "=0 pela MESMA leitura"
_forma     : "flank_wear_on/flank_transverse_on/k_wear_flank ficam default OFF
              (decisão do professor pendente, PARE F4 §6)"
```

⇒ os zeros **não são artefato de fit parcimonioso**; são **leitura do artigo**. Religar o
bearing contradiria a atribuição SEM/EDX. **O mecanismo do paper é o FLANCO**, o engine tem
esse canal, e ele estava desligado **aguardando exatamente a assinatura que agora existe**.

## O que se adota

No grupo **existente** `LIU_2020_WEAR`, dentro do `per_case` que já existe, na chave
**`zinc`** (que já carrega `mu`/`mu_thread`):

```
flank_wear_on       = 1.0
flank_transverse_on = 1.0
k_wear_flank        = 1.2e-15
```

⚠️ **`per_case`, NÃO grupo novo** — lição **D-AB**: *"grupo nasce mínimo"*. Um
`LIU_2020_WEAR_zinc` novo não herdaria `K_archard=0`, `C_creep=0`, `emb_um`, `N_emb` do
grupo base (o matcher escolhe **um** vencedor), e as 7 curvas de zinco perderiam tudo o
resto. `per_case` casa por **substring pura** e preserva o grupo.

⚠️ **As 2 curvas `fig15_DLC` NÃO são tocadas** — par tribológico distinto (revestimento
DLC × zinco eletrolítico). Constante tribológica é **por par** (§4.7).

## Regra de escolha da constante — declarada ANTES

**A maior dose cujo pior agravamento de MAE fique ≤ +0,010** (o gate padrão), porque o
objetivo é **conteúdo preditivo**, limitado pelo gate. Medido: 8e-16 → +0,0063;
**1,2e-15 → +0,0096**; 1,6e-15 → +0,0129 (reprova). ⇒ **1,2e-15**.

Não é escolha por MAE da curva-alvo (precedente **D-I**/**D-AA**: a regra vence a métrica).

## Por que vale adotar sem ganho de censo

O ganho é o que o item **L** mediu e nomeou: a fonte varre a amplitude transversal **4×**
(AF 0,1→0,4 mm, P₀ fixo) e o modelo devolve **0,9650 nas quatro** — cobertura **0 %**. Ela
está 8/9 no tripé com **4 predições distintas para 9 condições**.

| | hoje | com a adoção |
|---|---:|---:|
| espalhamento do MODELO na varredura | **0,0000** | **0,0777** |
| espalhamento do DADO | 0,1569 | 0,1569 |
| cobertura | **0 %** | **~50 %** |

E a `AF0,4mm` (hoje fora) passa a reprovar **só no MAE**, por 0,003:
0,0729/0,1339/0,0345 → **0,0526/0,0766/0,0227** — `res.máx` e σ **entram**.

Precedente de adoção sem ganho de censo: **D-P** (Φ medido no LI_2022, Δ = 0 nas 210,
adotada **por procedência**).

## Gates (congelados)

| # | gate | esperado |
|---|---|---|
| **G1** | as 2 `fig15_DLC` **bit-idênticas** | Δ = 0 exato nas 3 pernas |
| **G2** | **zero curvas saem** do tripé (fonte e global) | 0 |
| **G3** | nenhuma curva piora > **+0,010** de MAE | máx medido +0,0096 |
| **G4** | censo global **não decresce** | ≥ 141 |
| **G5** | isolamento: nenhuma curva fora do `LIU_2020_WEAR` muda | Δ = 0 |
| **G6** | conteúdo preditivo sobe | espalhamento do modelo > 0,05 (de 0,0000) |
| **G7** | guardas de censo/procedência/piso verdes | todas |
| **G8** | suíte completa verde | 941/1 ou mais |
| **G9** | docs vivos re-sincronizados no MESMO commit | mesa + fingerprint |

⚠️ **G1 e G3 matam a adoção se falharem.** Tocar o DLC seria aplicar constante tribológica
fora do par; estourar +0,010 seria a emenda que eu me recusei a auto-autorizar na rota do
bearing — e recusar lá e aceitar aqui seria incoerente.

## Procedência declarada

`k_wear_flank` = **`fitado-this-rig`, 1 número**. O que **tem** procedência de artigo é a
**escolha do canal** (SEM/EDX: flanco, não bearing) — a magnitude não tem âncora e isso vai
escrito no `prov`.

## Rollback

`.bkp_flanco` de `adopted_configs.json` e cópia do store. Qualquer gate divergente ⇒
restaura.
