#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
import pandas as pd
import numpy as np
from shroomdk import ShroomDK
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.dates as md
import matplotlib.ticker as ticker
import numpy as np
import altair as alt
sdk = ShroomDK("679043b4-298f-4b7f-9394-54d64db46007")
st.set_page_config(page_title="Terra in 2023", layout="wide",initial_sidebar_state="collapsed")



# In[2]:


import time
my_bar = st.progress(0)

for percent_complete in range(100):
    time.sleep(0.1)
    my_bar.progress(percent_complete + 1)


# In[5]:


st.title('Terra light feather')
st.write('')
st.markdown(' The launch of Station is an interchain wallet that simplifies the often complex, cumbersome process of interacting with multiple blockchain networks. With Station, users can easily stake, vote, send and receive tokens, and interact with their favorite dApps across all supported chains [Source](https://medium.com/terra-money/introducing-station-abd478aa4059). ')
st.markdown(' The idea of this work is to try to respond if this announcement has impacted the Terra ecosystem, if users are creating new wallets or buying tokens with station new features.')
st.write('This dashboard comprehens the following sections:')
st.markdown('1. Terra main activity comparison before and after station')
st.markdown('2. Terra supply before and after station')
st.markdown('3. Terra development before and after station')
st.markdown('4. Terra staking activity before and after station')
st.write('')
st.subheader('1. Terra main activity')
st.markdown('**Methods:**')
st.write('In this analysis we will focus on the activity of Terra ecosystem during the weeks before and after station announcement. More specifically, we will analyze the following data:')
st.markdown('● Total number transactions')
st.markdown('● Total active users')
st.markdown('● Total volume moved')
st.write('')

sql="""
with txns as(
select 
  date_trunc('day',block_timestamp) as date,
  count(distinct tx_id) as n_txns,
  count(distinct tx_sender) as n_wallets,
  sum(fee) as fee_luna
from terra.core.fact_transactions
  where block_timestamp >= '2023-01-07' and block_timestamp <= '2023-01-21'
group by date
order by date desc
),
new_wallets as (
select 
  date,
  count(tx_sender) as n_new_wallets
  from (
select 
  date_trunc('day',min(block_timestamp)) as date,
  tx_sender
from terra.core.fact_transactions
group by tx_sender
)
  where date >= '2023-01-07' and date <= '2023-01-21'
group by date
)

select 
  t.*,
    case when t.date>='2023-01-14' then 'After period' else 'Previous period' end as period,
  n.n_new_wallets,
  sum(n_new_wallets) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_new_wallets
from txns t left join new_wallets n using(date)
order by date desc

"""	
st.experimental_memo(ttl=50000)
@st.cache
def memory(code):
    data=sdk.query(code)
    return data

results = memory(sql)
df = pd.DataFrame(results.records)
df.info()
    


with st.expander("Check the analysis"):
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_txns:Q',color='period')
        .properties(title='Daily transactions evolution'))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='n_txns:Q',color='period')
        .properties(title='Transactions comparison'))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_wallets:Q',color='period')
        .properties(title='Daily active wallets evolution'))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='n_wallets:Q',color='period')
        .properties(title='Active wallets comparison'))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='fee_luna:Q',color='period')
        .properties(title='Daily fees evolution',))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='fee_luna:Q',color='period')
        .properties(title='Fees comparison'))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_new_wallets:Q',color='period')
        .properties(title='Daily new users evolution'))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='n_new_wallets:Q',color='period')
        .properties(title='New users comparison'))
	
    st.write('In these graphs we have analysed the activity of Terra, as when there is an announcement the activity of an ecosystem can vary. For this reason, it has been analysed to see if there is any different movement.  Transactions, active wallets, fees and news users have been analysed. In all four cases we can see that the activity has increased favourably, especially in the first 3 days. After that the values have decreased and, in some cases, as in the case of new users, the values are the same as before the launch.')	      

		      


# In[8]:


st.subheader("2. Ecosystem development before and after station")
st.markdown('**Methods:**')
st.write('In this analysis we will focus on the Terra main ecosystem development. More specifically, we will analyze the following data:')
st.markdown('● New deployed contracts')
st.markdown('● Used contracts')
st.markdown('● Swaps activity')



