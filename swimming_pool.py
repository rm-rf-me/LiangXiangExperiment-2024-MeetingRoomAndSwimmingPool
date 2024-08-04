import numpy as np
import pandas as pd
import json
import os
import matplotlib.pyplot as plt

los_high_no_wave = {
    220: '2024-07-26-11-37-30_220GHz_swmmingpool_los_3.xlsx',
    225: '2024-07-26-11-44-34_225GHz_swmmingpool_los_3.xlsx',
    229: '2024-07-26-11-49-03_229GHz_swmmingpool_los_3.xlsx'
}

los_high_little_wave = {
    220: '2024-07-26-12-13-20_220GHZ_swimmingpool_los_little_wave.xlsx',
    225: '2024-07-26-12-11-03_225GHZ_swimmingpool_los_little_wave.xlsx',
    229: '2024-07-26-12-00-20_229GHz_swmmingpool_los_little_wave.xlsx'
}
los_high_big_wave = {
    220: '2024-07-26-12-18-03_220GHZ_swimmingpool_los_big_wave.xlsx',
    225: '2024-07-26-12-20-40_225GHZ_swimmingpool_los_big_wave.xlsx',
    229: '2024-07-26-12-24-11_229GHZ_swimmingpool_los_big_wave.xlsx'
}

nlos_high_no_wave = {
    220: '2024-07-26-14-14-02_220GHz_swimmingpool_nLos_1.xlsx',
    225: '2024-07-26-14-18-02_225GHz_swimmingpool_nLos_1.xlsx',
    229: '2024-07-26-14-23-01_229GHz_swimmingpool_nLos_1.xlsx'
}

nlos_high_little_wave = {
    220: '2024-07-26-14-31-13_220GHz swimmingpool nlos little wave.xlsx',
    225: '2024-07-26-14-34-32_225GHz swimmingpool nlos little wave.xlsx',
    229: '2024-07-26-14-37-00_229GHz swimmingpool nlos little wave.xlsx'
}

nlos_high_big_wave = {
    220: '2024-07-26-14-42-37_220GHz big wave nlos.xlsx',
    225: '2024-07-26-14-45-20_225GHz big wave nlos.xlsx',
    229: '2024-07-26-14-54-19_229GHz big wave nlos.xlsx'
}

nlos_high_400m = {
    220: [
        "2024-07-26-14-59-20_220GHz 400m.xlsx",
        "2024-07-26-15-05-11_220.xlsx"
    ],
    225: "2024-07-26-15-01-35_225.xlsx",
    229: "2024-07-26-15-03-20_229.xlsx"
}

los_low_no_wave = {
    140: '2024-07-26-15-46-59_140GHz swmmingpool los.xlsx',
    120: '2024-07-26-15-50-42_120GHz swmming pool los.xlsx',
    160: '2024-07-26-15-54-39_160GHz swmming pool los.xlsx'
}

los_low_little_wave = {
    140: '2024-07-26-16-07-30_140GHz swmming pool los little wave.xlsx',
    120: '2024-07-26-16-09-11_120GHz swmming pool los little wave.xlsx',
    160: '2024-07-26-16-00-53_160GHz swmming pool los little wave.xlsx'
}

los_low_big_wave = {
    140: '2024-07-26-16-14-27_140GHz los big wave.xlsx',
    120: '2024-07-26-16-16-30_120GHz los big wave.xlsx',
    160: '2024-07-26-16-12-11_160GHz los big wave.xlsx'
}

nlos_low_no_wave = {
    140: '2024-07-26-16-38-53_140GHz nlos .xlsx',
    120: '2024-07-26-16-43-06_120GHz swmming pool nlos.xlsx',
    160: '2024-07-26-16-46-49_160GHz swmming pool nlos.xlsx'
}

nlos_low_little_wave = {
    140: '2024-07-26-16-53-28_140 nlos little wave.xlsx',
    120: '2024-07-26-16-51-31_120 nlos littile wave.xlsx',
    160: '2024-07-26-16-56-27_160 nlos little wave.xlsx'
}
nlos_low_big_wave = {
    140: '2024-07-26-17-01-07_140 nlos big wave.xlsx',
    120: '2024-07-26-17-03-12_120 nlos big wave.xlsx',
    160: '2024-07-26-16-58-19_160 nlos big wave.xlsx'
}

