import pandas as pd
import numpy as np
import requests
import plotly.express as px
import streamlit as st

def IncomeStatement():


    if "my_input" not in st.session_state:
        st.session_state["my_input"] = ""

    my_input = st.text_input("Enter Ticker here", st.session_state["my_input"])
    submit = st.button("Submit")

    if submit:
        st.session_state["my_input"] = my_input
        st.write("You have entered: ", my_input)

    #API = #[Enter API KEY HERE]


    company = [my_input]


    IncomeStatment = []

    BalanceSheet = []


    for i in company:


        response_is = requests.get("https://financialmodelingprep.com/api/v3/income-statement/{0}?limit=120&apikey={1}".format(i,API))
        r_is = response_is.json()
        
        IncomeStatment.append(r_is)
        

        response_bs = requests.get("https://financialmodelingprep.com/api/v3/balance-sheet-statement/{0}?period=annual&apikey={1}".format(i,API))
        r_bs = response_bs.json()
        
        BalanceSheet.append(r_bs)



    is_flat_list = []

    for i in IncomeStatment:
        for y in i:
            is_flat_list.append(y)
        
        
    bs_flat_list = []

    for i in BalanceSheet:
        for y in i:
            bs_flat_list.append(y)


    
    is_df = pd.DataFrame.from_dict(is_flat_list)
    bs_df = pd.DataFrame.from_dict(bs_flat_list)

    #current ratio
    bs_df['Current Ratio'] = bs_df['totalCurrentAssets']/bs_df['totalCurrentLiabilities']
    Current_Ratio = bs_df[['date','symbol','calendarYear','Current Ratio']]
    

    #Quick Ratio
    bs_df['NumQR'] = bs_df['cashAndShortTermInvestments'] + bs_df['shortTermInvestments'] + bs_df['netReceivables']
    bs_df['QuickRatio']  =  bs_df['NumQR']/bs_df['totalCurrentLiabilities']
    Quick_Ratio = bs_df[['date','symbol','calendarYear','QuickRatio']]

    #Cash Ratio
    bs_df['numCashR'] = bs_df['cashAndShortTermInvestments'] + bs_df['shortTermInvestments']
    bs_df['CashRatio']  =  bs_df['numCashR']/bs_df['totalCurrentLiabilities']
    Cash_Ratio = bs_df[['date','symbol','calendarYear','CashRatio']]


    #to find the average for turnover ratios.

    def dfavg(acct):
    
    
        final_df_list = []


        df_val_list = []
        df_co_list = []
        df_date_list = []



        for i in company:

            nr = bs_df[['date','symbol','calendarYear',acct]]

            current_df = nr[nr['symbol']== i]
            current_df.sort_values(by='date')
            lastcol = current_df.columns[-1]
            current_df.rename(columns={lastcol: "Value"}, inplace=True)

            for y in range(0,len(current_df)):

                df_val_list.append(current_df.iloc[y:y+2].Value.mean())
                df_co_list.append(current_df.iloc[y].symbol)
                df_date_list.append(current_df.iloc[y].calendarYear)

        curr_dict = {'Company': df_co_list, 'Date': df_date_list, 'Value': df_val_list} 

        final_df = pd.DataFrame(curr_dict)
        
        final_df["ID"] = final_df["Company"] + final_df["Date"]

        final_df_list.append(final_df)
        
        
        return final_df_list[0]
    

    #Turn Over Ratios

    NetRecivables_df = dfavg('netReceivables')

    Revenue_Df = is_df[['date','symbol','calendarYear',"revenue"]]

    Revenue_Df['ID'] = Revenue_Df['symbol'] + Revenue_Df['calendarYear']

    Recturn_Ratio = pd.merge(NetRecivables_df, Revenue_Df, on='ID')

    Recturn_Ratio['RecivablesturnoverRatio'] = Recturn_Ratio['revenue']/Recturn_Ratio['Value']

    Recturn_Ratio['AvgReceivablesCollectionDays'] = 365/Recturn_Ratio['RecivablesturnoverRatio']



    #st.dataframe(Recturn_Ratio)

    #Inventory Turnover

    inventoryturnover_df = dfavg('inventory')

    Cogs_Df = is_df[['date','symbol','calendarYear',"costOfRevenue"]]

    Cogs_Df['ID'] = Cogs_Df['symbol'] + Cogs_Df['calendarYear']

    InvTurn_DF = pd.merge(inventoryturnover_df, Cogs_Df, on='ID')

    InvTurn_DF['InventoryTurnover'] = InvTurn_DF["costOfRevenue"]/InvTurn_DF["Value"]

    InvTurn_DF['InventoryDaysInStock'] = 365/InvTurn_DF['InventoryTurnover']

    #Payables Turnover

    AccountsPayable = dfavg('accountPayables')

    PayableTurn_DF = pd.merge(AccountsPayable, Cogs_Df, on='ID')

    PayableTurn_DF['PayableTurnover'] = PayableTurn_DF["costOfRevenue"]/PayableTurn_DF["Value"]

    PayableTurn_DF['AvgPayableOutStanding'] = 365/PayableTurn_DF['PayableTurnover']





    














    

    #Current Ratio Viz
    st.subheader('Current Ratio')
    fig_rev_ex = px.scatter(Current_Ratio , x="calendarYear", y="Current Ratio",color = 'symbol',trendline="ols",trendline_scope="overall").update_traces(mode="lines+markers")
    st.plotly_chart(fig_rev_ex)
    

    #Quick Ratio Viz
    st.subheader('Quick Ratio')
    figQR = px.scatter(Quick_Ratio , x="calendarYear", y='QuickRatio',color = 'symbol',trendline="ols",trendline_scope="overall").update_traces(mode="lines+markers")
    st.plotly_chart(figQR)


    #Cash Ratio Viz
    st.subheader('Cash Ratio')
    figCashR = px.scatter(Cash_Ratio , x="calendarYear", y='CashRatio',color = 'symbol',trendline="ols",trendline_scope="overall").update_traces(mode="lines+markers")
    st.plotly_chart(figCashR)


    #Recivables Turnover Ratio

    st.subheader('Recivables Turnover Ratio')
    figRecturnRatio = px.scatter(Recturn_Ratio , x="calendarYear", y='RecivablesturnoverRatio',color = 'symbol',trendline="ols",trendline_scope="overall").update_traces(mode="lines+markers")
    st.plotly_chart(figRecturnRatio)

    #Avg Collection Days

    st.subheader('Avg Recivables Collection Days')
    figRecCollectDays = px.scatter(Recturn_Ratio , x="calendarYear", y='AvgReceivablesCollectionDays',color = 'symbol',trendline="ols",trendline_scope="overall").update_traces(mode="lines+markers")
    st.plotly_chart(figRecCollectDays)

    #Inventory Turnover

    st.subheader('Inventory Turnover Ratio')
    figInvTurn= px.scatter(InvTurn_DF , x="calendarYear", y='InventoryTurnover',color = 'symbol',trendline="ols",trendline_scope="overall").update_traces(mode="lines+markers")
    st.plotly_chart(figInvTurn)


    #Average days inventory in stock

    st.subheader('Average days inventory in stock')
    figInvDays= px.scatter(InvTurn_DF , x="calendarYear", y='InventoryDaysInStock',color = 'symbol',trendline="ols",trendline_scope="overall").update_traces(mode="lines+markers")
    st.plotly_chart(figInvDays)


    #Payable Turnover

    st.subheader('Payables Turnover')
    figPayTurn= px.scatter(PayableTurn_DF , x="calendarYear", y='PayableTurnover',color = 'symbol',trendline="ols",trendline_scope="overall").update_traces(mode="lines+markers")
    st.plotly_chart(figPayTurn)


    #Payable Turnover

    st.subheader('Payables Days Outstanding')
    figPayOut= px.scatter(PayableTurn_DF , x="calendarYear", y='AvgPayableOutStanding',color = 'symbol',trendline="ols",trendline_scope="overall").update_traces(mode="lines+markers")
    st.plotly_chart(figPayOut)






 














        











if __name__ == "__main__":
    IncomeStatement()

