# Parâmetros para Reprodução Numérica — Zhang, Jiang & Lee (2007)

**Referência completa:** Zhang, M.; Jiang, Y.; Lee, C.-H. "Finite Element Modeling of Self-Loosening of Bolted Joints." *ASME Journal of Mechanical Design*, Vol. 129, pp. 218–226, February 2007. DOI: 10.1115/1.2406092

**Software utilizado:** ABAQUS (solver) + Hypermesh (pré-processamento da malha)

**Objetivo:** Simulação 3D do afrouxamento de Estágio II (back-off da porca com redução gradual da força de aperto) em junta aparafusada sob carga transversal cíclica.

---

## 1. Geometria da Rosca — M12×1.75 (ISO)

| Parâmetro | Valor |
|-----------|-------|
| Designação | M12×1.75 (rosca métrica ISO) |
| Diâmetro nominal, *d* | 12 mm |
| Passo, *P* | 1.75 mm |
| Ângulo do filete (lead angle), *α* | 2.66° |
| Condição de engajamento | Comprimento médio (*medium length*) |
| Grau de tolerância | 6 |
| Ajuste rosca (designação) | **6H/6g** (6H = porca, 6g = parafuso) |
| Folga entre diâmetros primitivos | ≈ 0.138 mm |
| Nº de filetes modelados na porca | **4** |
| Nº de filetes modelados no parafuso | **6** |
| Classe de resistência do parafuso | 10.9 (σ_y = 1040 MPa) |

> **Nota:** Os filetes foram criados fielmente ao padrão ISO. O corpo do parafuso (cilindro) e as roscas (hélice) foram modelados e mallhados separadamente, depois acoplados via *fixed contact elements*.

---

## 2. Geometria do Conjunto (Junta)

O modelo reproduz o setup experimental descrito em Jiang et al. (2004), ASME J. Mech. Des., 126:925–931.

### Componentes do modelo FE

| Componente | Material | Descrição |
|------------|----------|-----------|
| Parafuso (bolt) | Aço (Classe 10.9) | Corpo cilíndrico + roscas helicoidais |
| Porca (nut) | Aço | 4 filetes internos |
| Placa superior (top plate) | Aço | Placa de aperto — recebe deslocamento transversal |
| Placa inferior (fixed plate) | Aço | Placa fixa — extremidade esquerda engastada |
| Insertos de ferro fundido (2×) | Ferro fundido | Superfícies de contato entre as placas; um inserto ligado à placa superior, outro à placa inferior |
| Célula de carga (load cell) | Aço (propriedades ortotrópicas de expansão) | Posicionada entre a placa inferior e a cabeça do parafuso |

### Condições de contorno

- **Placa inferior:** extremidade esquerda fixa (engaste)
- **Placa superior:** deslocamento uniformemente distribuído aplicado na extremidade direita
- **Mola auxiliar:** elemento de mola com rigidez de **100 N/mm** acoplado à placa móvel (para evitar singularidade numérica durante o escorregamento entre placas). A força gerada por esta mola é desprezível e não afeta os resultados.

### Ligações entre componentes

| Interface | Tipo de conexão |
|-----------|-----------------|
| Inserto superior ↔ Placa superior | *Tied* (colado) |
| Inserto inferior ↔ Placa inferior | *Tied* (colado) |
| Corpo do parafuso ↔ Roscas helicoidais | *Fixed contact elements* |

---

## 3. Propriedades dos Materiais

**Todos os materiais foram considerados elásticos lineares** (o Estágio II é dominado por deformação elástica; a plasticidade tem efeito menor).

| Material | Módulo de Elasticidade, *E* | Coeficiente de Poisson, *ν* | Aplicação |
|----------|----------------------------|----------------------------|-----------|
| Aço | **206.8 GPa** | **0.28** | Parafuso, porca, placas, célula de carga |
| Ferro fundido | **103.4 GPa** | **0.28** | Insertos de desgaste entre as placas |

### Dados complementares de resistência (do estudo experimental associado)

