# Pendências no `report_html.py` — achadas em 2026-07-29, NÃO aplicadas

> ## ✅ RESOLVIDAS em 2026-07-29 (tarde) — pela sessão que estava com o arquivo
>
> **As duas** foram aplicadas pela outra sessão (a das "58 hunks em voo"), que
> chegou aos mesmos dois defeitos pela mesma pergunta do professor. Este
> documento fica como **registro do achado**, não de pendência — mas leia as
> divergências abaixo antes de usar os patches sugeridos, porque duas contas
> daqui foram corrigidas por medição:
>
> · **§1** virou `_tripe_block` (§3 do report por caso): as três pernas com
>   valor, limite e **múltiplo do limite**, veredicto nomeando a perna que manda,
>   e o RMSE com as duas leituras que carrega (posição na cunha
>   `MAE ≤ RMSE ≤ res.máx` + decomposição `RMSE² = viés² + σ_res²`), dito como
>   LEITURA e não porta. Os 3 sítios (870 / 888-889 / 998) e o resumo do topo
>   passaram a ler `META_*`; **zero literais 0.1 sobraram nos 203**. O número
>   daqui confere: **93 das 98** violam σ_res — e a versão mais forte é que ele é
>   a perna que **MANDA** (maior múltiplo) em **87 das 98 (89 %)**, contra 9 do
>   MAE e 2 do res.máx. Isso está publicado no painel mestre agora.
> · **§2** foi pela opção **(2), embutir**, não pela (1) recomendada aqui — o
>   professor pediu explicitamente *"as figuras podem ficar gravadas no html de
>   maneira permanente"* nesta sessão. ⚠️ Se a instrução registrada aqui ("depois
>   disse para não fazer agora") ainda vale, é uma **divergência para o professor
>   decidir**, não para uma sessão resolver sozinha.
>   Duas contas daqui saíram erradas na medição: (a) o custo não é "50 figuras =
>   7 MB", é **243 usos de 49 figuras** ⇒ 203 reports de 18,4 → **37,9 MB**
>   (2,06×); (b) reduzir para ~900 px **quase não ajuda**, porque a mediana do
>   acervo já é **776 px** — quem faz o trabalho é a **paleta** (PNG indexado 128
>   cores, erro médio **< 1/255 por canal nas 49**). WebP q80 daria 33,6 MB e foi
>   **recusado por princípio**: a figura é o instrumento da conferência da
>   digitalização, e comprimi-la com perda troca a coisa medida pela medição.
>
> Invariantes presos em `tests/test_scatter3_panel.py`.

**Por que não aplicadas:** o professor avisou que está *"em outra frente"* e o
arquivo tem 58 hunks / 768 linhas de trabalho em voo de outra sessão (marca
`_marca3` com triângulo para ponto recortado, `data-cid` no `<a>`, `tabindex`).
Editar ali agora atropelaria aquele trabalho. As duas pendências abaixo estão
com localização exata e o patch pronto — quem pegar o arquivo quieto aplica em
uma passada.

---

## 1. ⚠️ O report POR CASO ficou na régua ANTIGA (defeito de coerência)

O documento mestre já lê o tripé de três pernas (res.máx ≤ 0,10 · MAE ≤ 0,05 ·
σ_res ≤ 0,025 ⇒ 104 + 44 exceções = 148/202). **A página de cada caso não.** Ela
julga pelo MAE sozinho contra **0,10**, que é o limite de duas réguas atrás.
Consequência: o mestre pode dizer que uma curva está fora e o report dela dizer
"modelo no alvo", na mesma geração.

Sítios (linhas de 2026-07-29, confira antes de aplicar):

| linha | o que está lá | o que deveria |
|---|---|---|
| 870 | `mae_html` colore por `(result.mae or 1) <= 0.1` | `<= META_MAE` |
| 888-889 | MAE por estágio: `"no alvo" if v <= 0.1 else "acima do alvo 0.1"` | comparar com `META_MAE` e nomear o limite pelo valor da constante |
| 998 | `<p class="exec">` … `"good" if result.mae <= 0.1` … `"no alvo (≤0.1)"` | as **três** pernas, cada uma com o seu limite |

