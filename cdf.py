import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import rice
import os


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
    cdf_rician1 = rice.cdf(x_values1, *rice.fit(power11))

    x_values2 = np.linspace(min(power12), max(power12), 200)
    cdf_rician2 = rice.cdf(x_values2, *rice.fit(power12))

    x_values3 = np.linspace(min(power13), max(power13), 200)
    cdf_rician3 = rice.cdf(x_values3, *rice.fit(power13))

    # Plotting the empirical and fitted CDFs
    plt.figure()
    plt.grid(False)

    # Plot empirical CDFs
    h1 = plt.hist(power11, bins=200, density=True, cumulative=True, histtype='step', color='r', linestyle=':',
                  linewidth=2, label='No Wave Empirical CDFs')
    h2 = plt.hist(power12, bins=200, density=True, cumulative=True, histtype='step', color='b', linestyle=':',
                  linewidth=2, label='Small Wave Empirical CDFs')
    h3 = plt.hist(power13, bins=200, density=True, cumulative=True, histtype='step', color='g', linestyle=':',
                  linewidth=2, label='Big Wave Empirical CDFs')

    # Plot fitted Rician CDFs
    plt.plot(x_values1, cdf_rician1, 'r-', linewidth=1, label='No Wave Fitted CDFs')
    plt.plot(x_values2, cdf_rician2, 'b-', linewidth=1, label='Small Wave Fitted CDFs')
    plt.plot(x_values3, cdf_rician3, 'g-', linewidth=1, label='Big Wave Fitted CDFs')

    # # plt Power11, Power12, Power13, x-axis is the Number
    # plt.plot(np.arange(rmax1), Power11, 'r-', linewidth=1, label='No Wave Power')
    # plt.plot(np.arange(rmax1), Power12, 'b-', linewidth=1, label='Small Wave Power')
    # plt.plot(np.arange(rmax1), Power13, 'g-', linewidth=1, label='Big Wave Power')

    plt.xlabel('SNR')
    plt.ylabel('CDF')
    plt.xlim([0, 16])
    plt.legend()
    if title is not None:
        plt.title(title)
    if save_path is not None:
        plt.savefig(save_path)
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
             save_path=os.path.join(save_path_base, '_los_high_no_wave.png'), title='LOS 220GHz', noice_level=39)
    cdf_rice([cut_data(x) for x in los_high_list[225].values()],
             save_path=os.path.join(save_path_base, '_los_high_little_wave.png'), title='LOS 225GHz', noice_level=39)
    cdf_rice([cut_data(x) for x in los_high_list[229].values()],
             save_path=os.path.join(save_path_base, '_los_high_big_wave.png'), title='LOS 229GHz', noice_level=39)
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
             save_path=os.path.join(save_path_base, '_nlos_high_no_wave.png'), title='NLOS 220GHz', noice_level=39)
    cdf_rice([cut_data(x) for x in nlos_high_list[225].values()],
             save_path=os.path.join(save_path_base, '_nlos_high_little_wave.png'), title='NLOS 225GHz', noice_level=39)
    cdf_rice([cut_data(x) for x in nlos_high_list[229].values()],
             save_path=os.path.join(save_path_base, '_nlos_high_big_wave.png'), title='NLOS 229GHz', noice_level=39)
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
             save_path=os.path.join(save_path_base, '_los_low_no_wave.png'), title='LOS 140GHz', noice_level=38)
    cdf_rice([cut_data(x) for x in los_low_list[120].values()],
             save_path=os.path.join(save_path_base, '_los_low_little_wave.png'), title='LOS 120GHz', noice_level=38)
    cdf_rice([cut_data(x) for x in los_low_list[160].values()],
             save_path=os.path.join(save_path_base, '_los_low_big_wave.png'), title='LOS 160GHz', noice_level=38)
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
             save_path=os.path.join(save_path_base, '_nlos_low_no_wave.png'), title='NLOS 140GHz', noice_level=38)
    cdf_rice([cut_data(x) for x in nlos_low_list[120].values()],
             save_path=os.path.join(save_path_base, '_nlos_low_little_wave.png'), title='NLOS 120GHz', noice_level=38)
    cdf_rice([cut_data(x) for x in nlos_low_list[160].values()],
             save_path=os.path.join(save_path_base, '_nlos_low_big_wave.png'), title='NLOS 160GHz', noice_level=38)


if __name__ == '__main__':
    cdf_for_swimming_poll()