| Parâmetro | Valor | Fonte |
|-----------|-------|-------|
| Tensão de escoamento (Classe 10.9) | 1040 MPa | Zhang & Jiang, 2007 |
| Tensão de escoamento (aço 1070, referência) | 449 MPa | Zhang & Jiang, 2007 |
| Tratamento dos parafusos comerciais | Laminação a frio após tratamento térmico | Informação do artigo |

---

## 4. Coeficientes de Atrito

| Interface de contato | Coeficiente de atrito, *μ* | Observação |
|----------------------|---------------------------|------------|
| **Rosca (bolt-nut threads)**, *μ_t* | **0.09** | Determinado experimentalmente (Jiang et al., 2002) |
| **Face da porca (nut bearing surface)**, *μ_n* | **0.12** | Determinado experimentalmente (Jiang et al., 2002) |
| Insertos de ferro fundido (entre si) | **0.3** | Valor assumido |
| Placa fixa ↔ Célula de carga | **0.3** | Valor assumido |
| Célula de carga ↔ Cabeça do parafuso | **0.3** | Valor assumido |

> **Nota:** Os coeficientes de atrito foram considerados **isotrópicos** em todas as interfaces. O método experimental para determinação de μ_t e μ_n está descrito em Jiang et al. (2002), *Proceedings ASME PVP Conference*, Vancouver, PVP Vol. 433, pp. 59–66.

---

## 5. Formulação de Contato

| Parâmetro | Escolha | Justificativa |
|-----------|---------|---------------|
| Formulação | **Infinitesimal sliding** | Movimentos relativos pequenos entre superfícies; ignora efeitos geométricos não-lineares |
| Alternativas disponíveis no ABAQUS | Finite sliding, Small sliding | Não utilizadas neste trabalho |
| Vantagem | Redução significativa do tempo computacional | — |

> **Nota:** A diferença entre *infinitesimal-sliding* e *small-sliding* é que a primeira ignora o efeito geométrico não-linear. Ambas são projetadas para considerar grandes movimentos entre dois corpos.

---

## 6. Malha de Elementos Finitos

| Parâmetro | Valor |
|-----------|-------|
| Total de nós | **22,387** |
| Total de elementos | **20,982** |
| Tipo de elemento | **Brick sólido de 8 nós** (C3D8 ou equivalente) |
| Tamanho mínimo do elemento (região de contato das roscas) | **0.5 mm** |
| Justificativa do tipo de elemento | Elementos brick de 8 nós são preferidos para análises envolvendo contatos de superfície |

---

## 7. Aplicação da Pré-carga — Método de Expansão Térmica Ortotrópica

A pré-carga foi simulada por expansão térmica **ortotrópica** na célula de carga:

| Parâmetro | Valor |
|-----------|-------|
| Coeficiente de expansão térmica na direção *z* (axial do parafuso) | **3.5 × 10⁻⁴ /°C** |
| Coeficiente de expansão térmica nas direções *x* e *y* | **0** (zero) |
| Relação temperatura → pré-carga | **1 °C → 0.822 kN** |
| Componente aquecido | Somente a célula de carga |
| Demais componentes | Sem expansão térmica |

### Temperaturas necessárias para cada pré-carga

| Pré-carga desejada, *P₀* (kN) | Temperatura aplicada (°C) |
|-------------------------------|--------------------------|
| 25 | ≈ 30.4 |
| 32 | ≈ 38.9 |
| 40 | ≈ 48.7 |

> **Nota:** A temperatura e o coeficiente de expansão são **artificiais** — servem apenas para gerar a pré-carga. Não representam propriedades térmicas reais do material.

---

## 8. Aplicação da Carga Transversal

### Protocolo de carregamento cíclico

Um ciclo completo de carga transversal é composto por **4 passos (steps)**:

1. Deslocamento positivo (direção +*x*) até o máximo → δ = +Δδ/2
2. Retorno ao zero → δ = 0
3. Deslocamento negativo (direção −*x*) até o máximo → δ = −Δδ/2
4. Retorno ao zero → δ = 0

| Parâmetro | Valor |
|-----------|-------|
| Tipo de controle | **Deslocamento imposto** (uniformemente distribuído) |
| Incrementos por step | **4 a 10** |
| Número total de ciclos simulados | **8 ciclos** por caso |
| Tempo computacional por simulação | **≈ 35 horas** (NCSA supercomputer, ~2005) |

