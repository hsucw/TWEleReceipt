function res = genNormalizedDaily(fname, target)
    data = load(fname);

    x = target;
    y = size(data,1);

    trans_matx = genTransMatrix(x,y);
    res = trans_matx*data./(y/x);
    
    freq_fname=strrep(fname, ".txt", "_nor.csv");
    csvwrite("out.csv", res);
    
    return; 
end