sql="""
select 
   date_trunc('day',block_timestamp) as date,    
   case when date>='2023-01-14' then 'After period' else 'Previous period' end as period,
  count(distinct tx_id) as n_contracts,
  sum(n_contracts) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_contracts
from terra.core.ez_messages
where message_type = '/cosmwasm.wasm.v1.MsgInstantiateContract'
	and block_timestamp >= '2023-01-07' and block_timestamp <= '2023-01-21'
group by date, period
order by date desc


"""


sql2="""
select 
   date_trunc('day',block_timestamp) as date,
      case when date>='2023-01-14' then 'After period' else 'Previous period' end as period,
  count(distinct tx:body:messages[0]:contract) as n_contracts,
    sum(n_contracts) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_contracts
  from terra.core.fact_transactions 
  --where ATTRIBUTE_KEY in ('contract','u_contract_address','contract_name',
  --'contract_version','contract_addr','contract_address','dao_contract_address','pair_contract_addr','nft_contract')
  where block_timestamp >= '2023-01-07' and block_timestamp <= '2023-01-21'

group by date, period
order by date desc
"""


sql3="""
with txns as(
select 
  date_trunc('day',block_timestamp) as date,
      case when date>='2023-01-14' then 'After period' else 'Previous period' end as period,
  count(distinct tx_id) as n_txns,
  count(distinct trader) as n_wallets,
  sum(to_amount/1e6) as fee_luna,
  sum(n_txns) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_txns,
  sum(n_wallets) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_wallets,
  sum(fee_luna) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_fee_luna
from terra.core.ez_swaps
  where block_timestamp >= '2023-01-07' and block_timestamp <= '2023-01-21'
  and to_currency = 'uluna'
group by date, period
order by date desc
),
new_wallets as (
select 
  date,
  count(trader) as n_new_wallets
  from (
select 
  date_trunc('day',min(block_timestamp)) as date,
  trader
from terra.core.ez_swaps
group by trader
)
   where date >= '2023-01-07' and date <= '2023-01-21'
group by date
)

select 
  t.*,
  n.n_new_wallets,
  sum(n_new_wallets) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_new_wallets
from txns t left join new_wallets n using(date)
order by date desc

"""




results = memory(sql)
df = pd.DataFrame(results.records)
df.info()

results2 = memory(sql2)
df2 = pd.DataFrame(results2.records)
df2.info()

results3 = memory(sql3)
df3 = pd.DataFrame(results3.records)
df3.info()



with st.expander("Check the analysis"):
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_contracts:Q',color='period')
        .properties(title='Daily new contracts evolution'))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='n_contracts:Q',color='period')
        .properties(title='New contracts comparison'))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df2)
        .mark_bar()
        .encode(x='date:N', y='n_contracts:Q',color='period')
        .properties(title='Daily active contracts evolution'))
    
    col2.altair_chart(alt.Chart(df2)
        .mark_bar()
        .encode(x='period:N', y='n_contracts:Q',color='period')
        .properties(title='Active contracts comparison'))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='date:N', y='n_txns:Q',color='period')
        .properties(title='Daily swaps evolution'))
    
    col2.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='period:N', y='n_txns:Q',color='period')
        .properties(title='Swaps comparison'))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='date:N', y='n_wallets:Q',color='period')
        .properties(title='Daily active swappers evolution'))
    
    col2.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='period:N', y='n_wallets:Q',color='period')
        .properties(title='Active swappers comparison'))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='date:N', y='fee_luna:Q',color='period')
        .properties(title='Daily swap fees evolution'))
    
    col2.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='period:N', y='fee_luna:Q',color='period')
        .properties(title='Swap fees comparison'))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='date:N', y='n_new_wallets:Q',color='period')
        .properties(title='Daily new swappers evolution'))
    
    col2.altair_chart(alt.Chart(df3)
        .mark_bar()
        .encode(x='period:N', y='n_new_wallets:Q',color='period')
        .properties(title='New swappers comparison'))
    st.write ('In these graphs we have analysed the ecosystem development, as after a launch, the criteria analysed below may vary. Firstly, we see that daily swaps, new swappers and new contracts have had a very favourable evolution after the station. Daily active contracts and active swappers have also increased, but they were already on an upward trend before. Swap fees have increased but insignificantly.')



# In[9]:


st.subheader("3. Staking before and after station")
st.markdown('**Methods:**')
st.write('In this analysis we will focus on the Terra staking. More specifically, we will analyze the following data:')
st.markdown('● Staking actions')
st.markdown('● Stakers')
st.markdown('● Validators')