all_data = {
    'los_high_no_wave': los_high_no_wave,
    'los_high_little_wave': los_high_little_wave,
    'los_high_big_wave': los_high_big_wave,
    'nlos_high_no_wave': nlos_high_no_wave,
    'nlos_high_little_wave': nlos_high_little_wave,
    'nlos_high_big_wave': nlos_high_big_wave,
    'nlos_high_400m': nlos_high_400m,
    'los_low_no_wave': los_low_no_wave,
    'los_low_little_wave': los_low_little_wave,
    'los_low_big_wave': los_low_big_wave,
    'nlos_low_no_wave': nlos_low_no_wave,
    'nlos_low_little_wave': nlos_low_little_wave,
    'nlos_low_big_wave': nlos_low_big_wave
}

base_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '游泳池')


def read_data(file_name):
    data = pd.read_excel(os.path.join(base_path, file_name), header=None)

    return data


def read_all_data():
    data_dict = {}
    for key, value in all_data.items():
        if isinstance(value, dict):
            data_dict[key] = {}
            for freq, file_name in value.items():
                if isinstance(file_name, list):
                    data_dict[key][freq] = []
                    for file in file_name:
                        data = read_data(file)
                        data_dict[key][freq].append(data)
                else:
                    data = read_data(file_name)
                    data_dict[key][freq] = data

        else:
            data_dict[key] = read_data(value)
    return data_dict


def plot_data_list(data_list, title, save_path=None):
    # make this figure wider
    plt.rcParams['figure.figsize'] = [12, 4]
    plt.figure()
    for k, data in data_list.items():
        # plt.plot(data[1][1:].str.split().str.get(1), data[4][1:], label=k)
        plt.plot(data[0][1:], data[4][1:], label=k)
    plt.title(title)
    plt.xlabel('X')
    plt.tick_params(axis='x', rotation=45)
    plt.ylabel('Amplitude (dbm)')
    plt.legend()
    if save_path:
        plt.savefig(save_path)
    plt.show()


