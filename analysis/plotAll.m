

data = csvread('example.csv');

size(data,1);
size(data,2);

m = size(data,1);
%pick = (ceil(rand(1000,1).*m)+1);
pick = (2:m);
%pick = (11000:12000);
px = data(pick, 1);
py = data(pick, 3);
pz = data(pick, 2);
ptid = data(pick, 4);

colors = zeros(size(ptid,1),3);
coms = unique(ptid);
tn = size(coms,1) + 1;
palette = hsv(tn);

for i = 1:size(ptid,1)
    colors(i,:) = palette( coms == ptid(i), :);
end


x_min = min(px)
x_max = max(px)
px = px - x_min;
y_min = min(py)
y_max = max(py)
z_min = min(pz)
z_max = max(pz)


%axis([0 x_max-x_min y_min y_max z_min z_max]);
axis auto;
scatter3( px, py, pz , [] , colors);

