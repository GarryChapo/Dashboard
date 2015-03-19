import logging
import os

from oauth2client.appengine import oauth2decorator_from_clientsecrets
import webapp2

import bqclient
from gviz_data_table import encode
from gviz_data_table import Table

from google.appengine.api import memcache
from google.appengine.ext.webapp.template import render


CLIENT_SECRETS = os.path.join(os.path.dirname(__file__), 'client_secrets.json')
SCOPES = [
    'https://www.googleapis.com/auth/bigquery'
]
decorator = oauth2decorator_from_clientsecrets(
    filename=CLIENT_SECRETS,
    scope=SCOPES,
    cache=memcache)

# Common value for Query
BILLING_PROJECT_ID = "1011003757378"
WHERE = "where (Impression > 0) "

#Query Country Line Graph
SELECTCTLINE = "SELECT Date,Country,Sum(Impression) as Imp,Sum( Clicks) as Clicks,Round(Sum(Sum(Clicks)/Sum(Impression))*100,2) as CTR,Round(Sum(sum(Posimp)/Imp),2) as AvgPos,Round(Sum(Sum(Cost)/Sum(Clicks)),2) as CPC,Round(Sum(Cost),2) as Costs,Sum(AdWordsConversions) as ConvAdw,Sum(DFATransactions) as Sales,Sum(DFAActions) as Optin,Round(Sum(Sum(DFATransactions)/Sum(Clicks))*100,2) as CVRSales,Round(Sum(Sum(DFAActions)/Sum(Clicks))*100,2) as CVROptin,Round(Sum(Revenu),2) as CA,Round(Sum(Sum(Cost)/Sum(Revenu))*100,2) as TxDistri,Round(Sum(sum(Revenu)/sum(DFATransactions)),2) as AvgBasket "
FROMCTLINE = "from (Select Date, NTH(3,split(Campaign,\"_\")) as Country,Impression,Clicks,Posimp,Cost,AdWordsConversions,DFAActions,DFATransactions,Revenu FROM (Table_Query(elce_ds_reports_vf,'table_id contains \"left_join_report\"'))) "
GROUPBYCTLINE = "Group by Date,Country "
ORDERBYCTLINE = "Order by Date,Country"
QRCountryLine = SELECTCTLINE + FROMCTLINE + WHERE + GROUPBYCTLINE + ORDERBYCTLINE

#Query Country Tab
SELECTCTTAB = "SELECT Country,Sum(Impression) as Imp,Sum( Clicks) as Clicks,Round(Sum(Sum(Clicks)/Sum(Impression))*100,2) as CTR,Round(Sum(sum(Posimp)/Imp),2) as AvgPos,Round(Sum(Sum(Cost)/Sum(Clicks)),2) as CPC,Round(Sum(Cost),2) as Costs,Sum(AdWordsConversions) as ConvAdw,Sum(DFATransactions) as Sales,Sum(DFAActions) as Optin,Round(Sum(Sum(DFATransactions)/Sum(Clicks))*100,2) as CVRSales,Round(Sum(Sum(DFAActions)/Sum(Clicks))*100,2) as CVROptin,Round(Sum(Revenu),2) as CA,Round(Sum(Sum(Cost)/Sum(Revenu))*100,2) as TxDistri,Round(Sum(sum(Revenu)/sum(DFATransactions)),2) as AvgBasket "
FROMCTTAB = "from (Select Date, NTH(3,split(Campaign,\"_\")) as Country,Impression,Clicks,Posimp,Cost,AdWordsConversions,DFAActions,DFATransactions,Revenu FROM (Table_Query(elce_ds_reports_vf,'table_id contains \"left_join_report\"'))) "
GROUPBYCTTAB = "Group by Country "
ORDERBYCTTAB = "Order by Country"
QRCountryTab = SELECTCTTAB + FROMCTTAB + WHERE + GROUPBYCTTAB + ORDERBYCTTAB

mem = memcache.Client()

