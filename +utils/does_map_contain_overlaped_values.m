function [res] = does_map_contain_overlaped_values(map_obj)
%DOES_MAP_CONTAIN_NO Summary of this function goes here
%   Detailed explanation goes here
res = false;
k = keys(map_obj); 
for i = 1:length(k)-1
    k1 = k{i};
    for j = i+1:length(k)
        k2 = k{j};

        vals1 = map_obj(k1);
        vals2 = map_obj(k2);
        
        overlaped = compare_two_sets(vals1, vals2);
        if ~overlaped
            disp("=======================================");
            disp(k1);
            disp(k2);
            disp(vals1);
            disp(vals2);
              disp("=======================================");
        end
      
    end
end
end


function res=compare_two_sets(s1,s2)
    res = true; 
    tmp1 = s1.clone(); 
    tmp2 = s2.clone(); 
    tmp1.retainAll(tmp2);
    if size(tmp1) ~= 0
        res = false;
    end
    
end

