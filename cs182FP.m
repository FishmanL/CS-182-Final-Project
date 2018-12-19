% [filename, path] = uigetfile('*.csv');
path = '/Users/dschoenberg/Documents/PyCharm Projects/cs182-f18-psets-daysch/CS-182-Final-Project/dominiate/weights/';
bot = 'Bot10';
filename = ['weights' bot '.csv'];

%% weights vs iteration for Bot
%% Read data
data = csvread([path filename]);
data = abs(data);
%% Buy graphs
order1 = [{'curse'}; {'estate'}; {'duchy'}; {'province'}; {'copper'}; {'silver'}; {'gold'}; ...
          {'village'}; {'cellar'}; {'smithy'}; {'festival'}; {'market'}; {'laboratory'}; ...
          {'chapel'}; {'warehouse'}; {'council room'}; {'militia'}; {'moat'}];
order2 = order1;
order1 = strcat(order1, ' in game');
order2 = strcat(order2, ' in deck');
order3 = [{'buys'}; {'hand value'}];
order_total = [order1; order2; order3];

buys = data(1:4:end,1:38);
indices = 1:size(buys,2);
order_used = order_total(indices(~all(buys<1/38)));
buys = buys(:, indices(~all(abs(buys)<1/38)));


figure()
plot(1:length(buys), buys)
title(['buy weights greater than average vs iteration for ' bot])
xlabel('iteration')
ylabel('weight')
legend(order_used)

%% trash graph
order1 = [{'curse'}; {'estate'}; {'duchy'}; {'province'}; {'copper'}; {'silver'}; {'gold'}; ...
          {'village'}; {'cellar'}; {'smithy'}; {'festival'}; {'market'}; {'laboratory'}; ...
          {'chapel'}; {'warehouse'}; {'council room'}; {'militia'}; {'moat'}];
order2 = order1;
order3 = order1;
order1 = strcat(order1, ' in game');
order2 = strcat(order2, ' in deck');
order3 = strcat(order3, ' in hand');
order_total = [order1; order2; order3];

trashes = data(2:4:end, :);
l = size(trashes,2);
indices = 1:l;
order_used = order_total(indices(~all(abs(trashes)<0.1)));
trashes = trashes(:, indices(~all(abs(trashes)<0.1)));


figure()
plot(1:length(trashes), trashes)
title(['trash weights greater than 0.1 vs iteration for ' bot])
xlabel('iteration')
ylabel('weight')
legend(order_used)


%% discard graph
order1 = [{'curse'}; {'estate'}; {'duchy'}; {'province'}; {'copper'}; {'silver'}; {'gold'}; ...
          {'village'}; {'cellar'}; {'smithy'}; {'festival'}; {'market'}; {'laboratory'}; ...
          {'chapel'}; {'warehouse'}; {'council room'}; {'militia'}; {'moat'}];
order2 = [{'actions'};{'buys'};{'hand value'}];
order1 = strcat(order1, ' in hand');
order_total = [order1; order2; order3];

discards = data(3:4:end,1:21);
l = size(discards,2);
indices = 1:l;
order_used = order_total(indices(~all(abs(discards)<1/l)));
discards = discards(:, indices(~all(abs(discards)<1/l)));

figure()
plot(1:length(discards), discards)
title(['discard weights greater than average vs iteration for ' bot])
xlabel('iteration')
ylabel('weight')
legend(order_used)

%% play graph
order1 = [{'curse'}; {'estate'}; {'duchy'}; {'province'}; {'copper'}; {'silver'}; {'gold'}; ...
          {'village'}; {'cellar'}; {'smithy'}; {'festival'}; {'market'}; {'laboratory'}; ...
          {'chapel'}; {'warehouse'}; {'council room'}; {'militia'}; {'moat'}];
order2 = [{'actions'};{'buys'};{'hand value'}];
order1 = strcat(order1, ' in hand');
order_total = [order1; order2];

plays = data(4:4:end,1:21);
l = size(plays,2);
indices = 1:l;
order_used = order_total(indices(~all(abs(plays)<1/l)));
plays = plays(:, indices(~all(abs(plays)<1/l)));

figure()
plot(1:length(plays), plays)
title(['plays weights greater than average vs iteration for ' bot])
xlabel('iteration')
ylabel('weight')
legend(order_used)
