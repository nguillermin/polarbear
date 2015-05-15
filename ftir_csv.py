#!/usr/bin/python

# FTIR data munging script

import sys, os, re
from pandas import read_csv, DataFrame, concat

for d in sys.argv[1:]:
    top = os.path.basename(d)
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
            match = re.search(r'Sen\s*=\s*([0-9]*)\s*([nNuU]A*)',f)
            if match:
                m = match.groups()
                units = {'nA':1,'uA':1000,'N':1,'U':1000}
                sens = int(m[0]) * units[m[1]]
            else:
                print 'ERROR:', f

            bias = re.search(r'Bias\s*=\s*(-*[0-9]*\.*[0-9]*)\s*V',f)
            if bias:
                bias = float(bias.group(1))
            else:
                print f
            # I guess this is why people don't like using regexes...
            headers = headers.append(DataFrame([[bias,sens]],columns=headers.columns),
                                     ignore_index=True)

        dfs = [read_csv(os.path.join(d,pf),
                        '\t',header=None) for pf in pfiles]
        for i, df in enumerate(dfs):
            df[1] = df[1]*headers['Sensitivity'].iloc[i]   
        
        headers = headers.sort(columns='Bias')

        dfs = concat([dfs[i] for i in headers.index],axis=1)
        
        headers = headers.transpose()
        empty = ['' for x in range(len(headers.columns))]
        hc = headers.columns
        newcols = [x for t in zip(*[empty,hc]) for x in t]
        headers = headers.reindex(columns=newcols)
        
        out = os.path.join(prev_dir,'_'.join([top,p+'.csv']))
        headers.to_csv(out,mode='w',header=None,na_rep='')
        dfs.to_csv(out,mode='a',header=None,na_rep='')
