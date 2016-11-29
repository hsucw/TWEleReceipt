function analyze(norl)

    X = zeros(norl, 4);

    X(:,1)=genNormalizedDaily("20160911.txt", norl);
    X(:,2)=genNormalizedDaily("20160912.txt", norl);
    X(:,3)=genNormalizedDaily("20160913.txt", norl);
    X(:,4)=genNormalizedDaily("20160914.txt", norl);

    csvwrite("out.csv", X);

    

end