sql="""
with txns as(
select 
  date_trunc('day',block_timestamp) as date,
      case when date>='2023-01-14' then 'After period' else 'Previous period' end as period,
  count(distinct tx_id) as n_txns,
  count(distinct delegator_address) as n_wallets,
  count(distinct validator_address) as n_validators,
  sum(amount/1e6) as fee_luna,
  sum(n_txns) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_txns,
  sum(n_wallets) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_wallets,
  sum(fee_luna) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_fee_luna
from terra.core.ez_staking
  where action = 'Delegate'
  and block_timestamp >= '2023-01-07' and block_timestamp <= '2023-01-21'
group by date, period
order by date desc
),
new_wallets as (
select 
  date,
  count(delegator_address) as n_new
  from (
select 
  date_trunc('day',min(block_timestamp)) as date,
  delegator_address
from terra.core.ez_staking
group by delegator_address
)
  where date >= '2023-01-07' and date <= '2023-01-21'
group by date
),
new_validators as (
select 
  date,
  count(validator_address) as n_new
  from (
select 
  date_trunc('day',min(block_timestamp)) as date,
  validator_address
from terra.core.ez_staking
group by validator_address
)
  where date >= '2023-01-07' and date <= '2023-01-21'
group by date
)

select 
  t.*,
  coalesce(n.n_new, 0) as n_new_wallets,
  sum(n_new_wallets) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_new_wallets,
  coalesce(v.n_new, 0) as n_new_validators,
  sum(n_new_validators) over (partition by period order by date asc rows between unbounded preceding and current row) as cum_n_new_validators
from txns t 
  left join new_wallets n using(date)
  left join new_validators v using(date)
order by date desc
"""



results = memory(sql)
df = pd.DataFrame(results.records)
df.info()



with st.expander("Check the analysis"):
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_txns:Q',color='period')
        .properties(title='Daily staking actions evolution'))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='n_txns:Q',color='period')
        .properties(title='Staking actions comparison'))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_wallets:Q',color='period')
        .properties(title='Daily active stakers evolution'))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='n_wallets:Q',color='period')
        .properties(title='Active stakers comparison'))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_validators:Q',color='period')
        .properties(title='Daily validators evolution'))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='n_validators:Q',color='period')
        .properties(title='Active validators comparison'))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='fee_luna:Q',color='period')
        .properties(title='Daily staking fees evolution'))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='fee_luna:Q',color='period')
        .properties(title='Staking fees comparison'))
    
    col1,col2=st.columns(2)
    with col1:
        st.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='date:N', y='n_new_wallets:Q',color='period')
        .properties(title='Daily new stakers evolution'))
    
    col2.altair_chart(alt.Chart(df)
        .mark_bar()
        .encode(x='period:N', y='n_new_wallets:Q',color='period')
        .properties(title='New stakers comparison'))
    st.write ('Finally, we have analysed the staking before and after station. We can clearly see that daily staking actions, active stakers, staking fees and new stakers have increased significantly. However, after the first three days of the announcement, the values of these graphs went down again, almost reaching the previous values in some cases. If we look at the daily validators evolution, it is the only case where the validators remain practically the same as before the announcement. ')
    
    


# In[14]:
st.write('Key insight')

st.markdown('- Transactions, active wallets, fees and news users have been analysed the activity has increased favourably, especially in the first 3 days.')
st.markdown('- In the case of new users, the values are the same as before the launch.')
st.markdown('- Daily swaps, new swappers and new contracts have had a very favourable evolution after the station.')
st.markdown('- Daily active contracts and active swappers have also increased, but they were already on an upward trend before.')
st.markdown('- Swap fees have increased insignificantly.')
st.markdown('- Daily staking actions, active stakers, staking fees and new stakers have increased radically. ')
st.markdown('- After the first three days of the announcement, the values of these graphs went down again.')
st.markdown('- The validators remain practically the same as before the announcement.')
sr.write(' ')
sr.write(' ')


st.markdown('This dashboard has been done by _Cristina Tintó_ powered by **Flipside Crypto** data and carried out for **MetricsDAO**. ')
st.markdown('Link to full codes: https://github.com/cristinatinto/terra_light_feather')

# In[ ]:




