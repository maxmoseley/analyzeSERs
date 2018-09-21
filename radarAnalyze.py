'''
Created on Aug 28, 2018

@author: Maxwell.Moseley
'''

from itertools import combinations
import pandas as pd
import statsmodels.api as sm
import numpy as np
from time import strftime
import os

if __name__ == '__main__':
    
    RadarFile = "Data/2018-09-20 Radar SERs Data.xlsx"
    ResultsFile = "Results/%s-%s-%s Radar SERs Analysis %s%s.xlsx" % (strftime("%Y"),strftime("%m"),strftime("%d"),strftime("%H"),strftime("%M"))
    writer = pd.ExcelWriter(ResultsFile, engine='openpyxl')
    ResultsDF = pd.DataFrame()
    
    RadarDurs = pd.read_excel(RadarFile,sheet_name="Durations",index_col=0)
    RadarParams = pd.read_excel(RadarFile,sheet_name="Technical Parameters",index_col=0)
    RadarQuals = pd.read_excel(RadarFile,sheet_name="Other",index_col=0)
    
    for col in RadarDurs.columns:
        RadarDurs["ln_(%s)"%col] = np.log(RadarDurs[col]).replace([np.inf, -np.inf],np.nan)
        #RadarDurs["e^(%s)"%col] = np.exp(RadarDurs[col]).replace([np.inf, -np.inf],np.nan)

    for col in RadarParams.columns:
        RadarParams["ln_(%s)"%col] = np.log(RadarParams[col]).replace([np.inf, -np.inf],np.nan)
        RadarParams["e^(%s)"%col] = np.exp(RadarParams[col]).replace([np.inf, -np.inf],np.nan)

    '''
        RadarParams["(%s)^2"%col] = (RadarParams[col]**2).replace([np.inf, -np.inf],np.nan)
        RadarParams["sqrt(%s)"%col] = np.sqrt(RadarParams[col]).replace([np.inf, -np.inf],np.nan)
    '''
        
    airborne_index = (RadarQuals['Platform Category'] == 'Airborne')
    #Find some way to loop through the filter and change the sheet name
        
    skipCases = 0
    testCases = 0
    
    numPoints = 7
    numVars = 3
    
    while numVars >= 1:
        for i in RadarDurs.columns:
            for param in list(combinations(RadarParams.columns,numVars)):
                param = np.asarray(param)
                testSet = pd.concat([RadarDurs[i],RadarParams[param]], axis=1)
                testSet = testSet.replace([np.inf, -np.inf],np.nan)
                testSet = testSet.dropna(axis='rows',how='any')
                if not testSet.empty:
                    if len(testSet.index) >= numPoints:
                        y = RadarDurs[i]
                        x = RadarParams[param]
                        x = sm.add_constant(x)
                        model = sm.OLS(y,x,missing='drop')
                        results = model.fit()
                        paramCoeff = { str(key):value for key,value in results.params.to_dict().items() }
                        paramPvals = { str(key):value for key,value in results.pvalues.to_dict().items() }
                        paramTvals = { str(key):value for key,value in results.tvalues.to_dict().items() }
                        paramStdErr = { str(key):value for key,value in results.bse.to_dict().items() }
                        yDur = model.data.ynames
                        xParams = [str(m) for m in model.data.xnames]
                        
                        ResultVals = {
                            "Number of X Variables": numVars,
                            "Count of Usable Radars": results.nobs,
                            "Duration": yDur,
                            "Parameters": xParams,
                            "R-Squared": results.rsquared,
                            "Adj R-Squared": results.rsquared_adj,
                            "F Test": results.fvalue,
                            "Prob(F Test)": results.f_pvalue,
                            "Model Degrees of Freedom": results.df_model,
                            "Residual Degrees of Freedom": results.df_resid,
                            "Parameter Coefficients": paramCoeff,
                            "Parameter p-values": paramPvals,
                            "Parameter t-values": paramTvals,
                            "Parameter Std Err": paramStdErr,
                            "Model MSE": results.mse_model,
                            "Residual MSE": results.mse_resid,
                            "Total MSE": results.mse_total,
                            "Model Type": results.model.__class__.__name__,
                            "Sum of Squared Residuals": results.ssr,
                            "Scale": results.scale,
                            "AIC": results.aic,
                            "BIC": results.bic,
                            "Centered TSS": results.centered_tss,
                            "Uncentered TSS": results.uncentered_tss,
                            "Explained Sum of Squares": results.ess
                            }
                        
                        ResultsDF = ResultsDF.append(ResultVals, ignore_index=True)
                        
                        if not os.path.isfile(ResultsFile):
                            ResultsDF.tail(1).to_excel(writer, header=ResultsDF.columns, index=False, sheet_name='Results')
                        else:
                            ResultsDF.tail(1).to_excel(writer, startrow=len(ResultsDF), header=False, index=False, sheet_name='Results')
                        
                        writer.save()
                        
                        testCases = testCases + 1
                    
                    else:
                        skipCases = skipCases + 1
                
                else:
                    skipCases = skipCases + 1
                
                print "Tested: %s, Skipped: %s" % (testCases,skipCases)
        
        numVars = numVars - 1
           
    print "Done! :)"   
    pass