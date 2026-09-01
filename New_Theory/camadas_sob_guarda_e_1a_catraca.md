# A linha das camadas envelheceu em **uma hora** — e a catraca disparou pela 1ª vez

**2026-08-15 (16:0x)** · store `20be19aabe11`, censo **143/205**, fora **62**, fila
form-limited **0** · **nada reclassificado, nada adotado** — só testes.

---

## 1. O que aconteceu, com relógio

| hora | evento |
|---|---|
| ~14:5x | corrijo à mão o cabeçalho da mesa: `"estatuto das 64 … classe-encerrada 8"` convivia com `"fora 62"` **no mesmo parágrafo**. Escrevo, no próprio texto, que a linha **não está sob guarda** |
| 15:09 | a sessão paralela assina a `yang2023 0,25mm` como classe **SUB-SLIP** (`9f660c5`) |
| 15:51 | re-meço: exceção **22 → 23**, indecidível **15 → 14**. **A linha que consertei há uma hora está errada de novo** |

⇒ **conserto manual de número publicado não segura por uma hora** numa campanha com duas
sessões. Isto não é argumento estético — é a medição do tempo de meia-vida da correção.

## 2. Conserto durável: as 5 camadas passaram a ser vigiadas

`tests/test_meta_numeros_nao_envelhecem.py` ganhou:

- **`_camadas()`** — chama o **classificador canônico** (`regra_de_parada_triagem.classificar`)
  por `importlib`, no idioma que o `_passivo_prov` já usava. **Não reimplementa** nada.
- **5 âncoras novas em `_VIVAS`**, uma por parcela: exceção · declarada · classe-encerrada ·
  indecidível-sem-piso · metric-limited. ⚠️ Uma por parcela **de propósito** — a lição do
  `"perna que MANDA"` (que publicava 3 números com 1 ancorado) vale aqui com 5.
- **`test_a_soma_das_camadas_e_o_fora`** — guarda estrutural: as 5 têm de **particionar** as
  `fora`. Pega camada nova que ninguém publicou e curva que deixou de ser classificada.

**Validação por perturbação: 5 de 5 âncoras são efetivas** (cada número alterado derruba a
guarda, nomeando o arquivo), arquivo restaurado **bit-a-bit** (`newline=''`, sem resíduo CRLF).

Guarda: 21 → **27** testes.

⚠️ **A `_camadas()` replica a SELEÇÃO das `fora` do canônico, e essa foi a parte perigosa** —
eu a errei **três vezes** hoje de manhã (classificando também as que passam o tripé; fundindo
`_EXCECOES` com `_DECLARADAS`; descartando `sd is None`). Os comentários no helper registram
as três, porque as três eram **invisíveis** na contagem de `classe_parada`.

## 3. ⚠️ A catraca de exceções disparou — e foi sobre assinatura de outra sessão

`test_excecao_catraca_auditavel` (escrito ontem) **falhou de verdade pela primeira vez**: a
exceção SUB-SLIP entrou **sem o trio conferível** `(perna, valor, piso)`.

**Li a prova gravada antes de escolher a saída**, como manda o protocolo:

> *"sub-slip (stick 100 % medido): dado colapsa sob stick e nenhuma alavanca alcança — `gth`
> (q = 3,8 do próprio paper) varrido 27 células, máx. −48 % sem fechar (0,086/0,296/0,113 na
> melhor)"*

É prova da classe **"nenhuma alavanca alcança"**, irmã das provas em nível de lei do CHU. Ela
**não** afirma *"o modelo é tão bom quanto a dispersão do dado"* (o que exigiria piso); afirma
*"o alcançável não contém o alvo"*. E os três números são as **três pernas da melhor célula**,
não um par valor/piso.

⇒ **saída 2** (a que o próprio teste documenta): entra no `_SEM_TRIO_BASELINE` **com comentário
dizendo por quê**. Baseline 20 → **21**.

## 4. ⚠️ A tensão que a 1ª ativação expôs — e o teste que a mede

