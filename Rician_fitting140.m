clc
clear

%%读取数据，数据中每列为一组
% data1=importdata('tmp.txt');
data1=importdata('tmp.txt');
rmax1 = numel(data1)/4;

%%提取每列分别赋值到Power，SNR为（接收功率+底噪）/2
for ii=1:rmax1
   
%     Time1 (ii) = data1 (ii, 1) ;   
    Power11 (ii) = (data1(ii, 1)+38.8)/2; % 无雪SNR
    Power12 (ii) = (data1(ii, 1)+28.8)/2; %0.3mm/h(if 270GHz) 0.15mm/h(if 140GHz)
%     Power13 (ii) = (data1(ii, 4)+38.8)/2; %0.9mm/h(if 270GHz) 0.70mm/h(if 140GHz) SNR
%对数域转到线性域
    data11_linear (ii) = 10^(Power11 (ii)  / 10); 
    data12_linear (ii) = 10^(Power12 (ii)  / 10); % 如果数据以分贝为单位
%     data13_linear (ii) = 10^(Power13 (ii)  / 10); % 如果数据以分贝为单位

end

    % power11 = Power11;%实际为SNR
    % power12 = Power12;%实际为SNR
    % power13 = Power13;%实际为SNR
    power11 = data11_linear';%实际为SNR
    power12 = data12_linear';%实际为SNR
%     power13 = data13_linear';%实际为SNR

%%带入线性域SNR计算CDF
    x_values1 = linspace(min(power11), max(power11), 200);
    pd_rician1 = fitdist(power11, 'Rician');
    cdf_rician1 = cdf(pd_rician1, x_values1);

    pd_Rayleigh1 = fitdist(power11, 'Rayleigh');
    cdf_Rayleigh1 = cdf(pd_Rayleigh1, x_values1);

    pd_Weibull1 = fitdist(power11, 'Weibull');
    cdf_Weibull1 = cdf(pd_Weibull1, x_values1);
% 
%     x_values2 = linspace(min(power12), max(power12), 200);
%     pd_rician2 = fitdist(power12, 'Rician');
%     cdf_rician2 = cdf(pd_rician2, x_values2);

%     x_values3 = linspace(min(power13), max(power13), 200);
%     pd_rician3 = fitdist(power13, 'Rician');
%     cdf_rician3 = cdf(pd_rician3, x_values3);
%%画图
    figure
    h1 = cdfplot(power11); % Empirical CDF
    set(h1,'color','k','LineStyle',':','LineWidth',2);
    hold on
    plot(x_values1, cdf_rician1, 'r-', 'LineWidth', 1);
    plot(x_values1, cdf_Rayleigh1, 'b-', 'LineWidth', 1);
    plot(x_values1, cdf_Weibull1, 'g-', 'LineWidth', 1);
% 
%     h2 = cdfplot(power12); % Empirical CDF
%     set(h2,'color','k','LineStyle',':','LineWidth',2);
%     plot(x_values2, cdf_rician2, 'b-', 'LineWidth', 1);

%     h3 = cdfplot(power13); % Empirical CDF
%     set(h3,'color','k','LineStyle',':','LineWidth',2);
%     plot(x_values3, cdf_rician3, 'k', 'LineWidth', 1);

    % Str1 = {'Rr=0.7 mm/hr','μ =6.33dB'};
    % text(4.02,0.7,Str1,'Color','k','FontSize',10)
    % Str2 = {'Rr=0.15 mm/hr','μ =6.70dB'};
    % text(4.4,0.3,Str2,'Color','b','FontSize',10)
    % 
    % Str3 = {'Measured:...','Rician fitting:-'};
    % text(4.1,0.15,Str3,'Color','k','FontSize',12)
    % 
    
    % 
    % Str4 = {'(a)'};
    % text(4.02,0.95,Str4,'Color','k','FontSize',12)
    % 
    % tex = {'Rr=0','μ =6.8dB'};
    % text(4.8,0.7,tex,'Color','r',"FontSize",10);
    xlabel('SNR');
    ylabel('CDF')
    legend('Sine Wave', 'Cosine Wave');
%     xlim([4 5])
grid off;