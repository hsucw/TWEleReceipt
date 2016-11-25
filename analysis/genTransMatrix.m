function res = genTransMatrix( x, y)
    if x > y
        m = y;
        n = x;
    else
        m = x;
        n = y;
    end

    total = n/m;
    res = zeros(m,n);
    unit = 1;

    j=1;
    last_value = 0;
    for i = 1:m
        cur_value = 0;
       
        res(i, j) = unit-last_value;
        cur_value += unit-last_value;
        j+=1;

        while cur_value < total
            if unit > total-cur_value
                last_value = str2num(rats(total-cur_value));
                res(i,j) = last_value;
                break;
            else
                res(i,j) = unit;
                last_value = 0;
                cur_value +=unit;
            end
            j+=1;

            if(j>n)
                break;
            end
        end
    end
    if x > y 
        res = res';
    end

    %if size(res,1) != x || size(res,2) != y
    %    disp("error");
    %    disp(res);
    %else
    %    disp(size(res));
    %end

    return;
    %disp((res));
end
