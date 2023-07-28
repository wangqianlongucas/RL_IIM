# -*- coding: utf-8 -*-
# @Time    : 2023/7/25 15:50
# @Author  : wangqianlong
# @email   ：17634233142@qq.com
# @FileName: parameters.py
import random
import pandas as pd
random.seed(10)


def read_demand(J, N, T, TT='train'):
    DEJT = {}
    for j in J:
        path = f'../data/{TT}_h{j}.csv'
        data = pd.read_csv(path, index_col=0)
        for e in N:
            for t in T[: -1]:
                DEJT[(e, j, t + 1)] = data.loc[e][t]
    return DEJT


TII = 1  # todo instance set here !!!

TI = {
    1: {
        'NOH': 3,
        'MaxWS': 70,
    },
}
J = [h for h in range(1, TI[TII]['NOH'] + 1)]  # Number of hospitals

# hospitals
DelCost = {i: round(random.uniform(20, 100)) for i in J}
ShCost = {i: 40 for i in J}
HHCost = {i: 2 for i in J}
MaxHS = {i: 15 for i in J}
MaxHS[1], MaxHS[2] = 30, 23

# warehouse
OrCost = 100
WHCost = 1
MaxWS = TI[TII]['MaxWS']

# items
Price = 13
ExpCost = 13

E = 3  # Maximum shelf life
ER = [r for r in range(1, E + 1)]
T = [t for t in range(10 + 1)]  # Periods
N = [e for e in range(10)]  # Number of scenarios for hospitals
WI_0_r = {r: 0 for r in ER}


M = 1e6


D_ejt = read_demand(J, N, T)
P_ej = {(e, j): 1 / len(N) for e in N for j in J}
