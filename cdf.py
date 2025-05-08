import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import rice, rayleigh, weibull_min
import os


def cdf_rice(data_list, save_path=None, title=None, noice_level=None):
    # 设置全局字体为 Times New Roman
    plt.rcParams.update({
        'font.family': 'Times New Roman',
        'font.size': 12,  # 增大默认字体
        'mathtext.fontset': 'stix'
    })
    
    # 设置图片尺寸和DPI
    plt.rcParams['figure.figsize'] = [5, 3]
    plt.rcParams['figure.dpi'] = 300
    
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
    print(f"title: {title}, weibull_param1: {weibull_min.fit(power11)}")
    cdf_weibull1 = weibull_min.cdf(x_values1, *weibull_min.fit(power11))

    x_values2 = np.linspace(min(power12), max(power12), 200)
    rice_params2 = rice.fit(power12, floc=0)
    shape_param2, _, _ = rice_params2
    k_factor2 = (shape_param2 ** 2) / 2
    cdf_rician2 = rice.cdf(x_values2, *rice_params2)
    cdf_rayleigh2 = rayleigh.cdf(x_values2, *rayleigh.fit(power12))
    print(f"title: {title}, weibull_param2: {weibull_min.fit(power12)}")
    cdf_weibull2 = weibull_min.cdf(x_values2, *weibull_min.fit(power12))

    x_values3 = np.linspace(min(power13), max(power13), 200)
    rice_params3 = rice.fit(power13, floc=0)
    shape_param3, _, _ = rice_params3
    k_factor3 = (shape_param3 ** 2) / 2
    cdf_rician3 = rice.cdf(x_values3, *rice_params3)
    cdf_rayleigh3 = rayleigh.cdf(x_values3, *rayleigh.fit(power13))
    print(f"title: {title}, weibull_param3: {weibull_min.fit(power13)}")
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

    # 绘制散点图，使用更小的点和统一的实线
    plt.scatter(bin_centers11, cdf11, color='#1f77b4', s=0.5, label='No Wave (Measured)')
    plt.scatter(bin_centers12, cdf12, color='#ff7f0e', s=0.5, label='Small Wave (Measured)')
    plt.scatter(bin_centers13, cdf13, color='#2ca02c', s=0.5, label='Big Wave (Measured)')

    plt.plot(x_values1, cdf_weibull1, color='#1f77b4', linewidth=1, label='No Wave (Weibull)')
    plt.plot(x_values2, cdf_weibull2, color='#ff7f0e', linewidth=1, label='Small Wave (Weibull)')
    plt.plot(x_values3, cdf_weibull3, color='#2ca02c', linewidth=1, label='Big Wave (Weibull)')

    # 绘制拟合曲线，使用实线
    # plt.plot(x_values1, cdf_rician1, color='#1f77b4', linewidth=1.5, label='No Wave Rician')
    # plt.plot(x_values2, cdf_rician2, color='#ff7f0e', linewidth=1.5, label='Small Wave Rician')
    # plt.plot(x_values3, cdf_rician3, color='#2ca02c', linewidth=1.5, label='Big Wave Rician')

    # plt.plot(x_values1, cdf_rayleigh1, 'r--', linewidth=1, label='No Wave Fitted Rayleigh CDFs')
    # plt.plot(x_values2, cdf_rayleigh2, 'b--', linewidth=1, label='Small Wave Fitted Rayleigh CDFs')
    # plt.plot(x_values3, cdf_rayleigh3, 'g--', linewidth=1, label='Big Wave Fitted Rayleigh CDFs')

    # plt.plot(x_values1, cdf_weibull1, 'r-.', linewidth=1, label='No Wave Fitted Weibull CDFs')
    # plt.plot(x_values2, cdf_weibull2, 'b-.', linewidth=1, label='Small Wave Fitted Weibull CDFs')
    # plt.plot(x_values3, cdf_weibull3, 'g-.', linewidth=1, label='Big Wave Fitted Weibull CDFs')

    # # plt Power11, Power12, Power13, x-axis is the Number
    # plt.plot(np.arange(rmax1), Power11, 'r-', linewidth=1, label='No Wave Power')
    # plt.plot(np.arange(rmax1), Power12, 'b-', linewidth=1, label='Small Wave Power')
    # plt.plot(np.arange(rmax1), Power13, 'g-', linewidth=1, label='Big Wave Power')

    # 设置轴标签和标题，使用更大的字体
    plt.xlabel('SNR', fontsize=12, labelpad=8)
    plt.ylabel('CDF', fontsize=12, labelpad=8)
    
    # if title is not None:
    #     plt.title(title,
    #               pad=10, fontsize=14, fontweight='bold')
        # plt.title(title + f"\nK1={k_factor1:.2f}, K2={k_factor2:.2f}, K3={k_factor3:.2f}", 
        #          pad=10, fontsize=14, fontweight='bold')
    
    # 设置刻度，增大字体
    plt.tick_params(axis='both', direction='in', labelsize=11)
    
    # 添加网格线
    plt.grid(True, linestyle='--', alpha=0.3)

    # plt.xlim(0, 16)
    
    # 去除四周边框
    ax = plt.gca()
    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)

    # 图例放到图片外部右侧
    handles, labels = ax.get_legend_handles_labels()
    plt.legend(
        handles, labels,
        loc='center left',
        bbox_to_anchor=(1.01, 0.5),
        frameon=False,
        fontsize=10,
        ncol=1
    )

    plt.tight_layout()  # 右侧留出空间给图例
    
    # 保存图片
    if save_path:
        plt.savefig(save_path, 
                   bbox_inches='tight',
                   pad_inches=0.1,
                   dpi=300)
    
    plt.show()


