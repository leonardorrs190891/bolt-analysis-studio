# Prereg — a cadeia de reapertos do fig8: degradação ENTRE estágios

**2026-08-04** · decisão D-E (por delegação, mandato 2026-07-30) · gates
escritos **antes** de qualquer medição de MAE. Fingerprint de partida:
`63722b266dc0`.

## O alvo, e por que ele é o último alvo tratável

A triagem sob o fingerprint atual dá **fila form-limited = 7 curvas**. Três
delas são do `LIU_2022_RETIGHT` e — achado estrutural — **as três são da mesma
família `fig8_multi`**, que tem **grupo de config próprio**
(`LIU_2022_RETIGHT_fig8`). As outras 17 curvas da fonte resolvem para
`LIU_2022_RET` / `LIU_2022_RETIGHT_dry` e ficam fora do alcance de qualquer
mudança aqui. Alvo cirúrgico, não fonte inteira.

Estado das 5 curvas da cadeia (t0 = virgem, t1..t4 = reapertos sucessivos):

| estágio | MAE | res.máx | σ_res | viés | tripé |
|---|---:|---:|---:|---:|:--:|
| t0 | 0,0155 | 0,0380 | 0,0137 | −0,0147 | ✅ |
| t1 | 0,0533 | 0,0874 | 0,0269 | −0,0533 | ❌ (σ 1,07× · MAE 1,07×) |
| t2 | 0,0582 | 0,0720 | 0,0193 | −0,0582 | ❌ (MAE 1,16×) |
| t3 | 0,0404 | 0,0497 | 0,0135 | −0,0404 | ✅ (folga de MAE **0,0096**) |
| t4 | 0,0371 | 0,0850 | 0,0270 | +0,0371 | ❌ (σ 1,08×) |

## O defeito MEDIDO — e ele não é de nível nem de taxa

Retenção final **por estágio**:

| | t0 | t1 | t2 | t3 | t4 | vão |
|---|---:|---:|---:|---:|---:|---:|
| **dado** | 0,889 | **0,978** | 0,960 | 0,921 | **0,845** | **0,133** |
| **modelo** | 0,851 | 0,890 | 0,888 | 0,890 | **0,930** | 0,042 |

O dado cai **monotonicamente** a cada reaperto. O modelo é praticamente
**plano** em t1–t3 (0,890/0,888/0,890) e no último estágio **melhora**
(0,930) — anda para o lado errado.

Leitura física: o modelo trata cada reaperto como quase-recomeço
(`k_emb_renew=1,0`, renovação total do embedding), então cada estágio repete
o mesmo assentamento. A junta real **degrada entre estágios**: cada reaperto
assenta menos e escorrega mais, porque as superfícies já foram danificadas.

**Isto é forma faltante ENTRE estágios**, não erro dentro de uma corrida. É
por isso que os remédios locais não alcançam: em t1/t2/t3 o modelo perde
DEMAIS (viés negativo) e em t4 perde de MENOS (viés positivo) — uma
constante uniforme move os quatro para o mesmo lado e não pode fechar os
dois grupos. E σ_res é **invariante por translação**, então mesmo em t1,
onde o viés é 80 % do RMSE², deslocar o nível não fecha a perna que manda.

## Hipótese registrada

A **composição** da perda por reaperto está errada: sobra "assentamento
fresco" (que se repete igual a cada estágio, e por isso não cria tendência)
e falta "dano acumulado" (que cresce com o número de reapertos, e por isso
cria a tendência). O ajuste correto **troca um pelo outro**, não escala os
dois.

Alavancas candidatas, **no máximo 2 números**, todas já presentes no cfg do
grupo (nada de campo novo):

1. **baixar a perda de linha de base** — `k_wear_scale_tr` (0,06) ou
   `emb_depth` (4e-6) ou `k_emb_renew` (1,0). Efeito esperado: alivia
   t0–t3 (que perdem demais) e **piora t4**.
2. **subir a perda que ACUMULA** — `c_D` (0,5) ou `k_dmg_wear` (1,0). O
   dano é estado herdado pela cadeia, logo o efeito **cresce com o
   estágio**: pouco em t1, muito em t4. É essa dependência de estágio que
   pode fechar os dois grupos ao mesmo tempo.

`k_gall` (3,0) fica **congelado**: é a constante que o `verdict` do grupo
declara como a origem da recuperação dry 1,00→0,90 e mexer nela reescreveria
uma procedência existente sem dado novo.

## Gates (IMUTÁVEIS a partir daqui)

- **G0 (instrumento, antes de qualquer bisseção):** sonda de **2 pontos**
  por candidato, para fixar o SINAL da resposta. Δ = 0,0000 exato **não**
  autoriza "alavanca morta": conferir primeiro os companheiros do canal e
  se a chave é campo do engine ou de cfg (3 ocorrências de leitura errada
  em 2026-08-01/02; `tests/test_chaves_de_cfg_nao_sao_campos.py`).
- **G1 (PREDIÇÃO DE FORMA — o gate que decide):** a retenção final do
  modelo em t1→t4 tem de virar **estritamente decrescente**, com vão
  ≥ **0,08** (o dado tem 0,133; o modelo hoje tem 0,042 e crescente).
  Este gate é sobre **mecanismo**, não sobre erro.
- **G2 (nenhum caso pior):** nenhuma das 5 piora > **+0,01** em qualquer
  perna; **t0 e t3 têm de PERMANECER no tripé**. Declarado: a folga de MAE
  do t3 é só **0,0096** — é ele que aperta, não o t0.
- **G3 (isolamento):** as outras **17** curvas do `LIU_2022_*` ficam
  **bit-idênticas**. Se mudarem, o override vazou de grupo.
- **G4 (ganho):** ≥ **2** das 3 fora entram no tripé. Exatamente 1 ⇒
  adoção **parcial declarada**, não silenciosa. Zero ⇒ não adota.
- **G5 (procedência):** cada número adotado declarado por origem. Se for
  fit livre, dizer "fit livre" no `prov` — o gate falhado fica escrito no
  cfg, não em nota de rodapé (forma das adoções de 2026-08-01/02).
- **G6 (sincronia):** adoção ⇒ fingerprint muda ⇒ re-stamp uniforme dos
  210 + censo/docs/páginas/testes no MESMO commit.

### Ramos possíveis do veredicto

- **ADOTA** — G1 ∧ G2 ∧ G3 ∧ G4.
- **NÃO ADOTA (ajuste sem mecanismo)** — G1 **falha** e o MAE melhora.
  Este ramo é explícito porque é a armadilha do dia: melhorar o erro sem
  reproduzir a tendência é sobreajuste com aparência de progresso.
- **FALSIFICADO** — nenhuma parametrização das candidatas produz a
  tendência ⇒ a forma faltante não está nesta família de constantes;
  registrar e a classe entra na regra de parada.
- **INCONCLUSIVO** — o teste não testou (candidato inerte por companheiro
  desligado, gate nunca chamado, teto de simulação cortando a cauda).
  Ramo obrigatório desde 2026-07-30: sem ele o script é forçado a escolher
  entre PASSA e FALSIFICADO e escreve veredicto sobre teste vazio.

## Previsão registrada (para poder errar por escrito)

Espero que **`c_D` para cima** produza a tendência (o dano é o único estado
que a cadeia herda e que cresce com o número de reapertos) e que a
compensação venha de **`k_wear_scale_tr` para baixo**. **Não sei o sinal
da resposta do `k_emb_renew`** — a intuição diz que menos renovação alivia
os estágios tardios, mas a renovação também governa quanto assentamento
resta, e já errei o sinal duas vezes nesta campanha. Por isso o G0.
