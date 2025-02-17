import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import rice, rayleigh, weibull_min
import os
import pandas as pd

base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "实验室水面实验", "时序")


def read_data(file_name):
    data = pd.read_excel(os.path.join(base_path, file_name), header=None)
    return data


def read_all_data():
    data_dict = {}
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if file.endswith(".xlsx"):
                file_path = os.path.join(root, file)
                file_name = file.split(".")[0].split("_")[-1]
                file_degree = file_name.split("度")[0]
                file_freq = file_name.split("度")[1][:3]
                file_wave = file_name.split("度")[1][3:]
                if file_degree not in data_dict:
                    data_dict[file_degree] = {}
                if file_freq not in data_dict[file_degree]:
                    data_dict[file_degree][file_freq] = {}
                data = read_data(file_path)
                data_dict[file_degree][file_freq][file_wave] = data

    return data_dict


def cut_data(data_dict, start=0, length=None):
    data = data_dict
    if length is None:
        return data[4][start:].reset_index(drop=True)
    return data[4][start:start + length].reset_index(drop=True)


def cdf_rice(data_list, save_path=None, title=None, noice_level=None):
    data1, data2, data3 = data_list
    rmax1 = min(len(data1), len(data2), len(data3)) - 1

    Power11 = []
    Power12 = []
    Power13 = []
    data11_linear = []
    data12_linear = []
    data13_linear = []

    for ii in range(rmax1):
        Power11_val = (data1[ii + 1] + noice_level) / 2
        Power12_val = (data2[ii + 1] + noice_level) / 2
        Power13_val = (data3[ii + 1] + noice_level) / 2

        Power11.append(Power11_val)
        Power12.append(Power12_val)
        Power13.append(Power13_val)

        data11_linear.append(10 ** (Power11_val / 10))
        data12_linear.append(10 ** (Power12_val / 10))
        data13_linear.append(10 ** (Power13_val / 10))

    power11 = np.array(data11_linear)
    power12 = np.array(data12_linear)
    power13 = np.array(data13_linear)

    x_values1 = np.linspace(min(power11), max(power11), 200)
    rice_params1 = rice.fit(power11, floc=0)
    shape_param1, _, _ = rice_params1
    k_factor1 = (shape_param1 ** 2) / 2
    cdf_rician1 = rice.cdf(x_values1, *rice_params1)
    cdf_rayleigh1 = rayleigh.cdf(x_values1, *rayleigh.fit(power11))
    cdf_weibull1 = weibull_min.cdf(x_values1, *weibull_min.fit(power11))

    x_values2 = np.linspace(min(power12), max(power12), 200)
    rice_params2 = rice.fit(power12, floc=0)
    shape_param2, _, _ = rice_params2
    k_factor2 = (shape_param2 ** 2) / 2
    cdf_rician2 = rice.cdf(x_values2, *rice_params2)
    cdf_rayleigh2 = rayleigh.cdf(x_values2, *rayleigh.fit(power12))
    cdf_weibull2 = weibull_min.cdf(x_values2, *weibull_min.fit(power12))

    x_values3 = np.linspace(min(power13), max(power13), 200)
    rice_params3 = rice.fit(power13, floc=0)
    shape_param3, _, _ = rice_params3
    k_factor3 = (shape_param3 ** 2) / 2
    cdf_rician3 = rice.cdf(x_values3, *rice_params3)
    cdf_rayleigh3 = rayleigh.cdf(x_values3, *rayleigh.fit(power13))
    cdf_weibull3 = weibull_min.cdf(x_values3, *weibull_min.fit(power13))

    # Plotting the empirical and fitted CDFs
    plt.figure()
    plt.grid(False)

    # Plot empirical CDFs
    # h1 = plt.hist(power11, bins=200, density=True, cumulative=True, histtype='step', color='r', linestyle=':',
    #               linewidth=2, label='No Wave Empirical CDFs')
    # h2 = plt.hist(power12, bins=200, density=True, cumulative=True, histtype='step', color='b', linestyle=':',
    #               linewidth=2, label='Small Wave Empirical CDFs')
    # h3 = plt.hist(power13, bins=200, density=True, cumulative=True, histtype='step', color='g', linestyle=':',
    #               linewidth=2, label='Big Wave Empirical CDFs')

    counts11, bins11 = np.histogram(power11, bins=200, density=True)
    counts12, bins12 = np.histogram(power12, bins=200, density=True)
    counts13, bins13 = np.histogram(power13, bins=200, density=True)

    # 计算累积分布
    cdf11 = np.cumsum(counts11) / np.sum(counts11)
    cdf12 = np.cumsum(counts12) / np.sum(counts12)
    cdf13 = np.cumsum(counts13) / np.sum(counts13)

    # 计算 bin 的中心点
    bin_centers11 = (bins11[:-1] + bins11[1:]) / 2
    bin_centers12 = (bins12[:-1] + bins12[1:]) / 2
    bin_centers13 = (bins13[:-1] + bins13[1:]) / 2

    # 绘制散点图
    plt.scatter(bin_centers11, cdf11, color='r', s=0.5, linestyle=':', linewidth=1.5, label='No Wave Empirical CDFs')
    plt.scatter(bin_centers12, cdf12, color='b', s=0.5, linestyle=':', linewidth=1.5, label='Small Wave Empirical CDFs')
    plt.scatter(bin_centers13, cdf13, color='g', s=0.5, linestyle=':', linewidth=1.5, label='Big Wave Empirical CDFs')

    # Plot fitted Rician CDFs
    plt.plot(x_values1, cdf_rician1, 'r-', linewidth=1, label='No Wave Fitted CDFs')
    plt.plot(x_values2, cdf_rician2, 'b-', linewidth=1, label='Small Wave Fitted CDFs')
    plt.plot(x_values3, cdf_rician3, 'g-', linewidth=1, label='Big Wave Fitted CDFs')

    plt.plot(x_values1, cdf_rayleigh1, 'r--', linewidth=1, label='No Wave Fitted Rayleigh CDFs')
    plt.plot(x_values2, cdf_rayleigh2, 'b--', linewidth=1, label='Small Wave Fitted Rayleigh CDFs')
    plt.plot(x_values3, cdf_rayleigh3, 'g--', linewidth=1, label='Big Wave Fitted Rayleigh CDFs')

    plt.plot(x_values1, cdf_weibull1, 'r-.', linewidth=1, label='No Wave Fitted Weibull CDFs')
    plt.plot(x_values2, cdf_weibull2, 'b-.', linewidth=1, label='Small Wave Fitted Weibull CDFs')
    plt.plot(x_values3, cdf_weibull3, 'g-.', linewidth=1, label='Big Wave Fitted Weibull CDFs')

    # # plt Power11, Power12, Power13, x-axis is the Number
    # plt.plot(np.arange(rmax1), Power11, 'r-', linewidth=1, label='No Wave Power')
    # plt.plot(np.arange(rmax1), Power12, 'b-', linewidth=1, label='Small Wave Power')
    # plt.plot(np.arange(rmax1), Power13, 'g-', linewidth=1, label='Big Wave Power')

    plt.xlabel(f'SNR')
    plt.ylabel('CDF')
    plt.xlim([0, 25])
    plt.legend()
    if title is not None:
        plt.title(title + f"\nK1={k_factor1:.2f}, K2={k_factor2:.2f}, K3={k_factor3:.2f}")
    if save_path is not None:
        plt.savefig(save_path)
    plt.show()



def cdf_for_indoor_water():
    save_path_base = os.path.join(os.path.dirname(__file__), 'indoor_water_cdf_pic')
    data_dict = read_all_data()

    for degree in data_dict:
        for freq in data_dict[degree]:
            data_list = [None, None, None]
            for wave in data_dict[degree][freq]:
                if wave == '小浪':
                    idx = 1
                elif wave == '大浪':
                    idx = 2
                else:
                    idx = 0
                data_list[idx] = data_dict[degree][freq][wave]

            cdf_rice([cut_data(x) for x in data_list], save_path=os.path.join(save_path_base, f'_{degree}度_{freq}GHz_{wave}.png'),
                     title=f'{degree}Degree, {freq}GHz', noice_level=39)


if __name__ == '__main__':
    cdf_for_indoor_water()
