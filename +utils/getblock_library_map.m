function [blocktype_lib_map] = getblock_library_map(varargin)
%UNTITLED6 Creates the hashmap of builtin Block type and their simulink library paths 
%   key is block type (string)
% value is cell array where element is simulink library path
    blocktype_lib_map = containers.Map();
    load_system('simulink');
    %x = find_system('simulink', 'LookUnderMasks', 'all', 'Type', 'Block');
    %get_param(x,'BlockType')
    simulinkLibraryPaths = find_system('simulink', 'Type', 'Block');
    
    %Replace return key with space. char(10) is return key 
    simulinkLibraryPaths = cellfun(@(x) strrep(x,newline, ' '),simulinkLibraryPaths,'UniformOutput',false);
    
    %Remove redundant library and non-block library
    simulinkLibraryPaths = utils.remove_strmatching_cellarr(simulinkLibraryPaths,'Commonly Used Blocks',1);
    simulinkLibraryPaths = utils.remove_strmatching_cellarr(simulinkLibraryPaths,'Quick Insert',1);
    simulinkLibraryPaths = utils.remove_strmatching_cellarr(simulinkLibraryPaths,'/',1);
    pat = regexpPattern("Additional Math: Increment - Decrement$"); % Ends with;
    simulinkLibraryPaths = utils.remove_strmatching_cellarr(simulinkLibraryPaths,pat,1);
    pat = regexpPattern("Additional Discrete$"); % Ends with;
    simulinkLibraryPaths = utils.remove_strmatching_cellarr(simulinkLibraryPaths,pat,1);
    pat = regexpPattern("Examples$"); % Ends with;
    simulinkLibraryPaths = utils.remove_strmatching_cellarr(simulinkLibraryPaths,pat,1);
    
    %simulinkLibraryBlockTypes = get_param(simulinkLibraryPaths, 'BlockType');
    %ReferenceBlock Parameter of simulinkLibraryPath blocks is nil . So
    %here we place all the blocks in a dummy model and extract the block
    %type
    tmp_mdl = "tmp";
    load_system(new_system(tmp_mdl));
    for n = 1 : numel(simulinkLibraryPaths)
        lib_with_blocktype = simulinkLibraryPaths{n};
        add_block(lib_with_blocktype,tmp_mdl+"/"+n);
    end
    save_system(tmp_mdl);
    
    for n = 1 : numel(simulinkLibraryPaths)
        lib_with_blocktype = simulinkLibraryPaths{n};
        blocktype = utils.get_block_type(tmp_mdl+"/"+n); % return cell array
     

        %[lib,blocktype] = utils.split_two_last_delim( lib_with_blocktype,"/");
        %get_param(__,'blocktype') returns block type with no spaces and no dashes. So
        %making the key as blocktype with no spaces.  
        %blocktype = strrep(blocktype,' ','');
        %blocktype = strrep(blocktype,'-','');
        %if contains(blocktype,',')
            %Second-order Integrator Blocktype has the library path as
            %Integrator, second order.
            %[secondpart, firstpart] = utils.split_two_last_delim( blocktype,',');
            %blocktype = [firstpart secondpart];
            
        %end
        if(~isKey(blocktype_lib_map,blocktype))
            blocktype_lib_map(blocktype) = {};
        else
            %% Overriding the library paths for 
            %In Bus Element : 'simulink/Ports & Subsystems/In Bus Element'
            %In1 :  simulink/Ports & Subsystems/In1
            %Out : Bus Element simulink/Ports & Subsystems/Out Bus Element
            %Out1 : simulink/Ports & Subsystems/Out1
            %Vector Concatenate : simulink/Math Operations/Vector Concatenate
            if(nargin>0)
                loggerObj = varargin{1};
                
                loggerObj.info("Processing Blocktype: %s",blocktype);
                tmp = blocktype_lib_map(blocktype);
                loggerObj.info("Current Map contains : %s",tmp{1});
                loggerObj.info("Potentially Replacing or adding it with : %s",lib_with_blocktype);
            else
                disp("==========================");
                disp(blocktype);
                disp(blocktype_lib_map(blocktype));
                disp(lib_with_blocktype);
                disp("==========================");
                
            end    
            %if contains(lib_with_blocktype,"Sources") || contains(lib_with_blocktype,"Sinks") || contains(lib_with_blocktype,"Signal Routing")
             %   disp(blocktype);
             %   disp(blocktype_lib_map(blocktype));
             %   disp(lib_with_blocktype);
          
                %blocktype_lib_map(blocktype) = {};
            %end
        
            
        end
        val =  blocktype_lib_map(blocktype);
        val{end+1} = lib_with_blocktype;
        blocktype_lib_map(blocktype) = val;

    end
    close_system('simulink');
    close_system(tmp_mdl);
    delete(tmp_mdl+".slx");
    %%  Check if any block type has more than one simulink library paths
    %{
    for k = keys(blocktype_lib_map)
        if length(blocktype_lib_map(k{1})) > 1
        disp(k)
        end
    end
    %}
end