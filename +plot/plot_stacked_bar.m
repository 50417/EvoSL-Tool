function plot_stacked_bar(nodeandchangetype_matrix,xlabels)
    % Plotting a stacked bar chart
    figure(); 
    bar(nodeandchangetype_matrix, 'stacked'); 
    for i=1:size(nodeandchangetype_matrix,1)
        for j=1:size(nodeandchangetype_matrix,2)
            if nodeandchangetype_matrix(i,j)>0
            labels_stacked=num2str(nodeandchangetype_matrix(i,j),'%.2f');
            hText = text(i, sum(nodeandchangetype_matrix(i,1:j),2), labels_stacked);
            set(hText, 'VerticalAlignment','top', 'HorizontalAlignment', 'center','FontSize',10, 'Color','w');
            end
        end
    end
    set(gca,'XTickLabel',xlabels);
    
end

