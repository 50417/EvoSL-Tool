function  plot_bubblechart(category,category_percentage)
%PLOT_BUBBLECHART Summary of this function goes here

    figure;
    %x = [1:length(category)];
    %bubblechart(x,2*category_percentage,category_percentage);
    [~,sorted_idx] = sort(category_percentage);
    left = 1; 
    right = length(sorted_idx);
    new_order = ones(left,right);
    new_category_order = repmat({' '},left,right);
    
    for i = 1:length(sorted_idx)
        if mod(i,2)==0
            new_order(i) = category_percentage(sorted_idx(left));
            new_category_order{i} = strcat(category{sorted_idx(left)},sprintf(" %0.2f%%",new_order(i)));
            left = left + 1;
            
        else
            new_order(i) = category_percentage(sorted_idx(right));
            new_category_order{i} =strcat(category{sorted_idx(right)},sprintf(" %0.2f%%",new_order(i)));
            right = right -1;
        end
        
    end
    explode = ones(1,length(category_percentage));
    explode(length(category_percentage)-1) = 0;
    pie(new_order,explode,new_category_order);
    colormap('gray');
end