**E falta o σ_res na página.** Hoje a linha 879 (`sub`) mostra `RMSE` e
`erro máx`; o σ_res — que é a perna que reprova **93 das 98 fora** — não aparece
em lugar nenhum do report por caso. Era a pergunta do professor (*"o rms foi
abordado nas páginas específicas?"*): o RMSE está lá, mas como número solto, sem
limite e sem a decomposição que o mestre publica.

**Patch sugerido** (substituir o `sub` da linha 879 por um bloco de veredicto por
perna, com os limites vindos das constantes e a decomposição `RMSE² = viés² +
σ_res²` explicada em uma linha):

```python
        _v = lambda ok: "good" if ok else "warn"
        sub = (f'<div class="sub2">'
               f'<b>Tripé por perna</b> — '
               f'<span class="{_v(result.maxerr is not None and result.maxerr <= META_MAX)}">'
               f'res.máx {_fnum(result.maxerr)} / {META_MAX:.4g}</span> · '
               f'<span class="{_v(result.mae is not None and result.mae <= META_MAE)}">'
               f'MAE {_fnum(result.mae)} / {META_MAE:.4g}</span> · '
               f'<span class="{_v(result.resid_std is not None and result.resid_std <= META_SRES)}">'
               f'σ_res {_fnum(result.resid_std)} / {META_SRES:.4g}</span>'
               f' &#183; RMSE {_fnum(result.rmse)} (leitura, não perna: '
               f'MAE &le; RMSE &le; res.máx sempre) &#183; erro máx @ ciclo '
               f'{_fnum(result.maxerr_at)}{camp}</div>')
```

Além disso, `_error_narrative` (linha ~129) fala só do MAE (*"Em média o modelo
erra X pontos percentuais"*). Com a régua nova ela deveria dizer **qual perna
reprovou** — é a informação que decide o que atacar naquele caso.

## 2. A figura do artigo (§3b) NÃO carrega quando a página é servida por HTTP

O `<img src="../../variable_explorer/paper_figures/…">` funciona em `file://`,
mas quebra servido de dentro de `validation_html/`: `../../` **escapa da raiz do
servidor** e dá 404. Foi como o professor viu o defeito
(`http://127.0.0.1:8792/reports/lu2024_M8_fig20_T10Nm.html`).

Três saídas, em ordem de custo:

1. **Cópia dentro da raiz** — copiar as 50 PNGs para
   `validation_html/paper_figures/` no `write_reports` e usar
   `figpre="../paper_figures/"`. ~7 MB duplicados, zero mudança de conceito,
   funciona em `file://` **e** em HTTP.
2. **Embutir em base64** (foi o que o professor levantou e depois disse para não
   fazer agora): torna cada report autossuficiente de verdade — o princípio
   declarado do `_CSS` ("inline e self-contained") — mas as 50 figuras somam
   **7,0 MB** (média 137 kB, maior 372 kB) e a mesma figura se repete em todos os
   casos da fonte: o BAUER fig6 entraria 9 vezes. Antes de embutir vale reduzir
   (largura ~900 px já basta para conferência visual) e medir o tamanho final por
   report.
3. Servir a partir de `New_Theory/` em vez de `validation_html/` — resolve o HTTP
   sem tocar em código, mas depende de quem sobe o servidor lembrar.

**Recomendação:** a (1). Ela conserta o defeito real com um `shutil.copy2` no
gerador e não inflaciona 202 arquivos.

---

## Estado do que ficou pronto e fora de commit

`_fila_html` (item 2 das melhorias — a fila de prioridade por razão valor/piso)
está no working tree e **funcionando** na página: 27 curvas ordenadas, topo
`zhang18_fig13_14kN` a 5,3× o piso, mais 27 não ordenáveis por falta de piso
medido. Fragmento salvo fora do repo contra um revert; a chamada a preservar é
`_fila_html(trio, pisos)` no `return` de `_erro_section`.
