# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from itertools import product
from scipy.optimize import linprog

def downscale_demands( target, initial, income_i, income_f, gdp_f, names ):
    """
    Aim is to minimize the maximum difference between the percent change 
    in per capits GDP and energy intensity (per unit GDP).
    
    This is the LP problem:
    
    Min:  alpha
    s.t.  alpha >= | phi_c - delta_c | forall c
          sum_c(beta_c*delta_c) = target - sum_c(beta_c)
          alpha >= 0
    
    # don't allow 0 intensities in future time steps
    ei = initial / income_i
    ei[np.where(ei==0)] =  min(ei[ei.nonzero()])
    initial = ei * income_i
    """
    
    # the above simplifying parameters defined as:
    beta = income_f * initial / income_i
    phi = income_f / income_i - 1
    
    # x = [alpha, delta_1, delta_2, ...., delta_n]    
    # LP objective function coefficients for minimizing maximum difference in growth rates
    cobj = [1]
    cobj.extend([0]*len(names))
    cobj = np.array(cobj)

    # maxmin abs value constraint upper bound 1
    a = np.array([-1]*len(names))
    a.shape=(len(names),1)
    b = np.identity(len(names))
    Aub1 = np.concatenate((a,b),axis=1)
    bub1 = phi
    bub1.shape = (len(names),1)
    
    # maxmin abs value constraint upper bound 2
    a = np.array([-1]*len(names))
    a.shape=(len(names),1)
    b = np.identity(len(names))
    b *= -1
    Aub2 = np.concatenate((a,b),axis=1)
    bub2 = -1*phi
    bub2.shape = (len(names),1)
    
    # non negativity for absolute value
    Aub3 = np.array([-1])
    Aub3 = np.append(Aub3,[0]*len(names))
    Aub3.shape = (1,(len(names)+1))
    bub3 = np.array([[0]])
    Aub = np.concatenate((Aub1,Aub2,Aub3),axis=0)
    bub = np.concatenate((bub1,bub2,bub3),axis=0)

    # Equality constraint for ensuring the country balances match the regional target
    Aeq = np.array(np.append([0],beta))
    Aeq.shape = (1,(1+len(names)))
    beq = np.array([[target-sum(beta)]])
    beq.shape = (1,1)

    # Call LP solver
    res = linprog(
        c = cobj,
        A_ub=Aub,
        b_ub=bub,
        A_eq=Aeq,
        b_eq=beq,
        bounds=(-np.inf, np.inf),
        options={"disp":True,"tol":3.6e-10})
        
    # Return data frame with updated parameters
    val = []
    for i in range(1,(len(names)+1)):
        val.append(income_f[i-1]*(initial[i-1]/income_i[i-1])*(1+res.x[i]))
    
    df = pd.DataFrame({'node':names,'value':val})
    return df