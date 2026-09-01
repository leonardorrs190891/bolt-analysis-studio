# A **cobertura** do sistema de guardas, medida pela 1ª vez — 9 de 14 chaves; agora 14 de 14

**2026-08-15 (madrugada)** · store `85e8104420b0`, censo **141/205** · guarda ampliada e
validada por perturbação.

---

## 1. A premissa que nunca tinha sido testada

A campanha construiu o `test_meta_numeros_nao_envelhecem` para impedir que número publicado
envelheça (§4.43). **As falhas dele foram observadas várias vezes; a sua COBERTURA nunca foi
medida.**

Esta madrugada produziu duas falhas da mesma premissa, em poucas horas:

* a tabela do relatório executivo tinha **4 células vencidas** e o `_VIVAS` ancorava **uma**
  — as outras derivaram por várias adoções;
* as **células de custo** da mesa não têm guarda nenhuma, e uma delas media um
  contrafactual que ninguém executaria (o "item B custa −2 curvas").

Nos dois casos eu **observei** a falha depois de tropeçar nela. A pergunta certa é anterior:
**quantos dos números que o censo produz estão protegidos?**

## 2. Medido: 9 de 14

`_censo()` devolve **14 chaves**. O `_VIVAS` tinha **14 âncoras**, mas concentradas: **9
chaves** cobertas, **5** descobertas (`fontes`, `fora`, `manda_mae`, `manda_mx`, `n`).

Das cinco, **duas eram publicadas em contexto de afirmação** nos próprios documentos que o
`_VIVAS` já vigia:

| chave | valor | onde, sem guarda |
|---|---:|---|
| `fora` | **64** | o **cabeçalho** de `DECISOES_PENDENTES.md` — a linha que o cron manda toda sessão ler |
| `manda_mx` | **10** | a linha "perna que MANDA" do relatório executivo |

## 3. ⚠️ O modo de falha é o MESMO nos dois casos da noite: **ancoragem parcial de afirmação composta**

A linha "perna que MANDA" publica **três** números — `σ_res 47 · MAE 7 · res.máx 10` — e só
o primeiro estava ancorado. A tabela de oito linhas tinha **uma** ancorada. Em ambos, a
parcela protegida dá ao conjunto **aparência** de cobertura, e as demais envelhecem juntas.

⇒ **regra que isto gera:** afirmação composta precisa de âncora **por parcela**. Proteger o
primeiro número não protege os outros — protege *a impressão* de que estão protegidos.

## 4. O que foi feito

Três âncoras novas, todas **validadas por perturbação** (perturba → o teste falha nomeando
o arquivo → restaura, e o `git status` confirma restauração byte-a-byte):

| âncora | chave | perturbação |
|---|---|---|
| `perna que MANDA … MAE (\d+)` | `manda_mae` | 7 → 99 ⇒ **pegou** |
| `perna que MANDA … res\.máx (\d+)` | `manda_mx` | 10 → 88 ⇒ **pegou** |
| `censo \*\*\d+/205\*\* · fora \*\*(\d+)\*\*` | `fora` | 64 → 77 ⇒ **pegou** |

## 5. Cobertura final: **14 de 14**, sendo 12 direta e 2 por construção

As duas restantes — `n` = 205 e `fontes` = 27 — **não precisam de âncora própria**: elas são
**literais dentro das regex de outras âncoras** (5 e 1 respectivamente, ex.
`Na régua nova: \*\*(\d+)/205\*\*`). Se mudarem, essas regex deixam de casar e o teste falha
no modo **"âncora perdida"** — que é o segundo modo ruidoso previsto no desenho do teste.

⚠️ Isso é proteção **real mas de segunda ordem**: ela avisa que algo mudou, não *qual*
número. Registrado como característica, não como equivalente.

## 6. O que segue SEM guarda, e por quê

As **células de custo** da mesa (`DECISOES_PENDENTES.md`). Elas não são recomputáveis do
store: cada uma é uma **contrafactual** — *"quanto custaria fazer X"* — e só existe no
registro de quem a mediu. Ancorá-las exigiria declarar o contrafactual de cada uma numa
forma executável, o que é **decisão de política**, não de sessão.

A assimetria já estava registrada em 2026-08-14 (*"censo errado é constrangedor; custo
errado faz escolher a opção errada"*); o que esta noite acrescentou foi um **caso concreto**:
a célula do item B media uma variante que sobrepunha os grupos pinados, e a variante que a
sessão B de fato executou custou **zero**.

## Reprodutibilidade

`audit_guardas.py` no scratchpad (~1 s, só-leitura). ⚠️ **Nota:** a 1ª passada da sonda
usou uma regex frouxa para `manda_mx` (`res\.máx (\d+)`), que casou decimais e texto
histórico e inflou os "achados" de 2 para 6. Filtrando para afirmação vigente sobram os
dois do §2 — o achado sobrevive, a contagem inicial não.