A saída 2 faz o baseline **crescer**. Se **toda** exceção nova tomar a saída 2, a catraca deixa
de travar o problema e passa apenas a **documentar a deriva**. Melhor que o silêncio, mas não
é o objetivo.

Novo teste **`test_a_fracao_conferivel_nao_encolhe`**: o número de provas conferíveis não pode
cair abaixo do piso observado (**2**). Hoje: **2 de 23 = 8,7 %**.

⇒ se um dia esse teste falhar **junto** com a catraca, a leitura é única e clara: **as exceções
estão crescendo E ficando menos auditáveis ao mesmo tempo**.

**Piso em número absoluto, não em fração**, de propósito: com 2 conferíveis, uma barra
percentual oscilaria com o denominador e falharia por ruído a cada assinatura nova.

## 5. ⚠️ A suíte estava VERMELHA desde a D-AD — 2 testes, nenhum deles meu

Rodei a suíte completa antes de commitar (regra do charter) e vieram **2 falhas / 953 passam**.
Nenhuma vem das minhas edições; **as duas são dívida da adoção D-AD** (`42568f4`), que foi
commitada sem elas fechadas:

| teste | o que cobrava |
|---|---|
| `test_classe_parada_nao_cresce_calada` | a composição da classe encerrada mudou (2 curvas saíram) |
| `test_dof_reduction_software` | `s1_amp_gate_{dref,p}` deixaram de ser dormentes ⇒ *"atualize §4.42/MODEL_LEGITIMACY, ou reverta a adoção"* |

Fechei as duas, porque **suíte vermelha bloqueia toda adoção** (a regra exige suíte completa
antes de cada uma) e ambas são escrituração que a adoção devia.

**(a) Composição da classe.** As duas que saíram — `amp0p25` e `amp0p3` — **passam o tripé com
folga** hoje (0,72×/0,49×/0,53× e 0,72×/0,51×/0,73×). Saíram **por mérito**. Baseline
atualizado no idioma da entrada anterior (`chu test5`).

⚠️ **É a segunda vez que a mesma lição aparece, e agora pesa mais:** a `chu test5` saiu com
**2** constantes de assentamento; estas duas saíram com **UM** número. Somando, **três** curvas
de uma classe declarada **ENCERRADA** foram resolvidas — duas delas por uma forma que já
estava no engine, default-inerte. Isso é evidência direta a favor da proposta **N′**.

**(b) Contagem honesta de DOF.** Re-medida: **64 dos 115** campos tocados por alguma adoção,
**51 dormentes**. `s1_amp_gate_floor` **fica** nos dormentes (a adoção o deixou no default 0,0).

⚠️ **E aqui havia uma contradição aparente que precisava ficar escrita**, sob pena de o
próximo leitor concluir que o gate está morto. O comentário do próprio teste registra, de
2026-08-02: *"`s1_amp_gate` — falsificado **POR CONSTRUÇÃO**: contradomínio (0,1], só sabe
atrasar"*. E a D-AD o adotou.

Não é contradição — são **jobs opostos**:

| data | job pedido | contradomínio (0,1] serve? |
|---|---|---|
| 08-02 | **acelerar** a perda no fim (classe "aceleração tardia") | ⛔ não — falsificado por **álgebra**, sem medição |
| 08-15 | **reduzir** a perda em amplitude baixa (inclinação do `LIU_2025`) | ✅ é exatamente o que ele faz |

⇒ **falsificação por contradomínio vale contra o JOB, não contra o CAMPO.** Registrado no
próprio teste, ao lado da nota de 08-02.

## 6. O que NÃO mudou

Censo **143/205**, store `20be19aabe11`, fila form-limited **0**, `_EXCECOES`/`_DECLARADAS`
intactos, `regra_de_parada_triagem.py` e `report_html.py` **não tocados**, nenhuma config
alterada. Só `tests/` e o cabeçalho da mesa.

## Reprodutibilidade

`py -3.12 -m pytest tests/test_meta_numeros_nao_envelhecem.py tests/test_excecao_catraca_auditavel.py -q`
· perturbação inline no corpo do commit (5 casos, restauro verificado bit-a-bit).
