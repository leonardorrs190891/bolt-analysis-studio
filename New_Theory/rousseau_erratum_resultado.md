# ERRATUM ROUSSEAU_2025 — drive do aço 10× errado + piso da fonte inválido

**2026-08-01** · achado ao VETAR O PDF OFICIAL (baixado na Rodada 6 — a
"caça de substituição" reencontrou a própria fonte e o PDF, que a nota de
aparato marcava como confirmação pendente da Tabela 2). Mesma classe
dupla do LU (fig20-drive + piso-T22), pega pelo mesmo método: ler o paper.

## Defeito 1 — input: o aço rodava a 10× o drive real

Tabela 2 do PDF: aço **10 kN, 0,05/0,05/0,04 mm**; o registry rodava os 3
a **0,5 mm**. (HDPE estava CERTO — 0,5/0,49/0,38 via
`ROUSSEAU_HDPE.delta_amp_mm`, procedência antiga da Tabela 2.) Prosa
adicional agora documentada: Fig. 6 compara HDPE×aço a **0,2 mm**;
Fig. 10 varre 0,03/0,05/0,10 no aço (não digitizada).

Impacto MEDIDO antes de aplicar (disciplina YANG_2023/fig20):

| caso | antes (drive errado) | depois (drive real) |
|---|---|---|
| steel_t10 | 0,087 / 0,188 / 0,098 | **0,304 / 0,738 / 0,259** |
| steel_t12 | 0,046 / 0,074 / 0,031 | **0,078 / 0,267 / 0,092** (sai do tripé) |
| steel_t14 | 0,020 / 0,034 / 0,013 | **bit-idêntico** (stick nos 2 drives) |

O fit adotado (`ROUSSEAU_2025`: c_bend=0,3, emb 1,0 µm, kj pedersen)
absorvia o drive errado — **procedência contaminada para o aço**;
recuperação (re-fit sob o drive real) na fila, com as âncoras novas do
PDF (Fig. 10 = varredura de amplitude no aço).

## Defeito 2 — o piso da fonte era um PAR FALSO

A única "família" da fonte era **aço-t10 ↔ aço-t12** — espessuras
DIFERENTES (a variável varrida do paper!) pareadas como réplicas porque a
chave mecânica `(fonte, δ, F_amp, modo)` é **cega à geometria per-case**.
O "piso" resultante (MAE 0,206 · mx 0,546 · σ 0,186) era scatter
ENTRE-condições — mesma classe do piso inválido do LU (retratado 31/07).

- **3 exceções F7-FORTE RETRATADAS** (steel_t10, hdpe_t10, hdpe_t12 —
  provas preservadas em `_EXCECOES_RETRATADAS_ROUSSEAU_PISO_INVALIDO`);
  re-assinatura exige piso VÁLIDO, que a fonte NÃO tem (nenhuma condição
  repetida publicada).
- **Bloqueio permanente** `_SEM_FAMILIA_MECANICA` (aço t10/t12): curvas
  listadas nunca entram em família automática; pares declarados seguem
  possíveis. Lição de maquinaria: a chave mecânica precisa de
  discriminador de geometria — enquanto não houver, o bloqueio explícito
  é a guarda.
- Sem o piso falso, o limite σ da fonte volta ao global (0,025) e o
  **hdpe_t14 (σ 0,0302) também sai do tripé**.

## Censo após o erratum

**tripé 131/203 (65 %) · fora 72 · exceções 26 · declaradas 15 ·
resolvida/declarada 172/203** · manda σ33 · mae18 · mx21 (σ domina 46 %).
Fingerprint `3d432a65c7e8` uniforme (inputs ficam fora do hash; 3
registros re-simulados no store). A fonte ROUSSEAU_2025 fica: 1 tripé
(steel_t14) + 5 fila — com o diagnóstico e as âncoras novas (0,2 mm da
Fig. 6; varredura da Fig. 10) apontando a recuperação.
