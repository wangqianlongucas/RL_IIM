# -*- coding: utf-8 -*-
# @Time    : 2023/7/25 15:08
# @Author  : wangqianlong
# @email   ：17634233142@qq.com
# @FileName: data_generate.py
import random
import pandas as pd


def create_one_T_data(T, U):
    # T: len of T, U = [a, b]
    data = [round(random.uniform(U[0], U[1])) for i in range(T)]
    return data


def data_generate(path, n, T, U):
    datas = []
    for i in range(n):
        datas.append([i] + create_one_T_data(T, U))
    col = ['scenario']
    col += [i for i in range(T)]
    df = pd.DataFrame(datas, columns=col)
    df.to_csv(path, index=False)


if __name__ == '__main__':
    hospital_U_TI1 = {
        1: [0, 20],
        2: [0, 15],
        3: [0, 10],
    }
    N = {
        'train': 10,
        'test': 5,
    }
    T = 10
    for key, U in hospital_U_TI1.items():
        # train
        path_train = f'../data/train_h{key}.csv'
        data_generate(path_train, N['train'], T, U)
        # test
        path_test = f'../data/test_h{key}.csv'
        data_generate(path_test, N['test'], T, U)
