import os
import numpy as np
import pandas as pd

def get_order_info(path):
    # 這裡將訂單狀態以0, 1, 2表示
    status_dict = {"BACK" : 0, "FAIL" : 1, "CX" : 2}

    csv_path = os.path.join(path, "訂單資訊.csv")
    order = pd.read_csv(csv_path)

    order["order_status"] = order["order_status"].apply(lambda status: status_dict[status])
    order['create_date'] = pd.to_datetime(order['create_date']).dt.tz_convert(None)
    order['go_date'] = pd.to_datetime(order['go_date']).dt.tz_convert(None)
    order['back_date'] = pd.to_datetime(order['back_date']).dt.tz_convert(None)
    
    return order

def get_member_info(path):

    csv_path = os.path.join(path, "使用者資訊.csv")
    member = pd.read_csv(csv_path)

    member['create_date'] = pd.to_datetime(member['create_date'])
    member.rename(columns={'create_date': 'register_date'}, inplace=True)

    return member

def get_prod_info(path):

    csv_path = os.path.join(path, "產品資訊.csv")
    product = pd.read_csv(csv_path)

    return product

def get_anomaly_info(path):

    csv_path = os.path.join(path, "爭議帳款.csv")
    anomaly = pd.read_csv(csv_path)

    return anomaly

def get_label(anomaly, num_data):

    label = [0] * num_data
    for row in anomaly["order_id"]:
        label[row] = 1

    return np.array(label)

def add_time_feature(data):
    
    data['reg_to_create'] = (data['create_date'] - data['register_date']).apply(lambda x: int(x.total_seconds()/60))
    data['create_to_go'] = (data['go_date'] - data['create_date']).apply(lambda x: int(x.total_seconds()/60))
    
    return data

# 累積購買次數
def add_buytime_counts(data):

    count = 0
    user_record_dict = {}
    order_times = [0] * len(data)
    data = data.sort_values('create_date')
    for member in data['member_id']:
        if member in user_record_dict:
            user_record_dict[member] += 1
        else:
            user_record_dict[member] = 1
        order_times[count] = user_record_dict[member]
        count += 1

    data['buytime_counts'] = order_times

    return data

# 上次購買到這次購買之間隔時間
def add_buytime_gap(data):

    buytime_gap = []
    user_record_dict = {}
    data = data.sort_values('create_date')
    for member, create_date in zip(data['member_id'],data['create_date']):
        if member in user_record_dict:
            buytime_gap.append((create_date - user_record_dict[member]).total_seconds()/60)
            user_record_dict[member] = create_date
        else:
            buytime_gap.append(-1)
            user_record_dict[member] = create_date

    data['buytime_gap'] = buytime_gap

    return data

def get_data(path):
    # Return X, Y
    order_df = get_order_info(path)
    # print(order_df.head())
    member_df = get_member_info(path)
    # print(member_df.head())
    prod_df = get_prod_info(path)
    # print(prod_df.head())
    anomaly_df = get_anomaly_info(path)
    # print(anomaly_df.head())

    label = get_label(anomaly_df, order_df.shape[0])

    data = pd.merge(order_df, member_df, left_on="member_id", right_on="member_id")
    data = add_time_feature(data)
    data = add_buytime_counts(data)
    data = add_buytime_gap(data)

    data = data.sort_values('order_id')
    print(data.columns)
    data = data[['buytime_counts', 'buytime_gap', 'reg_to_create', 'create_to_go', 'prod_id', 'order_status', 'qty', 'price']]

    return data.to_numpy(), label