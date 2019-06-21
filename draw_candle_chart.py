# -*- coding: utf-8 -*-
"""
Created on Tue May 21 19:10:43 2019

@author: JAE
"""
import numpy as np

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
fig = plt.figure(figsize=(8, 5))
fig.set_facecolor('w')
gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
axes = []
axes.append(plt.subplot(gs[0]))
axes.append(plt.subplot(gs[1], sharex=axes[0]))
axes[0].get_xaxis().set_visible(False)


from mpl_finance import candlestick_ohlc

x = np.arange(len(df.index))
ohlc = df[['open', 'high', 'low', 'close']].astype(int).values
dohlc = np.hstack((np.reshape(x, (-1, 1)), ohlc))

# 봉차트
candlestick_ohlc(axes[0], dohlc, width=0.5, colorup='r', colordown='b')

# 거래량 차트
axes[1].bar(x, df.volume, color='k', width=0.6, align='center')

plt.tight_layout()
plt.show()


import datetime
_xticks = []
_xlabels = []
_wd_prev = 0
for _x, d in zip(x, df.date.values):
    weekday = datetime.datetime.strptime(str(d), '%Y%m%d').weekday()
    if weekday <= _wd_prev:
        _xticks.append(_x)
        _xlabels.append(datetime.datetime.strptime(str(d), '%Y%m%d').strftime('%m/%d'))
    _wd_prev = weekday
axes[1].set_xticks(_xticks)
axes[1].set_xticklabels(_xlabels, rotation=45, minor=False)



#%%
def fig2data ( fig ):
    """
    @brief Convert a Matplotlib figure to a 4D numpy array with RGBA channels and return it
    @param fig a matplotlib figure
    @return a numpy 3D array of RGBA values
    """
    # draw the renderer
    fig.canvas.draw ( )
 
    # Get the RGBA buffer from the figure
    w,h = fig.canvas.get_width_height()
    buf = np.fromstring ( fig.canvas.tostring_argb(), dtype=np.uint8 )
    buf.shape = ( w, h,4 )
 
    # canvas.tostring_argb give pixmap in ARGB mode. Roll the ALPHA channel to have it in RGBA mode
    buf = np.roll ( buf, 3, axis = 2 )
    return buf

