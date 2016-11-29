filename = 'daily_dist.csv';
M = csvread(filename);

second = M(M(:,1)==18221188,:);
thirdteen = M(M(:,1)==42078697,:);

second_day = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 50, 64, 65, 66,...
    67, 68, 71, 72, 73, 74, -33, -31, -30];
thirdteen_day = [3, 4, 23, 28, 34, 35, 45, 54, 55, -2, -23, -21, -17, -5];

pick_third = [54, 55];

day1 = thirdteen(thirdteen(:,2)==54,[2,4]);
day1(:,2)=log(day1(:,2));

day2 = thirdteen(thirdteen(:,2)==55,[2,4]);
day2(:,2)=log(day2(:,2));


%stem3(thirdteen(:,2), thirdteen(:,3), log(thirdteen(:,4)), '--*m');

%plot(thirdteen(thirdteen(:,3), log(thirdteen(:,4)))