def cut_data(data_dict, length=None):
    data = data_dict['data']
    start = data_dict['start']
    if length is None:
        return data[4][start:].reset_index(drop=True)
    return data[4][start:start + length].reset_index(drop=True)


def cdf_for_swimming_poll():
    from swimming_pool import read_all_data
    save_path_base = os.path.join(os.path.dirname(__file__), 'swimming_pool_cdf_pic')
    data_dict = read_all_data()
    # los_high_list = {
    #     220: {
    #         "No Wave": data_dict['los_high_no_wave'][220],
    #         "Little Wave": data_dict['los_high_little_wave'][220],
    #         "Big Wave": data_dict['los_high_big_wave'][220]
    #     },
    #     225: {
    #         "No Wave": data_dict['los_high_no_wave'][225],
    #         "Little Wave": data_dict['los_high_little_wave'][225],
    #         "Big Wave": data_dict['los_high_big_wave'][225]
    #     },
    #     229: {
    #         "No Wave": data_dict['los_high_no_wave'][229],
    #         "Little Wave": data_dict['los_high_little_wave'][229],
    #         "Big Wave": data_dict['los_high_big_wave'][229]
    #     }
    # }
    los_high_list = {
        220: {
            "No Wave": {'data': data_dict['los_high_no_wave'][220], "start": 0},
            "Little Wave": {'data': data_dict['los_high_little_wave'][220], "start": 0},
            "Big Wave": {'data': data_dict['los_high_big_wave'][220], "start": 0}
        },
        225: {
            "No Wave": {'data': data_dict['los_high_no_wave'][225], "start": 0},
            "Little Wave": {'data': data_dict['los_high_little_wave'][225], "start": 0},
            "Big Wave": {'data': data_dict['los_high_big_wave'][225], "start": 0}
        },
        229: {
            "No Wave": {'data': data_dict['los_high_no_wave'][229], "start": 0},
            "Little Wave": {'data': data_dict['los_high_little_wave'][229], "start": 0},
            "Big Wave": {'data': data_dict['los_high_big_wave'][229], "start": 0}
        }
    }

    cdf_rice([cut_data(x) for x in los_high_list[220].values()],
             save_path=os.path.join(save_path_base, '_los_high_no_wave.png'), title='Los 220GHz', noice_level=39)
    cdf_rice([cut_data(x) for x in los_high_list[225].values()],
             save_path=os.path.join(save_path_base, '_los_high_little_wave.png'), title='Los 225GHz', noice_level=39)
    cdf_rice([cut_data(x) for x in los_high_list[229].values()],
             save_path=os.path.join(save_path_base, '_los_high_big_wave.png'), title='Los 229GHz', noice_level=39)
    # nlos_high_list = {
    #     220: {
    #         "No Wave": data_dict['nlos_high_no_wave'][220],
    #         "Little Wave": data_dict['nlos_high_little_wave'][220],
    #         "Big Wave": data_dict['nlos_high_big_wave'][220]
    #     },
    #     225: {
    #         "No Wave": data_dict['nlos_high_no_wave'][225],
    #         "Little Wave": data_dict['nlos_high_little_wave'][225],
    #         "Big Wave": data_dict['nlos_high_big_wave'][225]
    #     },
    #     229: {
    #         "No Wave": data_dict['nlos_high_no_wave'][229],
    #         "Little Wave": data_dict['nlos_high_little_wave'][229],
    #         "Big Wave": data_dict['nlos_high_big_wave'][229]
    #     }
    # }
    nlos_high_list = {
        220: {
            "No Wave": {'data': data_dict['nlos_high_no_wave'][220], "start": 0},
            "Little Wave": {'data': data_dict['nlos_high_little_wave'][220], "start": 100},
            "Big Wave": {'data': data_dict['nlos_high_big_wave'][220], "start": 100}
        },
        225: {
            "No Wave": {'data': data_dict['nlos_high_no_wave'][225], "start": 0},
            "Little Wave": {'data': data_dict['nlos_high_little_wave'][225], "start": 50},
            "Big Wave": {'data': data_dict['nlos_high_big_wave'][225], "start": 300}
        },
        229: {
            "No Wave": {'data': data_dict['nlos_high_no_wave'][229], "start": 0},
            "Little Wave": {'data': data_dict['nlos_high_little_wave'][229], "start": 50},
            "Big Wave": {'data': data_dict['nlos_high_big_wave'][229], "start": 100}
        }
    }
    cdf_rice([cut_data(x) for x in nlos_high_list[220].values()],
             save_path=os.path.join(save_path_base, '_nlos_high_no_wave.png'), title='(b) N-Los 220GHz', noice_level=39)
    cdf_rice([cut_data(x) for x in nlos_high_list[225].values()],
             save_path=os.path.join(save_path_base, '_nlos_high_little_wave.png'), title='N-Los 225GHz', noice_level=39)
    cdf_rice([cut_data(x) for x in nlos_high_list[229].values()],
             save_path=os.path.join(save_path_base, '_nlos_high_big_wave.png'), title='N-Los 229GHz', noice_level=39)
    # los_low_list = {
    #     140: {
    #         "No Wave": data_dict['los_low_no_wave'][140],
    #         "Little Wave": data_dict['los_low_little_wave'][140],
    #         "Big Wave": data_dict['los_low_big_wave'][140]
    #     },
    #     120: {
    #         "No Wave": data_dict['los_low_no_wave'][120],
    #         "Little Wave": data_dict['los_low_little_wave'][120],
    #         "Big Wave": data_dict['los_low_big_wave'][120]
    #     },
    #     160: {
    #         "No Wave": data_dict['los_low_no_wave'][160],
    #         "Little Wave": data_dict['los_low_little_wave'][160],
    #         "Big Wave": data_dict['los_low_big_wave'][160]
    #     }
    # }
    los_low_list = {
        140: {
            "No Wave": {'data': data_dict['los_low_no_wave'][140], "start": 0},
            "Little Wave": {'data': data_dict['los_low_little_wave'][140], "start": 50},
            "Big Wave": {'data': data_dict['los_low_big_wave'][140], "start": 50}
        },
        120: {
            "No Wave": {'data': data_dict['los_low_no_wave'][120], "start": 0},
            "Little Wave": {'data': data_dict['los_low_little_wave'][120], "start": 0},
            "Big Wave": {'data': data_dict['los_low_big_wave'][120], "start": 100}
        },
        160: {
            "No Wave": {'data': data_dict['los_low_no_wave'][160], "start": 0},
            "Little Wave": {'data': data_dict['los_low_little_wave'][160], "start": 0},
            "Big Wave": {'data': data_dict['los_low_big_wave'][160], "start": 100}
        }
    }
    cdf_rice([cut_data(x) for x in los_low_list[140].values()],
             save_path=os.path.join(save_path_base, '_los_low_no_wave.png'), title='Los 140GHz', noice_level=38)
    cdf_rice([cut_data(x) for x in los_low_list[120].values()],
             save_path=os.path.join(save_path_base, '_los_low_little_wave.png'), title='Los 120GHz', noice_level=38)
    cdf_rice([cut_data(x) for x in los_low_list[160].values()],
             save_path=os.path.join(save_path_base, '_los_low_big_wave.png'), title='Los 160GHz', noice_level=38)
    # nlos_low_list = {
    #     140: {
    #         "No Wave": data_dict['nlos_low_no_wave'][140],
    #         "Little Wave": data_dict['nlos_low_little_wave'][140],
    #         "Big Wave": data_dict['nlos_low_big_wave'][140]
    #     },
    #     120: {
    #         "No Wave": data_dict['nlos_low_no_wave'][120],
    #         "Little Wave": data_dict['nlos_low_little_wave'][120],
    #         "Big Wave": data_dict['nlos_low_big_wave'][120]
    #     },
    #     160: {
    #         "No Wave": data_dict['nlos_low_no_wave'][160],
    #         "Little Wave": data_dict['nlos_low_little_wave'][160],
    #         "Big Wave": data_dict['nlos_low_big_wave'][160]
    #     }
    # }
    nlos_low_list = {
        140: {
            "No Wave": {'data': data_dict['nlos_low_no_wave'][140], "start": 0},
            "Little Wave": {'data': data_dict['nlos_low_little_wave'][140], "start": 150},
            "Big Wave": {'data': data_dict['nlos_low_big_wave'][140], "start": 150}
        },
        120: {
            "No Wave": {'data': data_dict['nlos_low_no_wave'][120], "start": 0},
            "Little Wave": {'data': data_dict['nlos_low_little_wave'][120], "start": 150},
            "Big Wave": {'data': data_dict['nlos_low_big_wave'][120], "start": 150}
        },
        160: {
            "No Wave": {'data': data_dict['nlos_low_no_wave'][160], "start": 0},
            "Little Wave": {'data': data_dict['nlos_low_little_wave'][160], "start": 50},
            "Big Wave": {'data': data_dict['nlos_low_big_wave'][160], "start": 50}
        }
    }
    cdf_rice([cut_data(x) for x in nlos_low_list[140].values()],
             save_path=os.path.join(save_path_base, '_nlos_low_no_wave.png'), title='N-Los 140GHz', noice_level=38)
    cdf_rice([cut_data(x) for x in nlos_low_list[120].values()],
             save_path=os.path.join(save_path_base, '_nlos_low_little_wave.png'), title='N-Los 120GHz', noice_level=38)
    cdf_rice([cut_data(x) for x in nlos_low_list[160].values()],
             save_path=os.path.join(save_path_base, '_nlos_low_big_wave.png'), title='(a) N-Los 160GHz', noice_level=38)


if __name__ == '__main__':
    cdf_for_swimming_poll()
