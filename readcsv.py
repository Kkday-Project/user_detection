import pandas as pd
from tqdm import tqdm
from datetime import datetime
import numpy as np

#read csv and casting

user = pd.read_csv('使用者資訊.csv', encoding = 'utf-8')
user['create_date'] = pd.to_datetime(user['create_date'])
user.rename(columns={'create_date': 'register_date'}, inplace=True)
order = pd.read_csv('訂單資訊.csv',encoding = 'utf-8')
order['create_date'] = pd.to_datetime(order['create_date']).dt.tz_convert(None)
order['go_date'] = pd.to_datetime(order['go_date']).dt.tz_convert(None)
order['back_date'] = pd.to_datetime(order['back_date']).dt.tz_convert(None)
argue = pd.read_csv('爭議帳款.csv',encoding = 'utf-8')
argue['dispute_date'] = pd.to_datetime(argue['dispute_date'])
product = pd.read_csv('產品資訊.csv',encoding = 'utf-8')

# mer = order.merge(argue)
# mer2 = pd.merge(mer, user, left_on="member_id", right_on="member_id")


# feature


data = pd.DataFrame()
data[['order_id','member_id','create_date','go_date','prod_id']] = order[['order_id','member_id','create_date','go_date','prod_id']]

label = [0] * len(order)
for row in argue["order_id"]:
    label[row] = 1
data['label'] = label

data = pd.merge(data, user, left_on="member_id", right_on="member_id")
# data = pd.merge(data, product,  left_on="prod_id", right_on="prod_oid")

data[['order_status','qty', 'price']] = order[['order_status','qty', 'price']]
data['reg_to_create'] = (data['create_date'] - data['register_date']).apply(lambda x: int(x.total_seconds()/60))
data['create_to_go'] = (data['go_date'] - data['create_date']).apply(lambda x: int(x.total_seconds()/60))

order.index = pd.to_datetime(order.create_date)
order = order.sort_index()

data = data.sort_values('create_date')

# 累積購買次數
order_times = [0] * len(order)
user_record_dict = {}
pbar = tqdm(len(data['member_id'])) 
count = 0
for member in data['member_id']:
    if member in user_record_dict:
        user_record_dict[member] += 1
    else:
        user_record_dict[member] = 1
    order_times[count] = user_record_dict[member]
    count += 1
    pbar.update(1)
pbar.close()
data['order_times'] = order_times

# 上次購買到這次購買之間隔時間
buytime_gap = []
user_record_dict = {}
pbar = tqdm(len(data['member_id']))
for member, create_date in zip(data['member_id'],data['create_date']):
    if member in user_record_dict:
        buytime_gap.append((create_date - user_record_dict[member]).total_seconds()/60)
        user_record_dict[member] = create_date
    else:
        buytime_gap.append('noRecord')
        user_record_dict[member] = create_date
    pbar.update(1)
pbar.close()
data['buytime_gap'] = buytime_gap



# 行為特徵
"""
action = pd.read_csv('使用者行為.csv', encoding = 'utf-8')
action['action_time'] = pd.to_datetime(action['action_time'])
action = action.sort_values('action_time')

user_record_dict = {}
pbar = tqdm(len(action['member_id'])) 
for member, time, act, product in zip(action['member_id'], action['action_time'], action['action'], action['prod_id']):
    if member in user_record_dict:
        user_record_dict[member].append([time,act,product])
    else:
        user_record_dict[member] = []
        user_record_dict[member].append([time,act,product])
    pbar.update(1)
pbar.close()

for order_id, member_id in zip(data['order_id'], data['member_id']):
    
    
    
    
"""


# label

# label = [0] * len(order)
# for row in argue["order_id"]:
#     label[row] = 1
# data['label'] = label