---

## 9. Casos de Carga Simulados

### Tabela completa (Table 1 do artigo)

| Caso | Pré-carga, *P₀* (kN) | Amplitude de deslocamento, Δδ/2 (mm) |
|------|----------------------|--------------------------------------|
| I | 25 | 0.45 |
| II | 25 | 0.40 |
| III | 25 | 0.35 |
| IV | 25 | 0.30 |
| V | 25 | 0.25 |
| VI | 25 | 0.20 |
| VII | 32 | 0.45 |
| VIII | 40 | 0.45 |

### Variáveis de estudo

- **Efeito da amplitude de deslocamento:** Casos I–VI (P₀ fixo = 25 kN, Δδ/2 variando de 0.20 a 0.45 mm)
- **Efeito da pré-carga:** Casos I, VII, VIII (Δδ/2 fixo = 0.45 mm, P₀ variando de 25 a 40 kN)
- **Efeito do atrito entre placas:** Dois subcasos com μ = 0.1 e μ = 0.3 entre as placas (resultado: afrouxamento praticamente idêntico, confirmando que Δδ/2 é o parâmetro dominante)

---

## 10. Resultados Quantitativos de Referência (para validação)

### Caso I (P₀ = 25 kN, Δδ/2 = 0.45 mm) — Caso principal

| Métrica | Valor aproximado após 8 ciclos |
|---------|-------------------------------|
| P/P₀ (clamping force ratio) | ≈ 80–82% |
| Rotação da porca, θ | ≈ 3.0–3.5° |
| Concordância FE vs. Experimental | Quantitativa favorável (Fig. 2 do artigo) |

### Pressão de contato na 1ª rosca engajada (Caso I)

| Condição | Nó A (α = 0°) | Nó C (α = 90°) | Nó E (α = 180°) |
|----------|---------------|-----------------|------------------|
| Após aplicação da pré-carga | ≈ 380 MPa | ≈ 380 MPa | ≈ 380 MPa |
| δ = +0.45 mm (max +x) | ≈ 0 MPa (possível separação) | ≈ 400 MPa | — |
| δ = 0 (retorno do +x) | ≈ 420 MPa (máximo) | — | ≈ 300 MPa |
| δ = −0.45 mm (max −x) | Levemente reduzida | ≈ 380 MPa | ≈ 0 MPa |

### Microescorregamento (microslip) na 1ª rosca engajada

| Parâmetro | Valor |
|-----------|-------|
| Amplitude máxima de microslip radial | ≈ 0.04 mm (nos extremos α = 0° e 180°) |
| Amplitude de slip relativo entre 1ª rosca engajada | 0.0381 mm |
| Distribuição ao longo das roscas | 1ª rosca: máximo; 2ª–4ª: redução drástica |
| Momento fletor por comprimento na 1ª rosca | 1.9 N·m/mm |

---

## 11. Modelo Simplificado de Validação — Blocos Inclinados

Para confirmar os mecanismos, Zhang & Jiang criaram dois modelos simplificados de blocos inclinados representando o contato entre filetes:

### Geometria dos blocos

| Parâmetro | Valor |
|-----------|-------|
| Dimensão da seção x-z | **5.5 × 1.7 mm** |
| Ângulo de inclinação (= lead angle) | **2.66°** |
| Bloco superior | Representa o parafuso |
| Bloco inferior | Representa a porca (fixo) |

### Modelo 1 — Microslip puro (sem momento fletor)

| Parâmetro | Valor |
|-----------|-------|
| Pressão de contato média | 400 MPa |
| Amplitude de deslocamento transversal (direção z) | 0.036 mm |
| Coeficiente de atrito | 0.09 |
| Mola auxiliar (prevenção de singularidade) | 1 × 10⁻⁵ N/mm (vertical) |
| Cantos do bloco superior | Arredondados (para evitar singularidade de tensão) |
| **Resultado: taxa de deslizamento** | **0.072 mm/ciclo (≈ 0.36°/ciclo)** |

#### Modelo analítico correspondente (Eq. 1 e 2 do artigo)

