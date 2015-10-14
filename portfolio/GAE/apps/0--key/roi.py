import os
import wsgiref.handlers
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app


def doRender(handler, tname='index.htm', values={}):
    temp = os.path.join(os.path.dirname(__file__), 'templates/' + tname)
    if not os.path.isfile(temp):
        return False

    # Make a copy of the dictionary and add the path
    newval = dict(values)
    newval['path'] = handler.request.path
    outstr = template.render(temp, newval)
    handler.response.out.write(outstr)
    return True


class MainPage(webapp.RequestHandler):
    def get(self):
        NuNu = self.request.get("nurses")
        TurnO = self.request.get("turnover")
        l1 = []
        if NuNu and TurnO:
            NN = int(NuNu)
            To = float(TurnO)
            Topr = str(To) + "%" 
            l1 = [{"# Nurses":[NN, NN, NN, NN]}]
            l1.append({"Turnover Rate":[Topr, Topr, Topr, Topr]})
            Vac = int(round(NN*To/100)); NuV = [Vac, Vac, Vac, Vac]
            sigma = [Vac, Vac, Vac, Vac]
            l1.append({"# Vacancies":NuV})
            l1.append({"Selection Effectivenes":["50%", "63%", "69%", "77%"]})
            j = Vac
            k = [0, 1, 1, 1]
            counter = 0
            while j  > 1:
                numbers = ["one", "two", "three", "four", "five", \
                           "six", "seven", "eight", "nine", "ten", \
                           "eleven", "twelve"]
                counter = counter+1 # iteration counter                
                row_name_1 = "Round "+ str(counter) + " Hired"
                row_name_2 = "Round " + str(counter) + " Kept"
                l1.append({row_name_1:NuV})
                NuV_1 = [int(round(NuV[0]/2)), int(round(NuV[1]*0.63)), \
                         int(round(NuV[2]*0.69)), int(round(NuV[3]*0.77))]
                l1.append({row_name_2:NuV_1})
                # lets change the initial array:
                NuV = [(NuV[0]-NuV_1[0]), (NuV[1]-NuV_1[1]), \
                       (NuV[2]-NuV_1[2]), (NuV[3]-NuV_1[3]), ]
                #logging.info("It's works!")
                for q in range(4):
                    sigma[(q-1)] = sigma[(q-1)] + NuV[(q-1)]
                    # lets counting iteration:
                    if NuV[(q-1)] > 0:
                        k[(q-1)] = k[(q-1)] + 1
                        #logging.info = "It's works!"
                l1.append({"<br /> ":["", "", "", ""]})
                j = round(j/2)
            l1.append({"Total Number of Hires":sigma})
            l1.append({"Number of Rounds of Hires (Recruitments)":k})
            HiSaved = [0, (sigma[0]-sigma[1]), (sigma[0]-sigma[2]), (sigma[0]-sigma[3])]
            l1.append({"Hires Saved Over Invalid Test":HiSaved})
            hiEff = []; costSavings25 = []; costSavings35 = [];
            costSavings45 = []; costSavings65 = []
            for s in HiSaved:
                he = str(int(round(100*s/sigma[0]))) + "%"
                hiEff.append(he)
                costSavings25.append(s*25000)
                costSavings35.append(s*35000)
                costSavings45.append(s*45000)
                costSavings65.append(s*65000)
            l1.append({"% Hiring Efficiency Over Invalid Test":hiEff})
            l1.append({"<br /> ":["", "", "", ""]})
            l1.append({"Cost Savings at:":["", "", "", ""]})
            l1.append({"<br /> ":["", "", "", ""]})
            l1.append({"$25K per hire":costSavings25})
            l1.append({"$35K per hire":costSavings35})
            l1.append({"$45K per hire":costSavings45})
            l1.append({"$65K per hire":costSavings65})
            l1.append({"<br /> ":["", "", "", ""]})
            test_administred = [int(round(sigma[1]/0.5)), int(round(sigma[2]/0.3)), int(sigma[3]/0.1)]
            cost_per_test = []
            for nt in test_administred:
                if nt > 1 and nt < 51: price = 186
                elif nt >= 51 and nt < 101: price = 178
                elif nt >= 101 and nt < 201: price = 168
                elif nt >= 201 and nt < 301: price = 162
                elif nt >= 301 and nt < 401: price = 156
                elif nt >= 401 and nt < 501: price = 151
                elif nt >= 501 and nt < 751: price = 144
                elif nt >= 751 and nt < 1001: price = 138
                elif nt >= 1001 and nt < 1501: price = 132
                elif nt >= 1501 and nt < 2001: price = 126
                elif nt >= 2001 and nt < 2501: price = 120
                elif nt >= 2501 and nt < 3501: price = 114
                elif nt >= 3501 and nt < 5001: price = 108
                elif nt >= 5001 and nt < 7501: price = 102
                elif nt >= 7501 and nt < 10001: price = 96
                elif nt >= 10001 : price = 94
                cost_per_test.append(price)
            total_test_administred = ["",]
            total_cost_per_test = ["",]
            total_test_administred.extend(test_administred)
            total_cost_per_test.extend(cost_per_test)
            l1.append({"Cost per Test Credit":total_cost_per_test})
            l1.append({"Total # of Test Credits Administered":total_test_administred})
            l1.append({"<br /> ":["", "", "", ""]})
            # E50 * E51
            tctc = [0, 0, 0]
            for aq in range(3):
                tctc[aq-1] = (cost_per_test[aq-1]*test_administred[aq-1])
            total_tctc = ["",]
            total_tctc.extend(tctc)
            l1.append({"Total Cost of Test Credits":total_tctc})
            l1.append({"<br /> ":["", "", "", ""]})
            # E45 - E53
            savings25 = list(costSavings25)
            del savings25[0]
            ns25 = [0, 0, 0]
            for bq in range(3):
                ns25[bq-1] = (savings25[bq-1]-tctc[bq-1])
            total_ns25 = ["",]
            total_ns25.extend(ns25)
            l1.append({"Net Savings at $25K per Hire":total_ns25})
            savings65 = list(costSavings65)
            del savings65[0]
            ns65 = [0, 0, 0]
            for bq in range(3):
                ns65[bq-1] = (savings65[bq-1]-tctc[bq-1])
            total_ns65 = ["",]
            total_ns65.extend(ns65)
            l1.append({"Net Savings at $65K per Hire":total_ns65})
        savings_at = ["25k", "35k", "45k", "65k"]
        row_names = ["# Nurses", "Turnover Rate", "# Vacancies", "Selection Effectiveness", "Total Number of Hires", "Number of Rounds of Hires (Recruitments)", "Hires Saved Over Invalid Test", "% Hiring Efficiency Over Invalid Test", "Cost Savings at:", "Cost per Test Credit", "Total # of Test Credits Administered", "Total Cost of Test Credits"]
        template_values = {'row_names':row_names, 'savings_at':savings_at, 'l1':l1}
        doRender(self,'roi.htm',template_values)

class Calculator(webapp.RequestHandler):
    def get(self):
        self.redirect("/roi/")
        

application = webapp.WSGIApplication([('/.*', MainPage), ('/roi/calculate', Calculator)], debug=True)

def main():
  run_wsgi_app(application)

if __name__ == '__main__':
  main()
