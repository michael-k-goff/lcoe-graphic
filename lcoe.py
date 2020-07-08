# Build a boxplot showing levelized cost of electricity (LCOE) for several major types of electricity.

# Imports
import pandas as pd
import numpy as np
import matplotlib as mpl
mpl.use('agg')
import matplotlib.pyplot as plt
import matplotlib.image as image
from PIL import Image

# This file contains the LCOE data used for this plot.
# It is generated by a separate file (Energy Model/production_overview.py)
# Every type of power is classified by Category and Type.
# Category is more broad (e.g. Coal, Natural Gas, Nuclear, etc.)
# Type is more specific (Depreciated Coal, IGCC, Supercritical, Advanced Ultra-Supercritical are examples of types of coal)
# In some cases, the data source lacks specificity beyond the general category, in which case Category and Type are the same.
df_lcoe = pd.read_csv("lcoe.csv")

# Types of energy that are excluded from the plot
# In general, we are excluding analysis of the following types of electricity, which are beyond the scope of this particular plot:
# - Depreciated power (we only want to compare new builds)
# - Carbon capture and sequestration
# - Power sources that are not technologically or commercially mature
# - Distributed power sources
skipped_types = ["Depreciated Coal","20-30% CCS","90+% CCS","IGCC with CCS","Supercritical with CCS","Combustion Turbine","Gas Peaking","Natural Gas CCS","Diesel Generator","Biomass Microgrid","Incineration with CCS","Depreciated Nuclear","Advanced Nuclear","Small Modular Reactor","Generation IV","Sodium-Cooled Fast Reactor","High Temperature Reactor","Fusion","Refurbishments","Organic PV","Solar Updraft Tower","Space-Based Solar","Distributed Solar - Small","Distributed Solar - Large","Community Solar","High Altitude","Wind Microgrid","Enhanced Geothermal System","Hydrothermal Vents","Fuel Cell","Solid Oxide Fuel Cells","Molten Carbonate Fuel Cells"]
df_lcoe = df_lcoe[~df_lcoe["Type"].isin(skipped_types)]

# The categories for this plot are not identical to the categories in the CSV file.
# This object tells us how to map to the categories for the current plot, based on type.
# For types not listed, the category for this plot is the same as in the CSV file.
# The major changes are dividing Solar into Solar PV and Solar, Non-PV; Wind into Onshore Wind and Offshore Wind, and renaming Petroleum -> Oil and MHK -> Ocean
category_changes = {
    "Photovoltaics":"Solar PV",
    "Crystalline PV":"Solar PV",
    "Thin Film PV":"Solar PV",
    "Perovskite":"Solar PV",
    "Organic PV":"Solar PV",
    "PV Fixed":"Solar PV",
    "PV 1-Axis Tracking":"Solar PV",
    "PV 2-Axis Tracking":"Solar PV",
    "Solar Thermal":"Solar,\nNon-PV",
    "Solar Thermal without Storage":"Solar,\nNon-PV",
    "Solar Thermal with Storage":"Solar,\nNon-PV",
    "Concentrated PV":"Solar,\nNon-PV", # It's still a PV, but a highly nonstandard design
    "Onshore Wind":"Onshore\nWind",
    "Offshore Wind":"Offshore\nWind",
    "Deep Offshore":"Offshore\nWind",
    "Floating Offshore":"Offshore\nWind",
    "Offshore Vertical Axis":"Offshore\nWind",
    "MHK":"Ocean",
    "Tidal":"Ocean",
    "Wave":"Ocean",
    "OTEC":"Ocean",
    "Osmotic":"Ocean",
    "Oil Power Plant":"Oil"
}

# Rename categories, since the desired category names for this plot differ from what is in the CSV file
def rename_category(row):
    if row["Type"] in category_changes:
        return category_changes[row["Type"]]
    else:
        return row["Category"]
df_lcoe["Category"] = df_lcoe.apply(rename_category, axis=1)

# The list of unique categories, after the above changes are applied
lcoe_keys = df_lcoe["Category"].unique()

# Each study reports either a single LCOE estimate, a range of LCOE estimate (high and low), or both
# For the purposes of this plot, we want every study/type combination to have equal weight, so all three values will be imputed for each study.
# If a central LCOE value is not given, it is assumed to be the midpoint of the high and low values.
# If only a single LCOE estimate is given, the high and low values are assumed to be the same.
def interpolate_lcoe(row):
    if (row["LCOE"]>0):
        return row["LCOE"]
    return (row["LCOE Low"]+row["LCOE High"])/2
def interpolate_lcoe_low(row):
    if (row["LCOE Low"]>0):
        return row["LCOE Low"]
    return row["LCOE"]
def interpolate_lcoe_high(row):
    if (row["LCOE High"]>0):
        return row["LCOE High"]
    return row["LCOE"]
# Apply LCOE interpolations
df_lcoe["LCOE"] = df_lcoe.apply(interpolate_lcoe, axis=1)
df_lcoe["LCOE Low"] = df_lcoe.apply(interpolate_lcoe_low, axis=1)
df_lcoe["LCOE High"] = df_lcoe.apply(interpolate_lcoe_high, axis=1)

# For every category, all applicable LCOE estimates are presented in a single array.
def get_lcoe_by_category(category):
    df_cat = df_lcoe[df_lcoe["Category"]==category]
    lcoe_low = df_cat["LCOE Low"].to_numpy()
    lcoe = df_cat["LCOE"].to_numpy()
    lcoe_high = df_cat["LCOE High"].to_numpy()
    return np.concatenate((lcoe_low, lcoe, lcoe_high))
lcoe_values = [get_lcoe_by_category(lcoe_keys[i]) for i in range(len(lcoe_keys))]

