from windowing.make_windows.utils import flag
import numpy as np
import sys
sys.path.insert(0, '/home/ghisalberti/Documents/PycharmProjects/space/')
from space.models import planetary as smp


def regions(df):
    df.loc[:, 'isMSP'] = (df.regions_pred.values == 0)
    df.loc[:, 'isMSH'] = (df.regions_pred.values == 1)
    df.loc[:, 'isSW'] = (df.regions_pred.values == 2)


def flag_msp_and_msh(df, win_length):
    flag(df, win_length, {"name": "encountersMSPandMSH", "fun": any, "features": ['isMSP', 'isMSH'],
                          "merger": lambda x: np.all(x, axis=1)})


def mp_r(df, model):
    """
    Returns the radius of Shue MP in the satellite direction (theta,phi)
    Precondition : df must have theta, phi, Pd, Bz features
    """
    filled_df = df.fillna(value={'Pd': 2.056, 'Bz': -0.001})
    pressure = filled_df.Pd.values
    bz = filled_df.Bz.values
    msh = smp.Magnetosheath(magnetopause=model, bow_shock='bs_jelinek2012')
    r_mp = msh.magnetopause(df.theta.values, df.phi.values, Pd=pressure, Bz=bz, coord_sys='spherical')[0]
    df.loc[:, 'r_mp'] = r_mp


def shue_mp(df):
    mp_r(df, 'mp_shue1998')


def beyond_sup_limit(df, dl):
    df.loc[:, 'beyond_sup_limit'] = df.R.values > (df.r_mp.values + dl)


def below_inf_limit(df, dl):
    df.loc[:, 'below_inf_limit'] = df.R.values < (df.r_mp.values - dl)


def is_around_mp(df):
    df.loc[:, 'is_around_mp'] = np.logical_and(np.logical_not(df['beyond_sup_limit'].values),
                                               np.logical_not(df['below_inf_limit'].values))


def flag_around_mp(df, win_length):
    flag(df, win_length, {"fun": lambda x: np.logical_not(any(x)), "name": "isCloseToMP",
                          "features": ["is_around_mp"]})
