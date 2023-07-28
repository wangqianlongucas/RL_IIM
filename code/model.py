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
        self.Z = {}

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
        ZL = [14, 23, 5678]

        self.Z[14] = quicksum(self.Q[r, t] * Price * r / E +
                         self.WI[r, t] * WHCost
                         for r in ER for t in T)
        self.Z[23] = quicksum(self.B[t] * OrCost +
                         self.ExpWar[t] * Price
                         for t in T)
        self.Z[5678] = quicksum(self.Y[j, t] * DelCost[j] +
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
        self.model.setObjective(quicksum(self.Z[zi] for zi in ZL), GRB.MINIMIZE)

    def constraint_2_3(self):
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

    def constraint_5_9(self):
        for t in T[1:]:
            self.model.addConstr(quicksum(self.WI[r, t] for r in ER) - self.ExpWar[t] - self.s <= M * (1 - self.B[t]),
                                 name=f'cons_5_{t}')
            self.model.addConstr(quicksum(self.WI[r, t] for r in ER) - self.ExpWar[t] - self.s >= - M * self.B[t] + 1,
                                 name=f'cons_6_{t}')
            self.model.addConstr(quicksum(self.WI[r, t - 1] for r in ER) + quicksum(self.Q[r, t] for r in ER)
                                 - self.ExpWar[t] - self.S >= - M * (1 - self.B[t]),
                                 name=f'cons_7_{t}')
            self.model.addConstr(quicksum(self.WI[r, t - 1] for r in ER) + quicksum(self.Q[r, t] for r in ER)
                                 - self.ExpWar[t] - self.S <= M * (1 - self.B[t]),
                                 name=f'cons_8_{t}')
            for r in ER:
                self.model.addConstr(self.Q[r, t] <= M * self.B[t], name=f'cons_9_{r}_{t}')

    def constraint_11(self):
        for j in J:
            for t in T[1:]:
                self.model.addConstr(quicksum(self.X[j, r, t] for r in ER) <= M * self.Y[j, t], name=f'cons_11_{j}_{t}')

    def constraint_12_15(self):
        for r in ER[:-1]:
            for t in T:
                self.model.addConstr(self.WI[r, t] >= - M * (1 - self.A[r, t]) + 1, name=f'cons_12_{r}_{t}')
                self.model.addConstr(self.WI[r, t] <= M * self.A[r, t], name=f'cons_13_{r}_{t}')
                for j in J:
                    self.model.addConstr(quicksum(self.X[j, r_, t] for r_ in ER[r:]) >= - M * (1 - self.A[r, t]),
                                         name=f'cons_14_{r}_{t}_{j}')
                    self.model.addConstr(quicksum(self.X[j, r_, t] for r_ in ER[r:]) <= M * (1 - self.A[r, t]),
                                         name=f'cons_15_{r}_{t}_{j}')

    def constraint_16(self):
        for t in T[1:]:
            self.model.addConstr(quicksum(self.WI[r+1, t-1] for r in ER[:-1]) + quicksum(self.Q[r, t] for r in ER) <= MaxWS,
                                 name=f'cons_16_{t}')

    def constraint_17_18(self):
        for e in N:
            for t in T[1:]:
                for j in J:
                    for r in ER[:-1]:
                        self.model.addConstr(self.HI[e, j, r, t] == self.HI[e, j, r + 1, t - 1] + self.X[j, r, t] -
                                             self.d[e, j, r, t],
                                             name=f'cons_17_{e}_{j}_{r}_{t}')
                    r = E
                    self.model.addConstr(self.HI[e, j, r, t] == self.X[j, r, t] - self.d[e, j, r, t],
                                         name=f'cons_18_{e}_{j}_{r}_{t}')

    def constraint_19_20(self):
        for j in J:
            for e in N:
                for t in T[1:]:
                    self.model.addConstr(self.ExpHos[e, j, t] == self.HI[e, j, 1, t], name=f'cons_19_{e}_{j}_{t}')
                    self.model.addConstr(quicksum(self.d[e, j, r, t] for r in ER) + self.Sh[e, j, t] ==
                                         D_ejt[(e, j, t)] + self.Sh[e, j, t - 1],
                                         name=f'cons_20_{e}_{j}_{t}')

    def constraint_21_24(self):
        for j in J:
            for r in ER[:-1]:
                for t in T:
                    for e in N:
                        self.model.addConstr(self.HI[e, j, r, t] >= - M * (1 - self.V[e, j, r, t]) + 1,
                                             name=f'cons_21_{e}_{j}_{r}_{t}')
                        self.model.addConstr(self.HI[e, j, r, t] <= M * (1 - self.V[e, j, r, t]),
                                             name=f'cons_22_{e}_{j}_{r}_{t}')
                        self.model.addConstr(quicksum(self.d[e, j, r_, t] for r_ in ER[r:]) >= - M * (1 - self.V[e, j, r, t]) + 1,
                                             name=f'cons_23_{e}_{j}_{r}_{t}')
                        self.model.addConstr(quicksum(self.d[e, j, r_, t] for r_ in ER[r:]) <= M * (1 - self.V[e, j, r, t]),
                                             name=f'cons_24_{e}_{j}_{r}_{t}')

    def constraint_25(self):
        for j in J:
            for t in T[1:]:
                for e in N:
                    self.model.addConstr(quicksum(self.HI[e, j, r + 1, t - 1] for r in ER[:-1]) +
                                         quicksum(self.X[j, r, t] for r in ER) <= MaxHS[j],
                                         name=f'cons_25_{j}_{t}_{e}')

    def constraints(self):
        self.constraint_2_3()
        self.constraint_4()
        self.constraint_5_9()
        self.model.addConstr(self.s + 1 <= self.S, name=f'cons_10')
        self.constraint_11()
        self.constraint_12_15()
        self.constraint_16()
        self.constraint_17_18()
        self.constraint_19_20()
        self.constraint_21_24()
        self.constraint_25()

    def output(self):
        if self.model.Status == 3:
            print('约束冲突')
            # 输出约束冲突内容
            self.model.computeIIS()
            self.model.write('smip_model.ilp')
        elif self.model.Status == 2:
            self.model.write('smip_model.lp')
            print()
            print('-' * 10, 'Ss policy', '-' * 10)
            print(f's: {self.s.X}, S:{self.S.X}')
            print()
        else:
            print('infeasible!')

    def main(self):
        self.add_vars()
        self.set_objective()
        self.constraints()
        self.model.optimize()
        self.output()


if __name__ == '__main__':
    smip = SMIP_IIM()
    smip.main()
