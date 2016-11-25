function res = genFrequencyRatio(fname, range, max_range)

    data = load(fname);
    data = floor(data./range);
    
    total_num = size(data, 1);

    min(data);
    max(data);
    interval = ceil(max_range/range);
    

    res = zeros(interval, 1);

    for i=1:interval
        res(i,:)=size( find(data <= i-1), 1)/total_num;
    end

    freq_fname=strrep(fname, ".txt", "_frq.csv");
    csvwrite(freq_fname, res);


    return;
end 
