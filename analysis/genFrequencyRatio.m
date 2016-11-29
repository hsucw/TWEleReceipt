function res = genFrequencyRatio(data, unit, num_unit)

    data = floor(data./unit);
    
    total_num = size(data, 1);

    res = zeros(num_unit, 1);

    for i=1:num_unit
        res(i,:)=size( find(data <= i-1), 1)/total_num;
    end

    #freq_fname=strrep(fname, ".txt", "_frq.csv");
    #csvwrite(freq_fname, res);


    return;
end 
