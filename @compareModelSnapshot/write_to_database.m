 function output_bol = write_to_database(obj, before_sha, after_sha, model,comparison_res_table)

            [rows,~] = size(comparison_res_table);
            for r = 1:rows
                block_path = comparison_res_table.path(r);
                block_path = block_path{1};
                
                node_type =  comparison_res_table.nodeType(r);
                node_type = node_type{1};
                
                block_type =  comparison_res_table.blockType(r);
                block_type = block_type{1};
                
                change_type =  comparison_res_table.changeType(r);
                change_type = change_type{1};
                is_modified = 0;
                is_added = 0;
                is_renamed = 0; 
                is_deleted = 0;
                
                if iscell(change_type)
                    %SEE getNodeChangeType.m in Model comparaision Utility
                    is_modified = 1;
                    is_renamed = 1; 
                else
                    switch change_type
                        case 'added'
                            is_added = 1; 
                        case 'deleted'
                            is_deleted = 1; 
                        case 'modified'
                            is_modified = 1; 
                        case 'renamed'
                            is_renamed = 1; 
                    end
                            
                
                end
                insert(obj.conn,obj.table_name,obj.colnames, ...
                                {obj.project_id,before_sha, after_sha, char(model), ...
                                block_path, node_type, block_type, ...
                               is_deleted, is_modified, is_added, is_renamed }); 
               
            end
            
            output_bol= 1;
        end