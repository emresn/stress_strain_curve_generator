import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
from scipy import stats
from datetime import datetime


rawdata = []
with open ("test_data.txt", "r") as file:
    for i in file:
        rawdata.append(i.replace("\n","").replace(",",".").split("\t"))

rawDf = pd.DataFrame(data=rawdata)


if int(len(rawDf.columns)) > 4:
    print("There are {} tests in test_data.txt.".format(int(len(rawDf.columns)/4)))
    t = int(input("Please select test number: "))    
    df = rawDf[[4*t-4,4*t-3,4*t-2,4*t-1]]
    df.columns = ["Time [sec]","Force [N]","Elongation [mm]","Ext.1 [mm]"]
    df.drop(index=[0,1,2], inplace=True)
    df.reset_index(drop=True, inplace=True)
    try:
        df.replace(r'',np.nan, regex = True, inplace = True)
        df.dropna(inplace = True)
    except:
        pass
    df.index.names = ["{}".format(rawDf[t*4-4].loc[0])]
else: 
    df = rawDf[[0,1,2,3]]
    df.columns = ["Time [sec]","Force [N]","Elongation [mm]","Ext.1 [mm]"]
    df.drop(index=[0,1,2], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df.index.names = ["{}".format(rawDf[0].loc[0])]

print(df)
testName = rawDf[0].loc[0]
materialName = input("Material Name: ")
geometry = input("\nPlease select the section geometry\n1: Rectangle\n2: Circle\n3: Enter specific section area\nYour choice: ")

if geometry == "1":
    rect_t = input("Thickness [mm]: ")
    rect_w = input("Width [mm]: ")
    section = float(rect_t)*float(rect_w)
elif geometry == "2":
    diameter = input("Diameter [mm]: ")
    section = (3.14 * (float(diameter))**2) / 4
elif geometry == "3":
    section = float(input("Section Area [mm²]: "))
else:
    print("Wrong choice. Please select any option again.")

l0= input("Gauge length (GL) [mm]: ")


def stressCalc(force):
    sigma = float(force) / float(section)
    return sigma

def strainCalc(deltal):
    epsilon = float(deltal) / float(l0)
    return epsilon

def remove_lastbaddatas(dataframe):
    removed_points_list= []
    for i in range(int(3*len(dataframe.index)/4),(len(dataframe.index)-1)):
        b = float(dataframe["Force [N]"].loc[i])
        a = float(dataframe["Force [N]"].loc[i-1])
        if a-b > 50:
            removed_points_list.append(i)
    if removed_points_list != []:
        dataframeNew = df.drop(index=(range(removed_points_list[0],len(df.index-1))))
        df.reset_index(drop=True, inplace=True)
    return dataframeNew

df = remove_lastbaddatas(df)
dfStress = df["Force [N]"].apply(stressCalc)
df.insert(4,"Stress [MPa]",dfStress,True)

dfStrain = df["Ext.1 [mm]"].apply(strainCalc)
df.insert(5,"Strain [mm/mm]",dfStrain,True)


fig1 = plt.figure()
axes_1 = fig1.add_axes([0.15,0.15,0.75,0.75])
axes_1.plot(df["Strain [mm/mm]"],df["Stress [MPa]"], color = "black")
axes_1.set_title("{} - Engineering Curve".format(materialName))
axes_1.set_xlabel("Strain ε [mm/mm]")
axes_1.set_ylabel("Stress σ [MPa]")
plt.savefig('1_engineering_stress_strain.png', dpi=300)
print("1_engineering_stress_strain.png file have been saved.")


# true stress straşn 
def trueStressCalc(stress,strain):
    stress_lst = []
    strain_lst = []
    truestress_lst = []
    for key, value in stress.iteritems():
        key
        stress_lst.append(value)
    for key, value in strain.iteritems():
        strain_lst.append(value)
    for s,e in zip(stress_lst,strain_lst):
        truestress_lst.append(float(s) * (1 + float(e)))
    return truestress_lst

def trueStrainCalc(strain):
    tstrain = math.log( float(1) + float(strain)) 
    return tstrain

dfTrueStress = trueStressCalc(df["Stress [MPa]"], df["Strain [mm/mm]"])
df.insert(6,"True Stress [MPa]",dfTrueStress,True)

dfTrueStrain = df["Strain [mm/mm]"].apply(trueStrainCalc)
df.insert(7,"True Strain [mm/mm]",dfTrueStrain,True)


fig2 = plt.figure()
axes_2 = fig2.add_axes([0.15,0.15,0.75,0.75])
axes_2.plot(df["True Strain [mm/mm]"],df["True Stress [MPa]"], color="red")
axes_2.set_title("{} - True Curve".format(materialName))
axes_2.set_xlabel("True Strain ε [mm/mm]")
axes_2.set_ylabel("True Stress σ [MPa]")
plt.savefig('2_true_stress_strain.png', dpi=300)
print("2_true_stress_strain.png file have been saved.")


fig3 = plt.figure()
axes_3 = fig3.add_axes([0.15,0.15,0.75,0.75])
axes_3.plot(df["True Strain [mm/mm]"],df["True Stress [MPa]"], color = "red", label= "True Curve")
axes_3.plot(df["Strain [mm/mm]"],df["Stress [MPa]"], color = "black", label = "Engineering Curve")
axes_3.set_title("{} - Engineering Curve & True Curve".format(materialName))
axes_3.set_xlabel("Strain ε [mm/mm]")
axes_3.set_ylabel("Stress σ [MPa]")
axes_3.legend()
plt.savefig('3_eng_true_stress_strain.png', dpi=300)
print("3_eng_true_stress_strain.png file have been saved.")


def makeReport():
    df.to_excel("test_data.xls")
    print("test_data.xls has been generated.")
    with open ("temp.html", "r", encoding="utf-8") as file_temp:
        html_content = file_temp.read() 
    excel_link = '<a href="test_data.xls" target="blank"> test_data.xls </a>' 
    if geometry == "1":
        htmlMatGeo = '''
         <tr>
            <td style="width: 200px;"><span style="color: #000000;"><strong>Thickness :</strong></span></td>
            <td style="width: 268.833px;"><span style="color: #000000;">{} mm</span></td>
        </tr>
        <tr>
            <td style="width: 200px;"><span style="color: #000000;"><strong>Width :</strong></span></td>
            <td style="width: 268.833px;"><span style="color: #000000;">{} mm</span></td>
        </tr>
        '''.format(rect_t,rect_w)
    elif geometry == "2":
        htmlMatGeo = '''
        <tr>
            <td style="width: 200px;"><span style="color: #000000;"><strong>Diameter :</strong></span></td>
            <td style="width: 268.833px;"><span style="color: #000000;">{} mm</span></td>
        </tr>
        '''.format(diameter)
    else:
        htmlMatGeo = ""

    with open ("test_report.html", "w", encoding="utf-8") as file:
        file.write(html_content.format(
                datetime.ctime(datetime.now()), materialName, t, htmlMatGeo, section,l0, excel_link))
        print("\nReport file 'test_report.html' has been generated.")

makeReport()
plt.show()

