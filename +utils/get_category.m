function [category] = get_category(blk_type,lib_or_blk_path,constructor_flag,varargin)
    %blk_type
    %lib_or_blk_path = simulink library path (true) or block_path(false)
    % varargin{1} = category block set map
    %GET_CATEGORY Summary of this function goes here
    
    if constructor_flag
        lib_split  = split(lib_or_blk_path,'/');
        potential_category = lib_split{2};
        if contains(potential_category,'Additional')
            potential_category = lib_split{3};
        end
        
        switch potential_category
            case 'Sources'
                category = potential_category;
                if strcmp(blk_type,'Inport') ||  strcmp(blk_type,'FromFile') ||  strcmp(blk_type,'FromWorkspace') || strcmp(blk_type,'FromSpreadsheet')
                    category = 'Interface';
                end
            case 'Sinks'
                category = potential_category;
                if strcmp(blk_type,'Outport') || strcmp(blk_type,'ToFile') ||  strcmp(blk_type,'ToWorkspace') || strcmp(blk_type,'FromSpreadsheet')
                    category = 'Interface';
                end
            case 'Math Operations'
                category = 'Math';
                if strcmp(blk_type,'Assignment') || strcmp(blk_type,'Concatenate') 
                    category = 'Signal Routing';
                end
            case 'Continuous'
                category = 'Continuous';
                if strcmp(blk_type,'Integrator')
                    category = 'Discrete';
                end
            case 'Model-Wide Utilities'
                 category = potential_category;
                 if strcmp(blk_type,'DocBlock') || strcmp(blk_type,'Model Info')
                    category = 'Documentation';
                 end
            case 'Ports & Subsystems'
                 if strcmp(blk_type,'SubSystem') || strcmp(blk_type,'ModelReference')
                    category = 'Structural';
                 elseif contains(blk_type,'Port') 
                    category = 'Trigger';
                 elseif  strcmp(blk_type,'Inport') ||  strcmp(blk_type,'Outport')
                      category = 'Interface';
                 else
                     category = 'Conditional';
              
                 end
            case 'Conditional'
                category = potential_category;
                if strcmp(blk_type,'Function-Call-Generator')
                    category = 'Trigger';
                end
            case 'Signal Routing'
                category = potential_category;
                if strcmp(blk_type,'Switch') || strcmp(blk_type,'ManualSwitch') || strcmp(blk_type,'MultiPortSwitch')
                    category = 'Conditional';
                end
            case 'User-Defined Functions'
                category = 'Custom';
                if strcmp(blk_type,'SubSystem') 
                    category = 'Structural';
              
                end
            case 'Matrix Operations'
                category = potential_category; 
                 if strcmp(blk_type,'SubSystem') 
                    category = 'Structural';
              
                 end
            case 'Lookup Tables'
                category = 'Math';
            case 'Discontinuities'
                category = potential_category;
                if strcmp(blk_type,'DeadZone') || strcmp(blk_type,'RateLimiter') || strcmp(blk_type,'Saturate')
                    category = 'Math';
              
                 end


                
            case 'Logic and Bit Operations'
                category = 'Logic';
            case 'Additional Discrete'
                category = 'Discrete';
            case 'Additional Math: Increment - Decrement'
                category = 'Math';
            otherwise %Continuous, Discontinuities, Signal Attributes,Messages & Events
                      %Lookup Tables,Discrete,String,Model Verification
               category = potential_category;
        end
    else
        category = 'Others';
        if nargin < 1
            error('Not all argument passed');
        else
             category_block_set_map = varargin{1};
        end
        k = keys(category_block_set_map); 
        local_global_blk_type = java.util.HashSet;
        local_global_blk_type.add('DataStoreRead');
        
        local_global_blk_type.add('DataStoreWrite');
        
        local_global_blk_type.add('Inport');
        local_global_blk_type.add('Outport');
        for i = 1:length(k)
            values_set = category_block_set_map(k{i});
            if values_set.contains(blk_type)
                category = k{i};
                if strcmp(category,'Interface') || strcmp(category,'Signal Routing')
                    if local_global_blk_type.contains(blk_type)
                    
                        if count(lib_or_blk_path,'/') == 1
                            category = 'Interface';
                        elseif count(lib_or_blk_path,'/') > 1
                            category = 'Signal Routing';
                        else
                            error('Potential Error');
                        end
                    end
                end
                if strcmp(category,'Structural') && (endsWith(lib_or_blk_path,'DocBlock') || endsWith(lib_or_blk_path,'Model Info'))
                    category = 'Documentation';
                end
                 if strcmp(category,'Structural') && strcmp(lib_or_blk_path,'Signal Builder') 
                    category = 'Sources';
                end
            end
        end
        if strcmp(blk_type,'ForIterator')
           category = 'Trigger';
        elseif strcmp(blk_type,'DataTypePropagation')
            category = 'Signal Attributes';
        end
    end
end



