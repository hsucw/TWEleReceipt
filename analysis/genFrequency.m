function res = genFrequency(fname, range)
    data = load(fname);
    data = floor(data./range);
    
    min(data);
    max(data);
    interval = max(data)-min(data);

    res = zeros(interval, 1);

    for i=1:interval+1
        res(i,:)=size( find(data == i-1), 1);
    end

    freq_fname=strrep(fname, ".txt", ".csv");
    csvwrite(freq_fname, res);


    return;
end 

