function  check_intersection(map_obj)
%CHECK_INTERSECTION Summary of this function goes here
%   Detailed explanation goes here
k = keys(map_obj); 
for i = 1:length(k) -1
    A_set =map_obj(k{i});
   
    for j = i+1:length(k)
        fprintf("Comparing %s and %s\n",k{i}, k{j})
         setA = java.util.HashSet(A_set);
         %disp(setA);
         
         setB = map_obj(k{j});
         
         %disp(setB);
         setA.retainAll(setB);
         if isempty(setA)
         disp("NO Intersection")
         else  
         disp(setA);
         end
         
        
    end
end

