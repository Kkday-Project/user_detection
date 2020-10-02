import os
import pickle
import numpy as np
import pandas as pd

from data_processing import get_data
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

def main():
    # 這裡我把所有csv檔都放在一個叫做data的資料夾底下
    # 如果你把程式碼和csv檔放在一起，就把它改成"./"就行了
    data_dir = "../data"
    save_model_path = 'model.pth'
    try:
        train_x = np.load("train_x.npy")
        train_y = np.load("train_y.npy")
    except FileNotFoundError:
        train_x, train_y = get_data(data_dir)
        np.save("train_x.npy", train_x)
        np.save("train_y.npy", train_y)

    print(train_x.shape)
    print(train_y.shape)
    # print(train_x[0])

    X_train, X_test, Y_train, Y_test = train_test_split(train_x, train_y, test_size=0.33, random_state=777)

    model = RandomForestClassifier(max_depth=None, random_state=777, n_jobs=-1)
    model.fit(X_train, Y_train)
    print(model.score(X_test, Y_test))

    # 儲存模型
    pickle.dump(model, open(save_model_path, 'wb'))
    # 讀取預先儲存的模型
    load_model = pickle.load(open(save_model_path, 'rb'))
    print(load_model.score(X_train, Y_train))

if __name__ == "__main__":
    main()