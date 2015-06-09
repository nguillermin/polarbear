#!/usr/bin/python

# FTIR data munging script

import sys, os, re
from pandas import read_csv, DataFrame, concat
import xlsxwriter

for d in sys.argv[1:]:
    toplevelname = os.path.basename(d)
    prev_dir = os.path.dirname(d)
    filelist = [f for f in os.listdir(d) if f[-4:].upper()=='.DPT']

    ports = set([re.search(r'Port\s*[0-9]',f).group() for f in filelist])

    if not ports:
        print "No FTIR data found."

    for p in ports:
        pfiles = [f for f in filelist if re.search(p,f)]
        headers = concat([DataFrame(columns=['Bias'],dtype='float'),
                          DataFrame(columns=['Sensitivity'],dtype='int')])
        for f in pfiles:
            match = re.search(r'(?:Sen|Sens)\s*=\s*([0-9]*)\s*([nNuU][aA]*)',f)
            if match:
                m = match.groups()
                units = {'n':1,'u':1000}
                sens = int(m[0]) * units[m[1][0]] # First character of units
                # only in order to match both 'n' and 'nA'
                
            else:
                print "Sensitivity not found in filename ", f

            bias = re.search(r'(?:Bias|V)\s*=\s*(-*[0-9]*\.*[0-9]*)\s*V',f)
            if bias:
                bias = float(bias.group(1))
            else:
                print "Bias not found in filename ", f
            # I guess this is why people don't like using regexes...
            headers = headers.append(DataFrame([[bias,sens]],columns=headers.columns),
                                     ignore_index=True)

        dfs = [read_csv(os.path.join(toplevelname,pf),
                        sep=',',dtype='float',header=None) for pf in pfiles]
        for i, df in enumerate(dfs):
            df[1] = df[1]*headers['Sensitivity'].iloc[i]
            
        headers = headers.sort(columns='Bias')
        
        data = concat([dfs[i] for i in headers.index],axis=1)

        outxls = os.path.join(os.path.dirname(toplevelname),p+'.xlsx')
        
        workbook = xlsxwriter.Workbook(outxls)
        worksheet = workbook.add_worksheet('Sheet1')
        
        worksheet.write(0, 0, 'Bias')
        worksheet.write(1, 0, 'Sensitivity')

        chart = workbook.add_chart({'type': 'scatter'})
        for i, h in enumerate(headers.index):
            worksheet.write_number(0, 2*i+2, headers['Bias'][h])
            worksheet.write_number(1, 2*i+2, headers['Sensitivity'][h])
            for r, row in dfs[h].iterrows():
                for c, col in enumerate(row):
                    worksheet.write_number(r+2, 2*i+c+1, row[c])
        
            l = len(dfs[h])
            chart.add_series({
                    'name': str(headers['Bias'][h]),
                    'categories': ['Sheet1', 2, 2*i+1, l+1, 2*i+1],
                    'values': ['Sheet1', 2, 2*i+2, l+1, 2*i+2],
                })
        # Set style smooth line no markers
        chart.set_style(11)
        worksheet.insert_chart('B3', chart)
            
        workbook.close()