```
tan(θ) = tan(α) / μ                    ... (Eq. 1)

d = t × tan(θ) = (tan(α) / μ) × t      ... (Eq. 2)
```

Para μ = 0.09, α = 2.66°, t = 0.036 mm:
- d = 0.0186 mm por step
- d = 0.0744 mm por ciclo (4 steps/ciclo)
- **Concordância excelente com o valor FE de 0.072 mm/ciclo**

### Modelo 2 — Stick-slip puro (momento fletor sem microslip)

| Parâmetro | Valor |
|-----------|-------|
| Carga vertical no bloco superior | 3.9 kN |
| Pressão de contato média | 400 MPa |
| Amplitude do momento fletor (totalmente reverso) | 10.5 N·m |
| Coeficiente de atrito | 0.09 |
| Comprimento do bloco (para cálculo do momento) | 5.5 mm |
| **Resultado: taxa de rotação** | **≈ 0.023°/ciclo** |

#### Critério stick-slip

```
η = τ / (μ × p)
```

- Se η < μ → **stick** (aderência)
- Se η = μ → **slip** (escorregamento)
- η > μ → **impossível** (fisicamente)

> **Conclusão:** A combinação de microslip e momento fletor reverso produz o afrouxamento. O microslip é o mecanismo dominante (0.36°/ciclo vs. 0.023°/ciclo), mas o efeito combinado **não é linear** (não é a soma simples dos dois).

---

## 12. Nomenclatura Completa

| Símbolo | Descrição | Unidade |
|---------|-----------|---------|
| *P* | Força de aperto (clamping force) | kN |
| *P₀* | Pré-carga inicial (preload) | kN |
| *δ* | Deslocamento relativo entre as duas placas de aperto | mm |
| *Δδ/2* | Amplitude do deslocamento relativo entre placas | mm |
| *ΔQ/2* | Amplitude da carga aplicada | kN |
| *θ* | Ângulo de rotação relativo entre porca e parafuso | ° (graus) |
| *μ_t* | Coeficiente de atrito na rosca (thread friction) | — |
| *μ_n* | Coeficiente de atrito na face de apoio da porca (bearing friction) | — |
| *α* | Ângulo de inclinação do filete (lead angle) | ° (graus) |
| *E* | Módulo de elasticidade | GPa |
| *ν* | Coeficiente de Poisson | — |

---

## 13. Referências Experimentais Associadas

Para reprodução completa, os seguintes artigos complementam os dados:

| Ref. | Conteúdo | Citação |
|------|----------|---------|
| [21] | Determinação experimental de μ_t e μ_n | Jiang, Y. et al. (2002), *Proc. ASME PVP Conference*, Vancouver, PVP Vol. 433, pp. 59–66 |
| [22] | Dados experimentais de afrouxamento (validação) | Jiang, Y. et al. (2004), *ASME J. Mech. Des.*, 126:925–931. DOI: 10.1115/1.1767814 |
| [23] | Estágio I — afrouxamento precoce (plasticidade cíclica) | Jiang, Y. & Zhang, M. (2003), *ASME J. Mech. Des.*, 125:518–526 |

---

## 14. Resumo dos Mecanismos Identificados (Stage II)

1. **Microslip entre roscas engajadas:** Causado pelo momento fletor cíclico induzido pela carga transversal. A 1ª rosca engajada sofre o maior microslip. O escorregamento radial repetitivo faz o bloco "descer" pela superfície inclinada (lead angle), equivalente à rotação da porca.

2. **Variação cíclica da pressão de contato:** O momento fletor oscilante causa variação significativa (de ~0 a ~420 MPa) na pressão de contato ao longo da circunferência das roscas, gerando alternância stick-slip localizada.

3. **Efeito combinado não-linear:** O microslip puro produz ~0.36°/ciclo e o stick-slip puro ~0.023°/ciclo, mas o efeito combinado real não é a soma aritmética.

4. **Parâmetro controlador:** O deslocamento relativo entre as placas (Δδ/2) é o principal parâmetro — o coeficiente de atrito entre as placas **não afeta** o afrouxamento (apenas muda a relação Q-δ).

5. **Maior pré-carga → maior resistência ao afrouxamento** (confirmado tanto por FE quanto experimentalmente).
