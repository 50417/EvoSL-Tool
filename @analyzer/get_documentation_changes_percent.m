function [doc_changes_percent,doc_type] = get_documentation_changes_percent(obj)
%GET_DOCUMENTATION_CHANGES_PERCENT Summary of this function goes here
%   Detailed explanation goes here


     doc_type = {'annotation','DocBlock','Model Info'};
     doc_changes_percent = zeros(1,3);
     annotation_count_query =     [  'SELECT count(*) cnt ' ...
                ' FROM ' char(obj.table_name) ...
                ' WHERE node_type == "annotation"' 
                ];
            
     result = fetch(obj.conn, annotation_count_query);
     annotation_cnt = result{1,1};
     
     docBlock_count_query =     [  'SELECT count(*) cnt ' ...
                ' FROM ' char(obj.table_name) ...
                ' WHERE block_path Like "%DocBlock"' 
                ];
            
     result = fetch(obj.conn, docBlock_count_query);
     docBlock_cnt = result{1,1};
     
     mdlinfo_count_query =  [  'SELECT count(*) cnt ' ...
                ' FROM ' char(obj.table_name) ...
                ' WHERE block_path Like "%Model Info"' 
                ];
            
     result = fetch(obj.conn, mdlinfo_count_query);
     mdlinfo_cnt = result{1,1};
      
     total_cnt = annotation_cnt + docBlock_cnt + mdlinfo_cnt;
     total_cnt = cast(total_cnt,"double");
     doc_changes_percent(1,1) = round(double(annotation_cnt)/double(total_cnt)*100,2);
     doc_changes_percent(1,2) = round((double(docBlock_cnt)/double(total_cnt))*100,2);
     doc_changes_percent(1,3) = round((double(mdlinfo_cnt)/double(total_cnt))*100,2);
end

