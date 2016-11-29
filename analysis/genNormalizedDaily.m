function res = genNormalizedDaily(data, target)
    #data = load(fname);

    x = target;
    y = size(data,1);

    disp(target)
    disp(x)

    trans_matx = genTransMatrix(x,y);
    res = trans_matx*data./(y/x);
    #res = trans_matx*data

    #freq_fname=strrep(fname, ".txt", "_nor.csv");
    #csvwrite("out.csv", res);
    
    return; 
end