if __name__ == '__main__':
    pic_base = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'swimming_pool_pic')
    data_dict = read_all_data()
    print(data_dict.keys())
    los_high_list = {
        220: {
            "No Wave":data_dict['los_high_no_wave'][220],
            "Little Wave": data_dict['los_high_little_wave'][220],
            "Big Wave": data_dict['los_high_big_wave'][220]
        },
        225: {
            "No Wave": data_dict['los_high_no_wave'][225],
            "Little Wave": data_dict['los_high_little_wave'][225],
            "Big Wave": data_dict['los_high_big_wave'][225]
        },
        229: {
            "No Wave": data_dict['los_high_no_wave'][229],
            "Little Wave": data_dict['los_high_little_wave'][229],
            "Big Wave": data_dict['los_high_big_wave'][229]
        }
    }
    plot_data_list(los_high_list[220], "LOS High 220GHz", os.path.join(pic_base, "los_high_220.png"))
    plot_data_list(los_high_list[225], "LOS High 225GHz", os.path.join(pic_base, "los_high_225.png"))
    plot_data_list(los_high_list[229], "LOS High 229GHz", os.path.join(pic_base, "los_high_229.png"))

    nlos_high_list = {
        220: {
            "No Wave": data_dict['nlos_high_no_wave'][220],
            "Little Wave": data_dict['nlos_high_little_wave'][220],
            "Big Wave": data_dict['nlos_high_big_wave'][220]
        },
        225: {
            "No Wave": data_dict['nlos_high_no_wave'][225],
            "Little Wave": data_dict['nlos_high_little_wave'][225],
            "Big Wave": data_dict['nlos_high_big_wave'][225]
        },
        229: {
            "No Wave": data_dict['nlos_high_no_wave'][229],
            "Little Wave": data_dict['nlos_high_little_wave'][229],
            "Big Wave": data_dict['nlos_high_big_wave'][229]
        }
    }
    plot_data_list(nlos_high_list[220], "NLOS High 220GHz", os.path.join(pic_base, "nlos_high_220.png"))
    plot_data_list(nlos_high_list[225], "NLOS High 225GHz", os.path.join(pic_base, "nlos_high_225.png"))
    plot_data_list(nlos_high_list[229], "NLOS High 229GHz", os.path.join(pic_base, "nlos_high_229.png"))

    # nlos_high_400m_list = {
    #     220: {
    #         "No Wave": data_dict['nlos_high_400m'][220][0],
    #         "Little Wave": data_dict['nlos_high_400m'][220][1]
    #     },
    #     225: data_dict['nlos_high_400m'][225],
    #     229: data_dict['nlos_high_400m'][229]
    # }
    nlos_high_people_swimmming_list = {
        "220-1": data_dict['nlos_high_400m'][220][0],
        "220-2": data_dict['nlos_high_400m'][220][1],
        "225": data_dict['nlos_high_400m'][225],
        "229": data_dict['nlos_high_400m'][229]
    }
    plot_data_list(nlos_high_people_swimmming_list, "NLOS High 400m People Swimming", os.path.join(pic_base, "nlos_high_400m_people_swimming.png"))
    plot_data_list({"220-1": data_dict['nlos_high_400m'][220][0]}, "NLOS High 400m People Swimming 220-1", os.path.join(pic_base, "nlos_high_400m_people_swimming_220-1.png"))
    plot_data_list({"220-2": data_dict['nlos_high_400m'][220][1]}, "NLOS High 400m People Swimming 220-2",
                   os.path.join(pic_base, "nlos_high_400m_people_swimming_220-2.png"))
    plot_data_list({"225": data_dict['nlos_high_400m'][225]}, "NLOS High 400m People Swimming 225", os.path.join(pic_base, "nlos_high_400m_people_swimming_225.png"))
    plot_data_list({"229": data_dict['nlos_high_400m'][229]}, "NLOS High 400m People Swimming 229", os.path.join(pic_base, "nlos_high_400m_people_swimming_229.png"))

    los_low_list = {
        140: {
            "No Wave": data_dict['los_low_no_wave'][140],
            "Little Wave": data_dict['los_low_little_wave'][140],
            "Big Wave": data_dict['los_low_big_wave'][140]
        },
        120: {
            "No Wave": data_dict['los_low_no_wave'][120],
            "Little Wave": data_dict['los_low_little_wave'][120],
            "Big Wave": data_dict['los_low_big_wave'][120]
        },
        160: {
            "No Wave": data_dict['los_low_no_wave'][160],
            "Little Wave": data_dict['los_low_little_wave'][160],
            "Big Wave": data_dict['los_low_big_wave'][160]
        }
    }
    plot_data_list(los_low_list[140], "LOS Low 140GHz", os.path.join(pic_base, "los_low_140.png"))
    plot_data_list(los_low_list[120], "LOS Low 120GHz", os.path.join(pic_base, "los_low_120.png"))
    plot_data_list(los_low_list[160], "LOS Low 160GHz", os.path.join(pic_base, "los_low_160.png"))

    nlos_low_list = {
        140: {
            "No Wave": data_dict['nlos_low_no_wave'][140],
            "Little Wave": data_dict['nlos_low_little_wave'][140],
            "Big Wave": data_dict['nlos_low_big_wave'][140]
        },
        120: {
            "No Wave": data_dict['nlos_low_no_wave'][120],
            "Little Wave": data_dict['nlos_low_little_wave'][120],
            "Big Wave": data_dict['nlos_low_big_wave'][120]
        },
        160: {
            "No Wave": data_dict['nlos_low_no_wave'][160],
            "Little Wave": data_dict['nlos_low_little_wave'][160],
            "Big Wave": data_dict['nlos_low_big_wave'][160]
        }
    }
    plot_data_list(nlos_low_list[140], "NLOS Low 140GHz", os.path.join(pic_base, "nlos_low_140.png"))
    plot_data_list(nlos_low_list[120], "NLOS Low 120GHz", os.path.join(pic_base, "nlos_low_120.png"))
    plot_data_list(nlos_low_list[160], "NLOS Low 160GHz", os.path.join(pic_base, "nlos_low_160.png"))


