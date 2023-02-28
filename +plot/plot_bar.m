function plot_bar(x_label,y,offset,xtickangle,ytextangle,ytick,ylimits,y_label)
%PLOT_BAR Summary of this function goes here
%   Detailed explanation goes here
    figure('Position',[100 100 1200 400]); 
    x = [1:length(y)];
    hB = bar(x,y);
    clrs = [0 0 0];
    set(hB,{'FaceColor'},{clrs(1,:)}.');
    set(gca, 'XTick', 1:length(x_label),'XTickLabel',x_label,'XTickLabelRotation',xtickangle);
    set(gca,'YTick',ytick);
    ylabel(y_label);
    ylim(ylimits);
    ax = gca;
    ax.YRuler.Exponent = 0; 
    for i = 1:length(y)                                                               
        text(x(i), double(y(i))+offset, utils.add_comma_to_num(y(i)), 'HorizontalAlignment','center', 'VerticalAlignment','middle','Rotation',ytextangle);
    end
    
end

