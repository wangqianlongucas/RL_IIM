# -*- coding: utf-8 -*-
# @Time    : 2023/7/27 17:19
# @Author  : wangqianlong
# @email   ：17634233142@qq.com
# @FileName: model.py
from gurobipy import *
from parameters import *


class SMIP_IIM:
    def __init__(self):
        self.model = Model('SMIP')

    def add_vars(self):
        self.HI = self.model.addVars(N, J, ER, T, vtype=GRB.INTEGER, name='HI')
        self.WI = self.model.addVars(ER, T, vtype=GRB.INTEGER, name='WI')
        self.X = self.model.addVars(J, ER, T, vtype=GRB.INTEGER, name='X')
        self.Q = self.model.addVars(ER, T, vtype=GRB.INTEGER, name='Q')
        self.Sh = self.model.addVars(N, J, T, vtype=GRB.INTEGER, name='Sh')
        self.Y = self.model.addVars(J, T, vtype=GRB.BINARY, name='Y')
        self.A = self.model.addVars(ER, T, vtype=GRB.BINARY, name='A')
        self.B = self.model.addVars(T, vtype=GRB.BINARY, name='B')
        self.V = self.model.addVars(N, J, ER, T, vtype=GRB.BINARY, name='V')
        self.ExpWar = self.model.addVars(T, vtype=GRB.INTEGER, name='ExpWar')
        self.ExpHos = self.model.addVars(N, J, T, vtype=GRB.INTEGER, name='ExpHos')
        self.d = self.model.addVars(N, J, ER, T, vtype=GRB.INTEGER, name='d')
        self.s = self.model.addVar(vtype=GRB.INTEGER, name='s')
        self.S = self.model.addVar(vtype=GRB.INTEGER, name='S')

    def set_objective(self):
        ZL = [14, 23, 5, 678]
        Z = {}
        Z[14] = quicksum(self.Q[r, t] * Price * r / E +
                         self.WI[r, t] * WHCost
                         for r in ER for t in T)
        Z[23] = quicksum(self.B[t] * OrCost +
                         self.ExpWar[t] * Price
                         for t in T)
        Z[5678] = quicksum(self.Y[j, t] * DelCost[j] +
                           quicksum(
                               P_ej[e, j] * (
                                   self.ExpHos[e, j, t] * ExpCost +
                                   quicksum(
                                       self.HI[e, j, r, t] * HHCost[j]
                                       for r in ER
                                   ) +
                                   self.Sh[e, j, t] * ShCost[j]
                               )

                               for e in N
                           )
                           for j in J for t in T)

    def constraint_23(self):
        for t in T[1:]:
            for r in ER[:-1]:
                self.model.addConstr(self.WI[r, t] == self.WI[r + 1, t - 1] + self.Q[r, t] -
                                     quicksum(self.X[j, r, t] for j in J),
                                     name=f'cons_23_{r}_{t}')
            r = E
            self.model.addConstr(self.WI[r, t] == self.Q[r, t] - quicksum(self.X[j, r, t] for j in J),
                                 name=f'cons_23_{r}_{t}')
        t = 0
        for r in ER:
            self.model.addConstr(self.WI[r, t] == WI_0_r[r], name=f'WH_I_INI_{t}_{r}')

    def constraint_4(self):
        for t in T:
            self.model.addConstr(self.ExpWar[t] == self.WI[1, t], name=f'cons_4_{t}')

    def constraint_56789(self):
        pass

    def constrains(self):
        self.constraint_23()
        self.constraint_4()

    def main(self):
        self.add_vars()
        self.set_objective()
        self.constrains()
        self.model.optimize()


smip = SMIP_IIM()
smip.main()