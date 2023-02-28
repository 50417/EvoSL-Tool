function conn = connect_db_and_create_table(obj,db,table_name)
    if ~isfile(db)
        conn = sqlite(db,'create');
    else
        conn = sqlite(db,'connect');
    end
    cols = strcat(obj.colnames(1) ," ",obj.coltypes(1)) ;
    for i=2:length(obj.colnames)
        cols = strcat(cols, ... 
            ',', ... 
            obj.colnames(i), " ",obj.coltypes(i) ) ;
    end
   create_metric_table = strcat("CREATE TABLE IF NOT EXISTS ", table_name, ...
    '( ID INTEGER primary key autoincrement ,', cols ,')' );
     % ', CONSTRAINT UPair  UNIQUE(Before_Project_SHA, AFTER_Project_SHA,Model,Block_Path) )');
    exec(conn,char(create_metric_table));

end
