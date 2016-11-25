function plotDailyDist( X, y, Z, symbol, color)

X = (1:1000)';
y = ones(1000, 1);
Z = rand(1000, 1).*100;
property = '';

stem3( X, y, Z) 


end