class MainPage(webapp2.RequestHandler):
    
    @staticmethod
    def to_float(value):
        if value is not None:
            return float(value)
        else:
            return None
        
    #------------------ Country-----------------------------    
    def _CountryTab(self, bqCountryTab):
        # get data from query
        logging.info(bqCountryTab)
        tabCountryTab = Table()
        Country = bqCountryTab["schema"]["fields"][0]["name"]
        Impression = bqCountryTab["schema"]["fields"][1]["name"]
        Clicks = bqCountryTab["schema"]["fields"][2]["name"]
        CTR = bqCountryTab["schema"]["fields"][3]["name"]
        AvgPos = bqCountryTab["schema"]["fields"][4]["name"]
        CPC = bqCountryTab["schema"]["fields"][5]["name"]
        Costs = bqCountryTab["schema"]["fields"][6]["name"]
        ConvAdw = bqCountryTab["schema"]["fields"][7]["name"]
        Sales = bqCountryTab["schema"]["fields"][8]["name"]
        Optin = bqCountryTab["schema"]["fields"][9]["name"]
        CVRSales = bqCountryTab["schema"]["fields"][10]["name"]
        CVROptin = bqCountryTab["schema"]["fields"][11]["name"]
        CA = bqCountryTab["schema"]["fields"][12]["name"]
        TxDistri = bqCountryTab["schema"]["fields"][13]["name"]
        AvgBasket = bqCountryTab["schema"]["fields"][14]["name"]
        
        #create tab and attribute column with data
        tabCountryTab.add_column(Country, unicode, Country) 
        tabCountryTab.add_column(Impression, float, Impression)
        tabCountryTab.add_column(Clicks, float, Clicks)
        tabCountryTab.add_column(CTR, float, CTR)
        tabCountryTab.add_column(AvgPos, float, AvgPos)
        tabCountryTab.add_column(CPC, float, CPC)
        tabCountryTab.add_column(Costs, float, Costs)
        tabCountryTab.add_column(ConvAdw, float, ConvAdw)
        tabCountryTab.add_column(Sales, float, Sales)
        tabCountryTab.add_column(Optin, float, Optin)
        tabCountryTab.add_column(CVRSales, float, CVRSales)
        tabCountryTab.add_column(CVROptin, float, CVROptin)
        tabCountryTab.add_column(CA, float, CA)
        tabCountryTab.add_column(TxDistri, float, TxDistri)
        tabCountryTab.add_column(AvgBasket, float, AvgBasket)
        
        #loop on all row to get data and shaped for chart
        for row in bqCountryTab["rows"]:            
            tabCountryTab.append([row["f"][0]["v"], MainPage.to_float(row["f"][1]["v"]), MainPage.to_float(row["f"][2]["v"]), MainPage.to_float(row["f"][3]["v"]), MainPage.to_float(row["f"][4]["v"]), MainPage.to_float(row["f"][5]["v"]), MainPage.to_float(row["f"][6]["v"]), MainPage.to_float(row["f"][7]["v"]), MainPage.to_float(row["f"][8]["v"]), MainPage.to_float(row["f"][9]["v"]), MainPage.to_float(row["f"][10]["v"]), MainPage.to_float(row["f"][11]["v"]), MainPage.to_float(row["f"][12]["v"]), MainPage.to_float(row["f"][13]["v"]), MainPage.to_float(row["f"][14]["v"])])
        logging.info("----End Data")
        logging.info(tabCountryTab)
        return encode(tabCountryTab)
    #-----------------End Country----------------------------------------
    
    @decorator.oauth_required
    def get(self):
        data = mem.get('Alldata')
        bq = bqclient.BigQueryClient(decorator)
        
        valCountryTab = self._CountryTab(bq.Query(QRCountryTab, BILLING_PROJECT_ID))
        
        data = ({'CountryTab': valCountryTab,'QrCountryTab' : QRCountryTab})
        mem.set('Alldata', data)
        template = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(render(template, data))

application = webapp2.WSGIApplication([
    ('/', MainPage),
    (decorator.callback_path, decorator.callback_handler())
], debug=True)
