"""Orcamento de precisao do RELOGIO: quanta sobreposicao ha entre a janela de
colapso do MODELO e a do DADO, dado um erro de relogio eps.

Janela do dado:    [(1-phi)*Nf , Nf]         phi = fracao da vida no colapso
Janela do modelo:  [(1-phi)(1+eps)*Nf , (1+eps)*Nf]
Sobreposicao / janela do dado = max(0, 1 - |eps|/phi)
"""
PHI = {'amp0p25': 0.27, 'amp0p3': 0.29, 'amp0p4': 0.22, 'amp0p5': 0.21,
       'amp0p6': 0.26, 'amp0p8': 0.20, 'fig2': 0.20}
# eps medido: relogio Miner, m1=2.883 LIDO + 1 ancora (este estudo)
EPS_MINE = {'amp0p25': -0.138, 'amp0p3': -0.346, 'amp0p4': -0.074,
            'amp0p5': 0.000, 'amp0p6': +0.036, 'amp0p8': -0.344,
            'fig2': -0.055}
# eps do PR-24: m1=2.7 (declarado no paper) + 1 escala global fat_C1=6.7e30
EPS_PR24 = {'amp0p25': -0.168, 'amp0p4': 0.000, 'amp0p8': -0.143}

print('%-9s %6s | %8s %9s | %8s %9s' % (
    'curva', 'phi', 'eps_este', 'sobrep.', 'eps_PR24', 'sobrep.'))
for k, phi in PHI.items():
    e1 = EPS_MINE[k]
    ov1 = max(0.0, 1.0 - abs(e1) / phi)
    if k in EPS_PR24:
        e2 = EPS_PR24[k]
        ov2 = max(0.0, 1.0 - abs(e2) / phi)
        print('%-9s %6.2f | %+8.3f %8.0f%% | %+8.3f %8.0f%%'
              % (k, phi, e1, 100 * ov1, e2, 100 * ov2))
    else:
        print('%-9s %6.2f | %+8.3f %8.0f%% | %8s %9s' % (k, phi, e1, 100 * ov1, '-', '-'))

print()
phis = list(PHI.values())
pmin, pmax = min(phis), max(phis)
for target in (0.75, 0.90):
    print('  p/ sobreposicao >= %.0f%% em TODAS as curvas: |eps| <= %.1f%% '
          '(phi minimo = %.2f)' % (100 * target, 100 * (1 - target) * pmin, pmin))
print()
print('  DISPONIVEL: eps deterministico 17-35%% (PR-24 / este estudo)')
print('  IRREDUTIVEL: scatter de especime 44%% (fig2 10k vs amp0p8 14.4k, mesma amp)')
print()
print('  => o orcamento pede |eps| <= 5%%; o dado oferece 17-44%%. O relogio')
print('     PREDITIVO nao cabe no orcamento, qualquer que seja a forma da rampa.')