# We are presenting data from lowest to highest average LCOE from top to bottom. Sort data by average LCOE.
keyed_lcoe_values = [[lcoe_keys[i], lcoe_values[i]] for i in range(len(lcoe_keys))]
keyed_lcoe_values = sorted(keyed_lcoe_values, key=lambda x:-sum(x[1]/len(x[1])))
lcoe_values = [keyed_lcoe_values[i][1] for i in range(len(keyed_lcoe_values))]
lcoe_keys = [keyed_lcoe_values[i][0] for i in range(len(keyed_lcoe_values))]

######################## Plot

# Create a figure instance
fig = plt.figure(1, figsize=(9, 8))

# Create an axes instance
ax = fig.add_subplot(111)

# Create the boxplot
gray_diamond = dict(marker='D',markerfacecolor="#00000077")
medianprops = dict(linestyle='-', linewidth=1, color='#000000')
meanpointprops = dict(marker='D', markeredgecolor='black',
                      markerfacecolor='#000000')
# Following are arbitrary values for the key, to illustrate the boxplot diagram for the unfamiliar viewer.
key_box_values = [26,27,28,29,30,31,32,33,34,35,36,37,38,39,47,48,79]
bp = ax.boxplot((lcoe_values+[key_box_values]), vert=False, showfliers=False, flierprops=gray_diamond, showmeans=True, medianprops=medianprops, meanprops = meanpointprops, positions=list(range(1,len(lcoe_values)+1))+[len(lcoe_values)-0.5])
for element in ['boxes', 'whiskers', 'fliers', 'means', 'medians', 'caps']:
    plt.setp(bp[element], color="#00000077")
    
# Plot visual modifications
plt.yticks(range(1,len(lcoe_values)+1),lcoe_keys)
plt.xlim(0,50.5)
plt.ylim(0.001,len(lcoe_keys)+0.5)
# Since most LCOE estimates are below 10 cents/kWh, additional ticks are added to differentiate smaller values
# There are a few estimates above 100 cents/kWh, but for visual clarity those about 50 c/kWh are truncated.
plt.xticks([2,4,6,8,10,20,30,40,50],["2","4","6","8","10","20 \xa2/kWh","30 \xa2/kWh","40 \xa2/kWh","50 \xa2/kWh"],ha="right")
ax.xaxis.set_ticks_position('none')
ax.yaxis.set_ticks_position('none')
for spine in plt.gca().spines.values():
    spine.set_visible(False)
for i in range(4):
    ax.axvline(x=2+2*i, linewidth=0.7, color="#00000022")
ax.axvline(x=10, linewidth=0.7, color="#00000022")
ax.axvline(x=20, linewidth=0.7, color="#00000022")
ax.axvline(x=30, linewidth=0.7, color="#00000022",ymax=0.75)
ax.axvline(x=40, linewidth=0.7, color="#00000022",ymax=0.75)
ax.axvline(x=50, linewidth=0.7, color="#00000022",ymax=0.75)
plt.title("Levelized Cost of Electricity by Source",fontsize=25,fontweight="bold",x=0.44)
    
# Show all LCOE estimates.
# This is a nonstandard technique for boxplots and is done at the request of the client.
for i in range(len(lcoe_values)):
    for j in range(len(lcoe_values[i])):
        ax.plot(lcoe_values[i][j], i+1,marker="o",color="#00000044",markersize=4)
    mean_value = sum(lcoe_values[i])/len(lcoe_values[i])
    ax.annotate(str(round(mean_value, 1))+u'\xa2' + "/kWh", xy=(mean_value,i), xytext=(mean_value-1, i+0.45),fontsize=11)
ax.annotate("Ocean energy outliers\nexceeding 50\xa2/kWh not shown",xy=(50,0),xytext=(49,0.3),ha="right",fontsize=8)

# Annotate the key in the upper right
ax.annotate("Mean",xy=(40,11),xytext=(36,11),size=8)
ax.annotate("Median",xy=(40,11),xytext=(32.5,11),size=8)
ax.annotate("25th\nPercentile",xy=(40,11),xytext=(28,11.9),size=8)
ax.annotate("75th\nPercentile",xy=(40,11),xytext=(37,11.9),size=8)
ax.annotate("25th\nPercentile\nminus 1.5X\nInterquartile\nRange",xy=(40,11),xytext=(25,10.1),size=8)
ax.annotate("75th\nPercentile\nplus 1.5X\nInterquartile\nRange",xy=(40,11),xytext=(45,10.1),size=8)

# Add the Urban Cruise Ship logo and a caption
logo = image.imread("logo.png")
logoPIL = Image.open("logo.png")
logoPIL = logoPIL.resize((int(logoPIL.size[0]/9),int(logoPIL.size[1]/9)),Image.ANTIALIAS)
logo[:, :, -1] = 0.5  # set the alpha channel
fig.figimage(logoPIL, 655, 68, zorder=3)
plt.text(0.80,-0.140,'urbancruiseship.org\ninfo@urbancruiseship.org\nrev. July 7, 2020 by\nLee Nelson and\nMichael Goff', ha='left', va='top', transform=ax.transAxes,fontsize=7)
# Caption
# Line breaks are added manually.
caption_message = "Levelized cost of electricity from major sources. LCOE is defined as the price that a\npower plant needs to receive for electricity over its lifetime to be profitable. While\ninformative, the LCOE metric does not include several important costs of producing\nelectricity, such as transmission infrastructure and environmental impacts."
plt.text(-0.1,-0.13,caption_message,ha='left',va='top',transform=ax.transAxes,fontsize=10,wrap=True)

# Save the figure in SVG (scalable vector graphics) format.
fig.savefig('lcoe.svg', bbox_inches='tight')