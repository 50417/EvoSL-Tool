function conn = connect_db(db)
    if ~isfile(db)
        error('Database doesnot exists');
    else
        conn = sqlite(db,'connect');
    end
end